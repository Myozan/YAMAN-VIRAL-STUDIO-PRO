"""AI visual and scene-based B-roll providers for YAMAN VIRAL STUDIO PRO."""
from __future__ import annotations
import time
import ipaddress
import socket
from pathlib import Path
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPSConnection
from urllib3.connectionpool import HTTPSConnectionPool
import requests

RUNWAY_BASE = "https://api.dev.runwayml.com/v1"
RUNWAY_VERSION = "2024-11-06"

def _resolve_public_ips(host: str) -> list[str]:
    try:
        literal = ipaddress.ip_address(host)
        addresses = [literal]
    except ValueError:
        try:
            answers = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
            addresses = [ipaddress.ip_address(item[4][0]) for item in answers]
        except (OSError, ValueError, IndexError) as exc:
            raise ValueError("URL host could not be safely resolved") from exc
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("URL host resolves to a non-public IP address")
    return [str(addresses[0])]


def validate_public_https_url(url: str) -> str:
    """Validate HTTPS URL and reject private, local and ambiguous destinations."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid URL port") from exc
    if (parsed.scheme.lower() != "https" or not host or host == "localhost"
            or host.endswith((".localhost", ".local", ".internal"))
            or parsed.username is not None or parsed.password is not None
            or port not in (None, 443)):
        raise ValueError("Only public HTTPS URLs on the standard port are allowed")
    _resolve_public_ips(host)
    return url


class _PinnedHTTPSConnection(HTTPSConnection):
    """Connect to a validated IP while keeping the original hostname for TLS/SNI."""
    def __init__(self, *args, pinned_ip: str, **kwargs):
        self.pinned_ip = pinned_ip
        super().__init__(*args, **kwargs)

    def _new_conn(self):
        try:
            return socket.create_connection((self.pinned_ip, self.port), self.timeout, self.source_address)
        except OSError as exc:
            raise OSError(f"Pinned HTTPS connection failed: {exc}") from exc


class _PinnedHTTPSConnectionPool(HTTPSConnectionPool):
    ConnectionCls = _PinnedHTTPSConnection


def _pinned_https_get(url: str, ip: str, *, timeout: int):
    from urllib3 import PoolManager
    from requests import Session

    class PinnedAdapter(HTTPAdapter):
        def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
            self.poolmanager = PoolManager(
                num_pools=connections, maxsize=maxsize, block=block,
                **pool_kwargs, pinned_ip=ip,
            )
            self.poolmanager.pool_classes_by_scheme["https"] = _PinnedHTTPSConnectionPool
            from urllib3.poolmanager import PoolKey, _default_key_normalizer
            self.poolmanager.key_fn_by_scheme["https"] = lambda context: _default_key_normalizer(
                PoolKey, {key: value for key, value in context.items() if key != "pinned_ip"}
            )

    session = Session()
    session.trust_env = False
    session.mount("https://", PinnedAdapter())
    response = session.get(url, stream=True, timeout=timeout, allow_redirects=False)
    original_close = response.close
    def close_with_session():
        try:
            original_close()
        finally:
            session.close()
    response.close = close_with_session
    return response


def safe_stream_get(url: str, *, timeout: int, max_redirects: int = 5):
    """GET public HTTPS media with IP pinning and per-hop redirect validation."""
    current = url
    for _ in range(max_redirects + 1):
        validate_public_https_url(current)
        host = (urlparse(current).hostname or "").lower().rstrip(".")
        pinned_ip = _resolve_public_ips(host)[0]
        response = _pinned_https_get(current, pinned_ip, timeout=timeout)
        if response.status_code not in {301, 302, 303, 307, 308}:
            return response
        location = response.headers.get("Location")
        response.close()
        if not location:
            raise VisualProviderError("Remote media redirect did not include a Location header")
        current = urljoin(current, location)
    raise VisualProviderError("Remote media URL exceeded the redirect limit")

class VisualProviderError(RuntimeError):
    pass

class RunwayClient:
    def __init__(self, api_key: str, timeout: int = 1800):
        if not api_key or len(api_key.strip()) < 12:
            raise VisualProviderError("Runway API anahtar─▒ Ayarlar > AI G├Ârsel Motorlar─▒ b├Âl├╝m├╝ne girilmelidir.")
        self.api_key = api_key.strip()
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "X-Runway-Version": RUNWAY_VERSION,
            "Content-Type": "application/json",
        })

    def _create(self, endpoint: str, payload: dict) -> str:
        response = self.session.post(f"{RUNWAY_BASE}/{endpoint}", json=payload, timeout=90)
        if response.status_code >= 400:
            detail = response.text[:1200]
            if response.status_code == 429:
                detail = "Runway kredi/rate limit s─▒n─▒r─▒ veya i┼ş kuyru─şu dolu. " + detail
            raise VisualProviderError(f"Runway {endpoint} ({response.status_code}): {detail}")
        task_id = response.json().get("id")
        if not task_id:
            raise VisualProviderError("Runway g├Ârev yan─▒t─▒nda task ID bulunamad─▒.")
        return str(task_id)

    def wait(self, task_id: str) -> list[str]:
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            response = self.session.get(f"{RUNWAY_BASE}/tasks/{task_id}", timeout=45)
            if response.status_code >= 400:
                raise VisualProviderError(f"Runway g├Ârev durumu okunamad─▒ ({response.status_code}): {response.text[:500]}")
            data = response.json()
            status = str(data.get("status", "")).upper()
            if status == "SUCCEEDED":
                outputs = data.get("output") or []
                if not outputs:
                    raise VisualProviderError("Runway g├Ârevi tamamland─▒ ancak ├ğ─▒kt─▒ URL'si d├Ânmedi.")
                return [str(x) for x in outputs if isinstance(x, str)]
            if status in {"FAILED", "CANCELED", "CANCELLED"}:
                raise VisualProviderError("Runway ├╝retim g├Ârevi ba┼şar─▒s─▒z: " + str(data.get("failure") or data.get("error") or status)[:800])
            time.sleep(4)
        raise VisualProviderError("Runway ├╝retimi zaman a┼ş─▒m─▒na u─şrad─▒. Runway g├Ârev kimli─şi: " + task_id)

    @staticmethod
    def download(url: str, target: Path, max_bytes: int = 300 * 1024 * 1024):
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise VisualProviderError("Runway ├ğ─▒kt─▒ adresi g├╝venli HTTPS olmal─▒d─▒r.")
        with safe_stream_get(url, timeout=180) as response:
            response.raise_for_status()
            size = 0
            with target.open("wb") as stream:
                for chunk in response.iter_content(1024 * 1024):
                    if not chunk:
                        continue
                    size += len(chunk)
                    if size > max_bytes:
                        raise VisualProviderError("├£retilen medya dosyas─▒ izin verilen boyutu a┼şt─▒.")
                    stream.write(chunk)
        if not target.is_file() or target.stat().st_size < 1024:
            raise VisualProviderError("├£retilen medya indirilemedi veya bo┼ş.")
        return target

    def generate_image(self, prompt: str, target: Path, ratio: str = "1080:1920") -> Path:
        task = self._create("text_to_image", {
            "model": "gen4_image_turbo",
            "promptText": prompt[:1000],
            "ratio": ratio,
        })
        return self.download(self.wait(task)[0], target, max_bytes=20 * 1024 * 1024)

    def animate_image(self, image: Path, prompt: str, target: Path, seconds: int = 5) -> Path:
        import base64
        if image.stat().st_size > 4 * 1024 * 1024:
            raise VisualProviderError("Sahne g├Ârseli 4 MB ├╝st├╝nde; Runway g├Ârsel giri┼ş s─▒n─▒r─▒na yakla┼şt─▒.")
        mime = "image/png" if image.suffix.lower() == ".png" else "image/jpeg"
        uri = f"data:{mime};base64," + base64.b64encode(image.read_bytes()).decode("ascii")
        task = self._create("image_to_video", {
            "model": "gen4.5",
            "promptImage": uri,
            "promptText": prompt[:1000],
            "ratio": "720:1280",
            "duration": max(2, min(10, int(seconds))),
        })
        return self.download(self.wait(task)[0], target)

    def generate_music(self, prompt: str, seconds: int, target: Path) -> Path:
        task = self._create("text_to_music", {
            "model": "eleven_music_v2_5",
            "promptText": prompt[:4000],
            "duration": max(3, min(600, int(seconds))),
            "instrumental": True,
        })
        return self.download(self.wait(task)[0], target, max_bytes=80 * 1024 * 1024)


def search_pexels_video(api_key: str, query: str, target: Path, orientation: str = "portrait") -> dict:
    if not api_key or len(api_key.strip()) < 12:
        raise VisualProviderError("Pexels API anahtar─▒ Ayarlar > AI G├Ârsel Motorlar─▒ b├Âl├╝m├╝ne girilmelidir.")
    response = requests.get(
        "https://api.pexels.com/v1/videos/search",
        headers={"Authorization": api_key.strip()},
        params={"query": query[:180], "orientation": orientation, "per_page": 8, "locale": "tr-TR"},
        timeout=45,
    )
    if response.status_code >= 400:
        raise VisualProviderError(f"Pexels API ({response.status_code}): {response.text[:600]}")
    videos = response.json().get("videos", [])
    if not videos:
        raise VisualProviderError(f"Pexels'ta '{query}' i├ğin uygun B-roll bulunamad─▒.")
    videos.sort(key=lambda x: (x.get("width", 0) < x.get("height", 1), x.get("duration", 0)), reverse=True)
    for video in videos:
        files = sorted(video.get("video_files", []), key=lambda f: (f.get("width", 0) <= 1920, f.get("width", 0)), reverse=True)
        for item in files:
            link = item.get("link", "")
            if not link.startswith("https://"):
                continue
            try:
                with safe_stream_get(link, timeout=120) as download:
                    download.raise_for_status()
                    size = 0
                    with target.open("wb") as stream:
                        for chunk in download.iter_content(1024 * 1024):
                            if not chunk: continue
                            size += len(chunk)
                            if size > 250 * 1024 * 1024: raise VisualProviderError("Pexels klibi 250 MB s─▒n─▒r─▒n─▒ a┼şt─▒.")
                            stream.write(chunk)
                if target.is_file() and target.stat().st_size > 1024:
                    return {"path": target, "source": "Pexels", "photographer": video.get("user", {}).get("name", ""),
                            "page": video.get("url", ""), "duration": video.get("duration", 0)}
            except Exception:
                target.unlink(missing_ok=True)
                continue
    raise VisualProviderError("Pexels arama sonu├ğlar─▒ndan video indirilemedi.")
