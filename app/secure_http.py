"""Pinned HTTPS transport for third-party HTTP APIs and remote media."""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager
from urllib3.connection import HTTPSConnection
from urllib3.connectionpool import HTTPSConnectionPool
from urllib3.poolmanager import PoolKey, _default_key_normalizer

_REDIRECTS = {301, 302, 303, 307, 308}


def resolve_public_ips(host: str) -> list[str]:
    """Resolve a host once and reject the whole answer set if any IP is non-public."""
    try:
        literal = ipaddress.ip_address(host)
        addresses = [literal]
    except ValueError:
        try:
            answers = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
            addresses = [ipaddress.ip_address(item[4][0]) for item in answers]
        except (OSError, ValueError, IndexError) as exc:
            raise ValueError("HTTPS host could not be safely resolved") from exc
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("HTTPS host resolves to a non-public IP address")
    return list(dict.fromkeys(str(address) for address in addresses))


def validate_public_https_url(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid URL port") from exc
    if (parsed.scheme.lower() != "https" or not host
            or host == "localhost" or host.endswith((".localhost", ".local", ".internal"))
            or parsed.username is not None or parsed.password is not None
            or port not in (None, 443)):
        raise ValueError("Only public HTTPS URLs on the standard port are allowed")
    resolve_public_ips(host)
    return url


class PinnedHTTPSConnection(HTTPSConnection):
    """Connect to a validated IP while retaining the hostname for TLS SNI/checks."""
    def __init__(self, *args, pinned_ip: str, **kwargs):
        self.pinned_ip = pinned_ip
        super().__init__(*args, **kwargs)

    def _new_conn(self):
        try:
            return socket.create_connection((self.pinned_ip, self.port), self.timeout, self.source_address)
        except OSError as exc:
            raise OSError(f"Pinned HTTPS connection failed: {exc}") from exc


class PinnedHTTPSConnectionPool(HTTPSConnectionPool):
    ConnectionCls = PinnedHTTPSConnection


class _PinnedAdapter(HTTPAdapter):
    def __init__(self, pinned_ip: str):
        self.pinned_ip = pinned_ip
        super().__init__(max_retries=0)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        manager = PoolManager(
            num_pools=connections, maxsize=maxsize, block=block,
            **pool_kwargs, pinned_ip=self.pinned_ip,
        )
        manager.pool_classes_by_scheme["https"] = PinnedHTTPSConnectionPool
        manager.key_fn_by_scheme["https"] = lambda context: _default_key_normalizer(
            PoolKey, {key: value for key, value in context.items() if key != "pinned_ip"}
        )
        self.poolmanager = manager


def _single_request(method: str, url: str, *, timeout, headers, params, data, json_body, stream):
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    pinned_ip = resolve_public_ips(host)[0]
    session = requests.Session()
    session.trust_env = False  # Never inherit ambient HTTP(S)_PROXY settings.
    session.mount("https://", _PinnedAdapter(pinned_ip))
    try:
        response = session.request(
            method, url, headers=headers, params=params, data=data, json=json_body,
            timeout=timeout, stream=stream, allow_redirects=False,
        )
    except Exception:
        session.close()
        raise
    if stream:
        original_close = response.close
        def close_with_session():
            try:
                original_close()
            finally:
                session.close()
        response.close = close_with_session
    else:
        # Consume before closing the one-request session; response.content remains cached.
        _ = response.content
        session.close()
    return response


def request_public_https(method: str, url: str, *, timeout=30, headers=None,
                         params=None, data=None, json=None, stream=False,
                         max_redirects: int = 0) -> requests.Response:
    """Send a public HTTPS request through per-hop DNS validation and IP pinning.

    Redirects are disabled by default. If explicitly enabled, every hop is revalidated;
    cross-origin redirects never receive Authorization, Cookie or proxy credentials.
    """
    method = method.upper()
    current_url = url
    current_headers = dict(headers or {})
    current_data, current_json, current_params = data, json, params
    original_host = (urlparse(url).hostname or "").lower().rstrip(".")
    for hop in range(max_redirects + 1):
        validate_public_https_url(current_url)
        response = _single_request(
            method, current_url, timeout=timeout, headers=current_headers,
            params=current_params, data=current_data, json_body=current_json, stream=stream,
        )
        current_params = None
        if response.status_code not in _REDIRECTS or max_redirects == 0:
            # Some APIs (notably YouTube resumable uploads) use 308 as an application
            # status. With redirects disabled, preserve the provider's response verbatim.
            return response
        location = response.headers.get("Location")
        if hop >= max_redirects or not location:
            response.close()
            if not location:
                raise requests.HTTPError("HTTPS redirect omitted its Location header")
            raise requests.TooManyRedirects("HTTPS redirect limit exceeded")
        next_url = urljoin(current_url, location)
        validate_public_https_url(next_url)
        next_host = (urlparse(next_url).hostname or "").lower().rstrip(".")
        if next_host != original_host:
            current_headers = {
                key: value for key, value in current_headers.items()
                if key.lower() not in {"authorization", "cookie", "proxy-authorization"}
            }
        if response.status_code == 303 or (response.status_code in (301, 302) and method not in ("GET", "HEAD")):
            method, current_data, current_json = "GET", None, None
            current_headers = {key: value for key, value in current_headers.items()
                               if key.lower() not in {"content-length", "content-type"}}
        response.close()
        current_url = next_url
    raise requests.TooManyRedirects("HTTPS redirect limit exceeded")


def safe_stream_get(url: str, *, timeout: int, max_redirects: int = 5, headers=None):
    return request_public_https("GET", url, timeout=timeout, headers=headers,
                                stream=True, max_redirects=max_redirects)
