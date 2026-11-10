<div align="center">

# YAMAN VIRAL STUDIO PRO

[TR Türkçe](README.md) | [EN English](README.en.md) | [DE Deutsch](README.de.md) | [ES Español](README.es.md)

**Lokale KI-Videoproduktionsumgebung**

Entwickelt von [Ozan Yaman](https://github.com/Myozan) | Version 1.4.0

</div>

## Überblick

YAMAN VIRAL STUDIO PRO analysiert Videos lokal, erstellt Whisper-Transkripte, wählt Kurzclips aus und erzeugt KI-Videozusammenfassungen. Die Anwendung verwendet FastAPI, Ollama, Faster-Whisper und FFmpeg.

## Funktionen

- Import von YouTube-URLs und lokalen Videos aus dem Downloads-Ordner.
- Zeitgestempelte Transkripte und TXT-Export.
- Zwölf spezialisierte KI-Agenten mit Einzelberichten.
- Persistente Aufgabenhistorie, Ereignisprotokoll, Abbruch, Wiederholung und Neustart-Wiederherstellung.
- Sprachumschaltung zwischen Türkisch und Englisch.
- OAuth-Verbindung und benutzerbestätigte Veröffentlichung für YouTube, TikTok und Instagram.
- Verschlüsselte lokale Speicherung von OAuth-Zugangsdaten und Token.
- Exportprofile für YouTube Shorts, Instagram Reels und TikTok.

## Installation unter Windows

Python 3.12, FFmpeg und Ollama installieren. ollama pull qwen3:1.7b ausführen, run_windows.bat starten und http://127.0.0.1:8765 öffnen.

## OAuth und Veröffentlichung

Die Entwickler-App-Zugangsdaten werden auf der Seite Plattformprofile konfiguriert und lokal verschlüsselt. YouTube benötigt youtube.upload. TikTok Direct Post erfordert die genehmigte video.publish-Berechtigung. Nicht geprüfte TikTok-Apps dürfen nur private Beiträge veröffentlichen. Instagram Reels benötigt ein professionelles Konto, eine Facebook-Seitenverknüpfung und eine öffentlich erreichbare HTTPS-Video-URL. Jede Veröffentlichung verlangt eine ausdrückliche Bestätigung.

## Sicherheit

OAuth-Geheimnisse und Token werden lokal mit Fernet verschlüsselt. Die Datei .oauth.key muss gesichert werden. Geheimnisse und Token dürfen nicht in Git eingecheckt werden.

## Lizenz

MIT. Siehe LICENSE.
