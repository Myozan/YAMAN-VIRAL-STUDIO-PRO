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

    monkeypatch.setattr(visual_factory.requests, "get", fake_get)
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

    monkeypatch.setattr(visual_factory.requests, "get", fake_get)
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
    monkeypatch.setattr(visual_factory.requests, "get", lambda *a, **k: Redirect())
    monkeypatch.setattr(visual_factory.socket, "getaddrinfo", lambda *a, **k: _dns_result("93.184.216.34"))
    with pytest.raises(visual_factory.VisualProviderError, match="redirect limit"):
        visual_factory.safe_stream_get("https://cdn.example/start", timeout=3, max_redirects=2)
