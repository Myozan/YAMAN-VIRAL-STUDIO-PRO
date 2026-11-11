from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from fastapi import HTTPException

from app import main


@pytest.mark.parametrize("url", [
    "http://youtube.com/watch?v=abc",
    "https://youtube.com:8443/watch?v=abc",
    "https://user:pass@youtube.com/watch?v=abc",
    "https://127.0.0.1/watch?v=abc",
    "https://localhost/watch?v=abc",
    "https://youtube.com.evil.example/watch?v=abc",
    "file:///etc/passwd",
    "javascript:alert(1)",
])
def test_youtube_url_rejects_noncanonical_or_local_targets(url):
    with pytest.raises(ValueError):
        main.validate_youtube_url(url)


@pytest.mark.parametrize("url", [
    "https://youtube.com/watch?v=abc",
    "https://www.youtube.com/shorts/abc",
    "https://youtu.be/abc",
    "https://m.youtube.com/watch?v=abc",
])
def test_youtube_url_accepts_supported_https_hosts(url):
    main.validate_youtube_url(url)


@pytest.fixture
def oauth_vault(tmp_path, monkeypatch):
    key = Fernet.generate_key().decode("ascii")
    monkeypatch.setenv("YAMAN_TOKEN_ENCRYPTION_KEY", key)
    monkeypatch.setattr(main, "OAUTH_TOKEN_FILE", tmp_path / "oauth_tokens.enc")
    monkeypatch.setattr(main, "OAUTH_KEY_FILE", tmp_path / ".oauth.key")
    return key, tmp_path / "oauth_tokens.enc"


def test_oauth_vault_encrypts_and_round_trips_secrets(oauth_vault):
    _, vault = oauth_vault
    payload = {"youtube": {"access_token": "secret-access-token", "refresh_token": "secret-refresh-token"}}
    main.save_oauth_tokens(payload)

    encrypted = vault.read_bytes()
    assert b"secret-access-token" not in encrypted
    assert b"secret-refresh-token" not in encrypted
    assert main.oauth_token_data() == payload


def test_oauth_vault_fails_closed_with_wrong_key(oauth_vault, monkeypatch):
    _, vault = oauth_vault
    main.save_oauth_tokens({"youtube": {"access_token": "must-not-leak"}})
    monkeypatch.setenv("YAMAN_TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode("ascii"))

    with pytest.raises(RuntimeError, match="cannot be decrypted"):
        main.oauth_token_data()


def test_oauth_vault_rejects_malformed_encryption_key(tmp_path, monkeypatch):
    monkeypatch.setenv("YAMAN_TOKEN_ENCRYPTION_KEY", "not-a-valid-fernet-key")
    monkeypatch.setattr(main, "OAUTH_KEY_FILE", tmp_path / ".oauth.key")
    with pytest.raises(Exception):
        main.oauth_fernet()


def test_auto_editor_rejects_parent_directory_traversal(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.mp4"
    outside.write_bytes(b"not-a-real-video")
    monkeypatch.setattr(main, "WORK", workspace)
    monkeypatch.setattr(main.shutil, "which", lambda _name: "auto-editor")

    with pytest.raises(HTTPException) as error:
        main.auto_editor_silence_remove(main.AutoEditorRequest(file="../outside.mp4"))
    assert error.value.status_code == 400


def test_auto_editor_rejects_absolute_path_outside_workspace(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.mp4"
    outside.write_bytes(b"not-a-real-video")
    monkeypatch.setattr(main, "WORK", workspace)
    monkeypatch.setattr(main.shutil, "which", lambda _name: "auto-editor")

    with pytest.raises(HTTPException) as error:
        main.auto_editor_silence_remove(main.AutoEditorRequest(file=str(outside)))
    assert error.value.status_code == 400


def test_auto_editor_rejects_symlink_escape(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.mp4"
    outside.write_bytes(b"not-a-real-video")
    link = workspace / "escape.mp4"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is not permitted in this Windows environment")
    monkeypatch.setattr(main, "WORK", workspace)
    monkeypatch.setattr(main.shutil, "which", lambda _name: "auto-editor")

    with pytest.raises(HTTPException) as error:
        main.auto_editor_silence_remove(main.AutoEditorRequest(file="escape.mp4"))
    assert error.value.status_code == 400


def test_saved_job_loader_ignores_workspace_symlink_escape(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "job.json").write_text('{"video":"x.mp4","clips":[],"segments":[]}', encoding="utf-8")
    try:
        (workspace / "linked-job").symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Directory symlink creation is not permitted in this Windows environment")
    monkeypatch.setattr(main, "WORK", workspace)
    main.jobs.clear()

    main.load_saved_jobs()

    assert "linked-job" not in main.jobs
import pytest

from app import visual_factory


def _dns_result(address):
    return [(2, 1, 6, "", (address, 443))]


@pytest.mark.parametrize("url", [
    "http://cdn.example/video.mp4",
    "https://127.0.0.1/video.mp4",
    "https://10.0.0.8/video.mp4",
    "https://169.254.169.254/latest/meta-data",
    "https://localhost/video.mp4",
    "https://user:pass@cdn.example/video.mp4",
    "https://cdn.example:9443/video.mp4",
])
def test_remote_media_url_rejects_private_or_ambiguous_targets(url, monkeypatch):
    monkeypatch.setattr(visual_factory.socket, "getaddrinfo", lambda *a, **k: _dns_result("93.184.216.34"))
    with pytest.raises(ValueError):
        visual_factory.validate_public_https_url(url)


def test_remote_media_url_rejects_hostname_resolving_to_private_ip(monkeypatch):
    monkeypatch.setattr(visual_factory.socket, "getaddrinfo", lambda *a, **k: _dns_result("192.168.1.20"))
    with pytest.raises(ValueError, match="non-public"):
        visual_factory.validate_public_https_url("https://cdn.example/video.mp4")


def test_remote_media_url_rejects_mixed_public_and_private_dns_answers(monkeypatch):
    def resolve(*_args, **_kwargs):
        return _dns_result("93.184.216.34") + _dns_result("10.0.0.5")
    monkeypatch.setattr(visual_factory.socket, "getaddrinfo", resolve)
    with pytest.raises(ValueError, match="non-public"):
        visual_factory.validate_public_https_url("https://cdn.example/video.mp4")


def test_remote_media_url_accepts_public_https_destination(monkeypatch):
    monkeypatch.setattr(visual_factory.socket, "getaddrinfo", lambda *a, **k: _dns_result("93.184.216.34"))
    assert visual_factory.validate_public_https_url("https://cdn.example/video.mp4") == "https://cdn.example/video.mp4"


def test_remote_media_redirect_to_private_ip_is_blocked(monkeypatch):
    class Redirect:
        status_code = 302
        headers = {"Location": "http://127.0.0.1/admin"}
        def close(self):
            pass

    calls = []
    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return Redirect()

    monkeypatch.setattr(visual_factory, "_pinned_https_get", lambda url, ip, **kwargs: fake_get(url, allow_redirects=False, **kwargs))
    monkeypatch.setattr(visual_factory.socket, "getaddrinfo", lambda *a, **k: _dns_result("93.184.216.34"))
    with pytest.raises(ValueError):
        visual_factory.safe_stream_get("https://cdn.example/start", timeout=3)
    assert len(calls) == 1
    assert calls[0][1]["allow_redirects"] is False


def test_remote_media_redirect_target_is_revalidated(monkeypatch):
    class Redirect:
        status_code = 302
        headers = {"Location": "https://cdn2.example/final.mp4"}
        def close(self):
            pass

    class Success:
        status_code = 200
        headers = {}
    calls = []
    def fake_get(url, **kwargs):
        calls.append(url)
        return Redirect() if len(calls) == 1 else Success()

    monkeypatch.setattr(visual_factory, "_pinned_https_get", lambda url, ip, **kwargs: fake_get(url, allow_redirects=False, **kwargs))
    monkeypatch.setattr(visual_factory.socket, "getaddrinfo", lambda *a, **k: _dns_result("93.184.216.34"))
    response = visual_factory.safe_stream_get("https://cdn.example/start", timeout=3)
    assert isinstance(response, Success)
    assert calls == ["https://cdn.example/start", "https://cdn2.example/final.mp4"]


def test_remote_media_redirect_limit_is_enforced(monkeypatch):
    class Redirect:
        status_code = 302
        headers = {"Location": "/again"}
        def close(self):
            pass
    monkeypatch.setattr(visual_factory, "_pinned_https_get", lambda *a, **k: Redirect())
    monkeypatch.setattr(visual_factory.socket, "getaddrinfo", lambda *a, **k: _dns_result("93.184.216.34"))
    with pytest.raises(visual_factory.VisualProviderError, match="redirect limit"):
        visual_factory.safe_stream_get("https://cdn.example/start", timeout=3, max_redirects=2)


def test_oauth_vault_key_rotation_reencrypts_all_vaults_and_keeps_backups(tmp_path, monkeypatch):
    old_key = Fernet.generate_key().decode("ascii")
    new_key = Fernet.generate_key().decode("ascii")
    monkeypatch.setenv("YAMAN_TOKEN_ENCRYPTION_KEY", old_key)
    monkeypatch.setattr(main, "OAUTH_TOKEN_FILE", tmp_path / "oauth_tokens.enc")
    monkeypatch.setattr(main, "OAUTH_APP_FILE", tmp_path / "oauth_apps.enc")
    monkeypatch.setattr(main, "VISUAL_PROVIDER_FILE", tmp_path / "visual_providers.enc")
    monkeypatch.setattr(main, "OAUTH_KEY_FILE", tmp_path / ".oauth.key")
    main.save_oauth_tokens({"youtube": {"refresh_token": "refresh-secret"}})
    main.OAUTH_APP_FILE.write_bytes(Fernet(old_key.encode()).encrypt(b'{"youtube":{"client_secret":"app-secret"}}'))
    main.VISUAL_PROVIDER_FILE.write_bytes(Fernet(old_key.encode()).encrypt(b'{"runway_api_key":"visual-secret"}'))
    result = main.rotate_oauth_vault_key(new_key)
    assert len(result["rotated_vaults"]) == 3
    assert len(result["backup_files"]) == 3
    assert main.oauth_token_data() == {"youtube": {"refresh_token": "refresh-secret"}}
    assert main.oauth_app_config()["youtube"]["client_secret"] == "app-secret"
    assert main.visual_provider_config()["runway_api_key"] == "visual-secret"
    assert all(".bak." in name for name in result["backup_files"])
    monkeypatch.setenv("YAMAN_TOKEN_ENCRYPTION_KEY", old_key)
    with pytest.raises(RuntimeError, match="cannot be decrypted"):
        main.oauth_token_data()


def test_oauth_key_rotation_rejects_bad_new_key_without_touching_vault(tmp_path, monkeypatch):
    key = Fernet.generate_key().decode("ascii")
    monkeypatch.setenv("YAMAN_TOKEN_ENCRYPTION_KEY", key)
    monkeypatch.setattr(main, "OAUTH_TOKEN_FILE", tmp_path / "oauth_tokens.enc")
    main.save_oauth_tokens({"youtube": {"refresh_token": "keep-me"}})
    before = main.OAUTH_TOKEN_FILE.read_bytes()
    with pytest.raises(ValueError, match="valid Fernet"):
        main.rotate_oauth_vault_key("invalid")
    assert main.OAUTH_TOKEN_FILE.read_bytes() == before


def test_pinned_https_connection_uses_validated_ip_but_keeps_tls_hostname(monkeypatch):
    calls = []
    sentinel = object()
    def connect(address, timeout, source_address):
        calls.append((address, timeout, source_address))
        return sentinel
    monkeypatch.setattr(visual_factory.socket, "create_connection", connect)
    connection = visual_factory._PinnedHTTPSConnection(
        host="cdn.example", port=443, pinned_ip="93.184.216.34", timeout=7,
    )
    assert connection._new_conn() is sentinel
    assert calls == [(('93.184.216.34', 443), 7, None)]
    assert connection.host == "cdn.example"  # urllib3 uses this for SNI/certificate matching.


def test_pinned_https_adapter_passes_ip_into_urllib3_pool(monkeypatch):
    from requests import Session
    class FakeResponse:
        status_code = 200
        headers = {}
        def close(self): pass
    captured = {}
    sentinel = object()
    monkeypatch.setattr(visual_factory.socket, "getaddrinfo", lambda *a, **k: _dns_result("93.184.216.34"))
    monkeypatch.setattr(visual_factory.socket, "create_connection", lambda address, *a, **k: sentinel)
    def fake_session_get(self, url, **kwargs):
        adapter = self.get_adapter(url)
        pool = adapter.poolmanager.connection_from_url(url)
        connection = pool._new_conn()
        captured.update(ip=connection.pinned_ip, host=connection.host, pool_ip=pool.conn_kw["pinned_ip"])
        return FakeResponse()
    monkeypatch.setattr(Session, "get", fake_session_get)
    response = visual_factory.safe_stream_get("https://cdn.example/media.mp4", timeout=4)
    assert response.status_code == 200
    assert captured == {"ip": "93.184.216.34", "host": "cdn.example", "pool_ip": "93.184.216.34"}
