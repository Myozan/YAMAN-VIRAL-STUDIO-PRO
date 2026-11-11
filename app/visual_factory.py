"""AI visual and scene-based B-roll providers for YAMAN VIRAL STUDIO PRO."""
from __future__ import annotations
import time
from pathlib import Path
from urllib.parse import urlparse
import app.secure_http as secure_http
socket = secure_http.socket  # Backward-compatible test seam; implementation lives in secure_http.
from app.secure_http import (
    PinnedHTTPSConnection as _PinnedHTTPSConnection,
    PinnedHTTPSConnectionPool as _PinnedHTTPSConnectionPool,
    resolve_public_ips as _resolve_public_ips,
    request_public_https,
    validate_public_https_url,
)

RUNWAY_BASE = "https://api.dev.runwayml.com/v1"
RUNWAY_VERSION = "2024-11-06"

def _pinned_https_get(url: str, ip: str, *, timeout: int, headers=None):
    # Compatibility shim for the pre-QA 3.6 helper name.
    return request_public_https("GET", url, timeout=timeout, headers=headers, stream=True)


def safe_stream_get(url: str, *, timeout: int, max_redirects: int = 5):
    return request_public_https("GET", url, timeout=timeout, stream=True, max_redirects=max_redirects)

class VisualProviderError(RuntimeError):
    pass

class RunwayClient:
    def __init__(self, api_key: str, timeout: int = 1800):
        if not api_key or len(api_key.strip()) < 12:
            raise VisualProviderError("Runway API anahtar─▒ Ayarlar > AI G├Ârsel Motorlar─▒ b├Âl├╝m├╝ne girilmelidir.")
        self.api_key = api_key.strip()
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Runway-Version": RUNWAY_VERSION,
            "Content-Type": "application/json",
        }

    def _create(self, endpoint: str, payload: dict) -> str:
        response = request_public_https("POST", f"{RUNWAY_BASE}/{endpoint}", headers=self.headers, json=payload, timeout=90)
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
            response = request_public_https("GET", f"{RUNWAY_BASE}/tasks/{task_id}", headers=self.headers, timeout=45)
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
        raise VisualProviderError("Pexels API anahtar? Ayarlar > AI G?rsel Motorlar? b?l?m?ne girilmelidir.")
    from requests import Request
    request = Request(
        "GET", "https://api.pexels.com/v1/videos/search",
        headers={"Authorization": api_key.strip()},
        params={"query": query[:180], "orientation": orientation, "per_page": 8, "locale": "tr-TR"},
    ).prepare()
    response = request_public_https("GET", request.url, timeout=45, headers=request.headers, max_redirects=4)
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
