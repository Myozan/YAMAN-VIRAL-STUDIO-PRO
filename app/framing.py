import subprocess
import shutil
from pathlib import Path


def render_face_tracked(source, output, start, duration, width=1080, height=1920):
    """Render a reliable 9:16 crop with FFmpeg; OpenCV is deliberately not required.

    The historical function name is kept for API compatibility. Current builds of
    OpenCV 5 may omit CascadeClassifier, so rendering must never depend on it.
    """
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg bulunamadı. FFmpeg kurulumunu ve PATH ayarını kontrol edin.")

    source = Path(source)
    output = Path(output)
    if not source.is_file():
        raise FileNotFoundError(f"Kaynak video bulunamadı: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)

    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},setsar=1"
    )
    cmd = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
        "-ss", str(max(0, float(start))), "-i", str(source),
        "-t", str(max(0.1, float(duration))),
        "-map", "0:v:0", "-map", "0:a?", "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", "-shortest", str(output),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0 or not output.is_file() or output.stat().st_size == 0:
        output.unlink(missing_ok=True)
        detail = (result.stderr or result.stdout or "Bilinmeyen FFmpeg hatası")[-2500:]
        raise RuntimeError("Dikey video oluşturulamadı: " + detail)
    return output
