import os
import subprocess
import sys
import time
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(os.name != "nt", reason="Windows Job Object lifecycle test")
@pytest.mark.skipif(not __import__("shutil").which("ffmpeg"), reason="FFmpeg is not installed")
def test_killing_worker_also_terminates_its_ffmpeg_child(tmp_path):
    worker_code = r"""
import subprocess
from app.process_control import run_media_process

run_media_process(
    ["ffmpeg", "-hide_banner", "-loglevel", "error", "-re",
     "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=24",
     "-t", "120", "-f", "null", "NUL"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
"""
    worker = subprocess.Popen(
        [sys.executable, "-c", worker_code],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    child_pid = None
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and worker.poll() is None:
            # Query the direct child without adding a dependency such as psutil.
            query = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command",
                 f"(Get-CimInstance Win32_Process -Filter 'ParentProcessId={worker.pid}' | "
                 "Select-Object -First 1 -ExpandProperty ProcessId)"],
                capture_output=True, text=True, timeout=5,
            )
            if query.returncode == 0 and query.stdout.strip().isdigit():
                child_pid = int(query.stdout.strip())
                break
            time.sleep(0.25)
        assert child_pid is not None, "FFmpeg child process did not start"
        worker.kill()
        worker.wait(timeout=10)

        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            check = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command",
                 f"if (Get-Process -Id {child_pid} -ErrorAction SilentlyContinue) "
                 "{ exit 1 } else { exit 0 }"],
                capture_output=True, text=True, timeout=5,
            )
            if check.returncode == 0:
                break
            time.sleep(0.2)
        else:
            pytest.fail(f"FFmpeg child {child_pid} survived worker termination")
    finally:
        if worker.poll() is None:
            worker.kill()
            worker.wait(timeout=10)
        if child_pid is not None:
            subprocess.run(
                ["taskkill", "/PID", str(child_pid), "/T", "/F"],
                capture_output=True, text=True, timeout=10,
            )
