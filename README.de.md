# YAMAN VIRAL STUDIO PRO

Lokales **KI-Video-Repurposing-Studio** für Videoanalyse, Transkription und die Erstellung vertikaler Clips für YouTube Shorts, Instagram Reels und TikTok.

<p align="center"><img src="docs/assets/hero.svg" alt="YAMAN VIRAL STUDIO PRO" width="100%"></p>

<p align="center"><a href="https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/actions/workflows/ci.yml"><img src="https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/actions/workflows/ci.yml/badge.svg?branch=import%2Fv1.2-source" alt="CI-Status"></a> <img src="https://img.shields.io/badge/AI-Local--First-7C5CFA" alt="Lokale KI"> <img src="https://img.shields.io/badge/PWA-installierbar-5B8DEF" alt="PWA"></p>

**v1.5.2 · PWA und responsives UI.** Die Desktop- und Mobilansichten sind illustrative Designvorschauen, keine Live-Screenshots.

## Funktionen
- Import geeigneter YouTube-Quellen oder lokaler Videos aus dem Windows-Downloads-Ordner.
- Transkription mit Faster-Whisper und Export mit Zeitstempeln.
- Lokale KI-Analyse zur Auswahl möglicher Kurzclips.
- Vertikale Videos mit Untertiteln für Shorts, Reels und TikTok.
- KI-Agenten und dauerhaft gespeicherter Aufgabenverlauf.
- Konfiguration von Ollama- und Whisper-Modellen.
- Überwachung von GPU, CPU, RAM und VRAM.

## Screenshots
| Desktop | Mobil |
|---|---|
| ![Desktop](docs/assets/dashboard-desktop.svg) | ![Mobil](docs/assets/dashboard-mobile.svg) |

## PWA-Installation

Die Installation erfordert HTTPS oder localhost. Unter iOS: Safari → Teilen → Zum Home-Bildschirm. Offline wird nur die App-Oberfläche zwischengespeichert; KI, Videoverarbeitung und API-Funktionen benötigen weiterhin den lokalen Server.

## Windows-Installation
Voraussetzungen: Windows 10/11, Python 3.12, FFmpeg und Ollama.

```powershell
git clone https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO.git
cd YAMAN-VIRAL-STUDIO-PRO
ollama pull qwen3:1.7b
run_windows.bat
```

Öffne http://127.0.0.1:8765. Weitere Informationen: [Architektur](docs/ARCHITECTURE.md), [Plattformintegrationen](docs/PLATFORM-INTEGRATIONS.md), [Änderungsprotokoll](CHANGELOG.md).

Verwende nur Medien, für die du die erforderlichen Nutzungsrechte besitzt. Veröffentlichungen über OAuth erfordern Plattformfreigaben und eine ausdrückliche Benutzerbestätigung.
