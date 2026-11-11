import shutil
import subprocess
from pathlib import Path

import pytest

from app import main


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
                    reason="FFmpeg/FFprobe are not installed")
def test_real_ffmpeg_render_is_repeat_safe_and_probeable(tmp_path):
    source = tmp_path / "qa38-source.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=24",
            "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100",
            "-t", "4", "-c:v", "libx264", "-preset", "ultrafast",
            "-pix_fmt", "yuv420p", "-c:a", "aac", str(source),
        ],
        check=True, capture_output=True, text=True, timeout=60,
    )
    job = {"folder": str(tmp_path), "video": str(source), "segments": []}
    clip = {
        "id": 1, "start": 0.0, "end": 3.5, "duration": 3.5,
        "title": "QA 3.8 repeat-safe render", "text": "Synthetic QA media fixture",
    }

    first = main.render_variant(job, clip, "youtube", captions=False)
    first_size = first.stat().st_size
    second = main.render_variant(job, clip, "youtube", captions=False)
    info = main.probe_media_info(second)

    assert first == second
    assert first.is_file() and second.stat().st_size > 0
    assert first_size > 0
    assert info["duration"] > 0
    video_stream = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
    assert video_stream["width"] == 1080
    assert video_stream["height"] == 1920
