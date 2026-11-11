<div align="center">

<img src="docs/assets/hero.svg" alt="YAMAN VIRAL STUDIO PRO — Estudio local de vídeo con IA" width="100%">

# YAMAN VIRAL STUDIO PRO

### Análisis de vídeo con IA local, creación de Shorts y flujo de contenido multiplataforma

[🇹🇷 Türkçe](README.md) · [🇬🇧 English](README.en.md) · [🇩🇪 Deutsch](README.de.md) · [🇪🇸 Español](README.es.md)

[![Version](https://img.shields.io/badge/version-1.4.1-6478ff?style=for-the-badge)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Local AI](https://img.shields.io/badge/AI-Local--First-8B5CF6?style=for-the-badge)](#arquitectura)
[![License](https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge)](LICENSE)

**Diseñado y desarrollado por [Ozan Yaman](https://github.com/Myozan)**

</div>

---

## ✨ Descripción general

YAMAN VIRAL STUDIO PRO es un estudio de vídeo con IA local que analiza vídeos largos, transcribe el habla con marcas de tiempo, detecta los momentos más potentes y prepara contenido corto para YouTube Shorts, Instagram Reels y TikTok.

El flujo de trabajo basado en Ollama, Faster-Whisper y FFmpeg está diseñado para mantener el procesamiento en el propio ordenador siempre que sea posible.

## 🖥️ Capturas de la aplicación

| Espacio de trabajo de escritorio | Vista adaptable para móvil |
|:---:|:---:|
| <img src="docs/assets/dashboard-desktop.png" alt="Interfaz de escritorio" width="100%"> | <img src="docs/assets/dashboard-mobile.png" alt="Interfaz móvil" width="72%"> |

## 🚀 Funciones principales

<img src="docs/assets/feature-map.svg" alt="Mapa de funciones del producto" width="100%">

- **Importación de vídeo:** URL de YouTube o carpeta local Descargas de Windows.
- **Transcripción inteligente:** Transcripción Faster-Whisper con marcas de tiempo y exportación TXT.
- **Selección de clips con IA:** Momentos candidatos según hooks, contexto, densidad de voz y potencial de visualización.
- **Vídeo resumen con IA:** MP4 vertical con momentos clave, subtítulos, introducción y cierre.
- **12 agentes especializados:** Estrategia, hooks, edición, SEO, revisión de riesgos, accesibilidad, localización y preparación de publicaciones.
- **Orquestación de tareas:** Historial SQLite, registro de eventos, cancelación, reintento y recuperación tras reiniciar.
- **Interfaz multilingüe:** Turco, inglés, alemán y español; el idioma se configura en Ajustes.
- **Flujos de plataforma:** Conexión OAuth y preparación de publicaciones con aprobación del usuario para YouTube, TikTok e Instagram.
- **Monitorización del sistema:** Uso de GPU, CPU, RAM y VRAM.
- **Interfaz adaptable:** Diseño para escritorio y dispositivos móviles.

## 🔄 Flujo de producción

<img src="docs/assets/pipeline.svg" alt="Flujo de producción de vídeo" width="100%">

1. Importa el vídeo de origen.
2. Transcribe el audio con Whisper.
3. Detecta momentos destacados y clips con IA local.
4. Aplica encuadre vertical, subtítulos y perfil de plataforma.
5. Revisa el MP4 y prepáralo para la plataforma elegida.

## 🧩 Arquitectura

<img src="docs/assets/architecture.svg" alt="Arquitectura de la aplicación" width="100%">

| Capa | Tecnología |
|---|---|
| API y gestión de tareas | Python 3.12 · FastAPI · Uvicorn |
| Modelo de lenguaje local | Ollama · Qwen |
| Reconocimiento de voz | Faster-Whisper |
| Procesamiento de vídeo | FFmpeg · FFprobe · yt-dlp |
| Interfaz web | HTML · CSS · JavaScript |
| Historial persistente | SQLite |
| Secretos OAuth | Cifrado local Fernet |

## ⚙️ Instalación en Windows

**Requisitos:** Windows 10/11, Python 3.12, FFmpeg y Ollama.

1. Clona el repositorio: **git clone https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO.git**
2. Abre la carpeta del proyecto.
3. Descarga el modelo local: **ollama pull qwen3:1.7b**
4. Ejecuta **run_windows.bat**.
5. Abre **http://127.0.0.1:8765** en el navegador.

Para una instalación manual, crea un entorno virtual de Python y ejecuta **pip install -r requirements.txt**.

## 🌐 Ajustes de idioma y apariencia

En la aplicación, abre **Ajustes → Idioma y localización** y selecciona Türkçe, English, Deutsch o Español. La preferencia se guarda en el navegador y se restaura en la próxima visita. El tema visual se puede cambiar por separado entre Dark, Light y Ocean.

## 🔐 OAuth y publicación

Configura las credenciales de desarrollador en Perfiles de plataforma. Las credenciales y los tokens se cifran localmente.

| Plataforma | Configuración | Permiso |
|---|---|---|
| YouTube | YAMAN_GOOGLE_CLIENT_ID / YAMAN_GOOGLE_CLIENT_SECRET | youtube.upload |
| TikTok | YAMAN_TIKTOK_CLIENT_KEY / YAMAN_TIKTOK_CLIENT_SECRET | video.publish |
| Instagram | YAMAN_META_APP_ID / YAMAN_META_APP_SECRET | instagram_basic, instagram_content_publish, pages_show_list |

Registra la URL exacta de callback OAuth en cada consola de desarrollador. Cada publicación requiere confirmación explícita del usuario. Las subidas a YouTube empiezan como privadas; la revisión de TikTok y las URL HTTPS públicas de Instagram dependen de las políticas de cada plataforma.

## 🛡️ Seguridad y privacidad

- La IA y el procesamiento de vídeo están diseñados para utilizar servicios locales.
- Los secretos OAuth y los tokens se cifran con Fernet.
- No incluyas .oauth.key, la bóveda de tokens, settings.local.json ni los datos del espacio de trabajo en Git.
- Guarda .oauth.key en un lugar seguro; sin ella no se podrá descifrar la bóveda.
- Importa únicamente contenido que tengas derecho a utilizar y volver a publicar.

## 🗂️ Estructura del proyecto

- **app/** — Aplicación FastAPI y lógica de IA/vídeo
- **web/** — Interfaz web, estilos y código cliente
- **docs/** — Arquitectura, integraciones y documentación visual
- **workspace/** — Archivos generados localmente (excluidos de Git)
- **run_windows.bat** — Lanzador de Windows
- **requirements.txt** — Dependencias de Python

## 🧭 Hoja de ruta

<img src="docs/assets/roadmap.svg" alt="Hoja de ruta del producto" width="100%">

## 📚 Documentación técnica

- [Investigación de agentes IA y OAuth](docs/AI-AGENTS-RESEARCH.md)
- [Notas de arquitectura](docs/ARCHITECTURE.md)
- [Integraciones de plataformas](docs/PLATFORM-INTEGRATIONS.md)
- [Historial de cambios](CHANGELOG.md)

## 📄 Licencia

MIT — consulta [LICENSE](LICENSE).

<div align="center">

**YAMAN VIRAL STUDIO PRO** · Desarrollado por [Ozan Yaman](https://github.com/Myozan)

</div>
