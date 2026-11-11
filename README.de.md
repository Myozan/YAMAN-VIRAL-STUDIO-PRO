# YAMAN VIRAL STUDIO PRO

Lokales KI-Videostudio für Videoanalyse, Shorts-Produktion und plattformübergreifende Workflows.

**Professionelle Benutzeroberfläche v1.5:** Symbolnavigation, neues App-Branding und Favicon, GitHub-Verknüpfungen, Breadcrumb-Navigation, überarbeitete dunkle Oberfläche, Tastaturfokus und mobile Navigation.

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
| ![Desktop](docs/assets/dashboard-desktop.png) | ![Mobil](docs/assets/dashboard-mobile.png) |

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
