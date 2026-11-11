# YAMAN VIRAL STUDIO PRO

<div align="center">

<img src="docs/assets/hero-v1.8.0.png" alt="YAMAN VIRAL STUDIO PRO v1.8.0 Premium AI Creator Studio" width="100%">

**CREACIÓN DE VÍDEO CON IA LOCAL · WINDOWS · PWA**

[![Versión](https://img.shields.io/badge/Versión-1.8.0-8b78f6?style=for-the-badge)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge)](https://fastapi.tiangolo.com/)
[![Licencia](https://img.shields.io/badge/Licencia-MIT-2ea44f?style=for-the-badge)](LICENSE)

[🇹🇷 Türkçe](README.md) · [🇬🇧 English](README.en.md) · [🇩🇪 Deutsch](README.de.md) · **🇪🇸 Español**

</div>

## ✦ Descripción general

YAMAN VIRAL STUDIO PRO es un **AI Creator Studio local-first** para convertir vídeos largos en vídeos cortos estructurados, editados y listos para publicar en YouTube Shorts, Instagram Reels y TikTok.

Whisper transcribe el audio, Ollama ayuda a analizar el contenido y FFmpeg corta, subtitula y renderiza vídeos verticales. El flujo principal de medios puede ejecutarse en tu propio equipo.

## ⚡ Inicio rápido

**Windows 10/11 · Python 3.12 · FFmpeg**

```powershell
git clone https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO.git
cd YAMAN-VIRAL-STUDIO-PRO
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
.\run_windows.bat
```

Abre **http://127.0.0.1:8765**. Instala [Ollama](https://ollama.com/download/windows) para el análisis local con IA.

## 🎬 Herramientas de creación

| Flujo | Función |
|---|---|
| **Whisper** | Transcripción de voz con marcas de tiempo |
| **Ollama** | Análisis local, guiones y selección de clips |
| **Smart Recap** | Selección de momentos clave y resumen |
| **Story Flow** | Narrativa desde la apertura hasta el cierre |
| **Documental** | Relato cronológico basado en la fuente |
| **Educación** | Objetivos, pasos, ejemplos y resumen |
| **Producto** | Vídeo de producto sin afirmaciones no verificadas |
| **FFmpeg** | Edición, subtítulos y exportación MP4 vertical |
| **Autopilot** | Flujos de producción local programados |
| **Biblioteca** | Gestión de fuentes, clips y resultados |

## 🖥️ Dentro del estudio

<p align="center"><strong>ESCRITORIO</strong></p>
<p align="center"><img src="docs/assets/screenshot-live-desktop-framed.png" alt="Interfaz de escritorio YAMAN Studio" width="100%"></p>

<p align="center"><strong>MÓVIL</strong></p>
<p align="center"><img src="docs/assets/screenshot-live-mobile-framed.png" alt="Interfaz móvil YAMAN Studio" width="52%"></p>

## 🔐 Local y bajo control

- La transcripción, el análisis y el procesamiento central pueden ejecutarse localmente.
- Runway, Pexels y Edge TTS son servicios opcionales que requieren conexión.
- Las credenciales se mantienen en el almacén local cifrado.
- La publicación requiere confirmación explícita.
- Importa y publica únicamente medios para los que tengas derechos de uso.

## ♻️ Actualizaciones

Las instalaciones pueden consultar la rama configurada de GitHub y mostrar una oferta de actualización cuando exista un commit más reciente. Antes de reemplazar archivos de la aplicación se crea una copia de seguridad. Los medios, ajustes y credenciales locales están diseñados para conservarse. Nunca se instala una actualización sin aprobación.

## 🧩 Arquitectura y documentación

<p align="center"><img src="docs/assets/architecture.svg" alt="Arquitectura de YAMAN Studio" width="100%"></p>

[Registro de cambios](CHANGELOG.md) · [Arquitectura](docs/ARCHITECTURE.md) · [Integraciones](docs/PLATFORM-INTEGRATIONS.md) · [Demo](docs/DEMO.md) · [Contribuir](CONTRIBUTING.md) · [Seguridad](SECURITY.md) · [Licencias](LICENSING.md)

## ⚖️ Licencia

Los archivos de código Community cubiertos por [LICENSE](LICENSE) se distribuyen bajo MIT. Las dependencias y servicios de terceros mantienen sus propias licencias. Consulta [LICENSING.md](LICENSING.md).

<div align="center">

**YAMAN VIRAL STUDIO PRO · v1.8.0**

*Crear localmente. Editar con inteligencia. Publicar en todas partes.*

[Repositorio](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO)

</div>
