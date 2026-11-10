@echo off
setlocal
cd /d "%~dp0"
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

where ffmpeg >nul 2>nul
if errorlevel 1 echo [UYARI] FFmpeg bulunamadi. FFmpeg ve FFprobe PATH'e eklenmeli.
where ollama >nul 2>nul
if errorlevel 1 (
  if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
)
where ollama >nul 2>nul
if errorlevel 1 (
  echo [UYARI] Ollama kurulu degil veya bulunamadi. Yerel AI siralamasi heuristic moda dusebilir.
  echo Resmi kurulum: https://ollama.com/download/windows
) else (
  echo [OK] Ollama CLI bulundu.
  ollama --version
)
echo YAMAN VIRAL STUDIO PRO at http://127.0.0.1:8765
python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
pause
