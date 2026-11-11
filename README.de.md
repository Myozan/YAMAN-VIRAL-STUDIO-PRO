<div align="center">

<img src="docs/assets/hero.svg" alt="YAMAN VIRAL STUDIO PRO — Lokales KI-Videostudio" width="100%">

# YAMAN VIRAL STUDIO PRO

### Lokale KI-Videoanalyse, Shorts-Erstellung und plattformübergreifender Content-Workflow

[🇹🇷 Türkçe](README.md) · [🇬🇧 English](README.en.md) · [🇩🇪 Deutsch](README.de.md) · [🇪🇸 Español](README.es.md)

[![Version](https://img.shields.io/badge/version-1.4.1-6478ff?style=for-the-badge)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Local AI](https://img.shields.io/badge/AI-Local--First-8B5CF6?style=for-the-badge)](#architektur)
[![License](https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge)](LICENSE)

**Entwurf und Entwicklung: [Ozan Yaman](https://github.com/Myozan)**

</div>

---

## ✨ Überblick

YAMAN VIRAL STUDIO PRO ist ein lokales KI-Videostudio zur Analyse langer Videos, zur Transkription mit Zeitstempeln, zur Erkennung starker Momente und zur Vorbereitung von Kurzvideos für YouTube Shorts, Instagram Reels und TikTok.

Der Workflow mit Ollama, Faster-Whisper und FFmpeg ist darauf ausgelegt, die Verarbeitung möglichst auf dem eigenen Computer auszuführen.

## 🖥️ Anwendungsansichten

| Desktop-Arbeitsbereich | Responsive Mobilansicht |
|:---:|:---:|
| <img src="docs/assets/dashboard-desktop.png" alt="Desktop-Oberfläche" width="100%"> | <img src="docs/assets/dashboard-mobile.png" alt="Mobile Oberfläche" width="72%"> |

## 🚀 Zentrale Funktionen

<img src="docs/assets/feature-map.svg" alt="Funktionsübersicht" width="100%">

- **Videoimport:** YouTube-URL oder lokaler Windows-Downloads-Ordner.
- **Intelligente Transkription:** Zeitgestempeltes Faster-Whisper-Transkript und TXT-Export.
- **KI-Clipauswahl:** Clip-Kandidaten anhand von Hooks, Kontext, Sprachdichte und Wiedergabepotenzial.
- **KI-Zusammenfassungsvideo:** Vertikales MP4 mit Schlüsselmomenten, Untertiteln, Intro und Outro.
- **12 spezialisierte KI-Agenten:** Strategie, Hooks, Schnitt, SEO, Risikoprüfung, Barrierefreiheit, Lokalisierung und Veröffentlichungsvorbereitung.
- **Aufgabenorchestrierung:** SQLite-Aufgabenverlauf, Ereignisprotokoll, Abbruch, Wiederholung und Wiederherstellung nach Neustart.
- **Mehrsprachige Oberfläche:** Türkisch, Englisch, Deutsch und Spanisch; die Sprache wird in den Einstellungen gewählt.
- **Plattform-Workflows:** OAuth-Verbindung und nutzerbestätigte Veröffentlichungsvorbereitung für YouTube, TikTok und Instagram.
- **Systemüberwachung:** GPU-, CPU-, RAM- und VRAM-Auslastung.
- **Responsives UI:** Anpassung an Desktop- und Mobilbildschirme.

## 🔄 Produktionsablauf

<img src="docs/assets/pipeline.svg" alt="Video-Workflow" width="100%">

1. Quellvideo importieren.
2. Sprache mit Whisper transkribieren.
3. Starke Momente und Clips mit lokaler KI erkennen.
4. Vertikales Format, Untertitel und Plattformprofil anwenden.
5. MP4-Ausgabe prüfen und für die gewünschte Plattform vorbereiten.

## 🧩 Architektur

<img src="docs/assets/architecture.svg" alt="Anwendungsarchitektur" width="100%">

| Ebene | Technologie |
|---|---|
| API und Aufgabenverwaltung | Python 3.12 · FastAPI · Uvicorn |
| Lokales Sprachmodell | Ollama · Qwen |
| Spracherkennung | Faster-Whisper |
| Videobearbeitung | FFmpeg · FFprobe · yt-dlp |
| Weboberfläche | HTML · CSS · JavaScript |
| Dauerhafter Aufgabenverlauf | SQLite |
| OAuth-Geheimnisse | Lokale Fernet-Verschlüsselung |

## ⚙️ Installation unter Windows

**Voraussetzungen:** Windows 10/11, Python 3.12, FFmpeg und Ollama.

1. Repository klonen: **git clone https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO.git**
2. Projektordner öffnen.
3. Lokales Modell laden: **ollama pull qwen3:1.7b**
4. **run_windows.bat** ausführen.
5. Im Browser **http://127.0.0.1:8765** öffnen.

Für eine manuelle Installation eine Python-Umgebung erstellen und **pip install -r requirements.txt** ausführen.

## 🌐 Sprach- und Darstellungseinstellungen

Öffne **Einstellungen → Sprache & Lokalisierung** und wähle Türkçe, English, Deutsch oder Español. Die Auswahl wird im Browser gespeichert und beim nächsten Besuch wiederhergestellt. Das Darstellungsthema lässt sich unabhängig davon auf Dark, Light oder Ocean einstellen.

## 🔐 OAuth und Veröffentlichung

Hinterlege die Entwickler-Zugangsdaten im Bereich Plattformprofile. Zugangsdaten und Token werden lokal verschlüsselt.

| Plattform | Konfiguration | Berechtigung |
|---|---|---|
| YouTube | YAMAN_GOOGLE_CLIENT_ID / YAMAN_GOOGLE_CLIENT_SECRET | youtube.upload |
| TikTok | YAMAN_TIKTOK_CLIENT_KEY / YAMAN_TIKTOK_CLIENT_SECRET | video.publish |
| Instagram | YAMAN_META_APP_ID / YAMAN_META_APP_SECRET | instagram_basic, instagram_content_publish, pages_show_list |

Trage die exakte OAuth-Callback-URL in jeder Entwicklerkonsole ein. Jede Veröffentlichung erfordert eine ausdrückliche Nutzerbestätigung. YouTube-Uploads starten standardmäßig privat; TikTok-App-Prüfung und öffentliche HTTPS-Medien-URLs für Instagram richten sich nach den Plattformregeln.

## 🛡️ Sicherheit und Datenschutz

- KI- und Videoprozesse sind für lokale Dienste ausgelegt.
- OAuth-Geheimnisse und Zugriffstoken werden mit Fernet verschlüsselt.
- .oauth.key, Token-Tresor, settings.local.json und Workspace-Daten dürfen nicht in Git landen.
- Sichere .oauth.key separat; ohne diese Datei kann der verschlüsselte Token-Tresor nicht entschlüsselt werden.
- Importiere nur Inhalte, die du verwenden und erneut veröffentlichen darfst.

## 🗂️ Projektstruktur

- **app/** — FastAPI-Anwendung und KI-/Videologik
- **web/** — Weboberfläche, Styles und Client-Code
- **docs/** — Architektur, Integrationen und visuelle Dokumentation
- **workspace/** — Lokal erzeugte Dateien (von Git ausgeschlossen)
- **run_windows.bat** — Windows-Startskript
- **requirements.txt** — Python-Abhängigkeiten

## 🧭 Roadmap

<img src="docs/assets/roadmap.svg" alt="Produkt-Roadmap" width="100%">

## 📚 Technische Dokumentation

- [KI-Agenten und OAuth-Recherche](docs/AI-AGENTS-RESEARCH.md)
- [Architekturnotizen](docs/ARCHITECTURE.md)
- [Plattformintegrationen](docs/PLATFORM-INTEGRATIONS.md)
- [Änderungsprotokoll](CHANGELOG.md)

## 📄 Lizenz

MIT — siehe [LICENSE](LICENSE).

<div align="center">

**YAMAN VIRAL STUDIO PRO** · Entwickelt von [Ozan Yaman](https://github.com/Myozan)

</div>
