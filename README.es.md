# YAMAN VIRAL STUDIO PRO

Estudio de vídeo con IA local para analizar vídeos, crear Shorts y preparar contenido multiplataforma.

**Nueva interfaz profesional v1.5:** navegación con iconos, identidad visual y favicon, accesos directos a GitHub, ruta de navegación del espacio de trabajo, superficies oscuras refinadas, foco accesible y navegación móvil.

## Funciones principales
- Importación de fuentes de YouTube autorizadas o vídeos locales de Windows.
- Transcripción con Faster-Whisper y exportación con marcas de tiempo.
- Análisis con IA local para seleccionar clips cortos.
- Renderizado vertical con subtítulos para Shorts, Reels y TikTok.
- Agentes especializados y registro persistente de tareas.
- Configuración de modelos locales de Ollama y Whisper.
- Supervisión de GPU, CPU, RAM y VRAM.

## Capturas
| Escritorio | Móvil |
|---|---|
| ![Escritorio](docs/assets/dashboard-desktop.png) | ![Móvil](docs/assets/dashboard-mobile.png) |

## Instalación en Windows
Requisitos: Windows 10/11, Python 3.12, FFmpeg y Ollama.

```powershell
git clone https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO.git
cd YAMAN-VIRAL-STUDIO-PRO
ollama pull qwen3:1.7b
run_windows.bat
```

Abre http://127.0.0.1:8765. Consulta la [arquitectura](docs/ARCHITECTURE.md), las [integraciones](docs/PLATFORM-INTEGRATIONS.md) y el [registro de cambios](CHANGELOG.md).

Utiliza únicamente contenido multimedia cuyos derechos de uso y publicación tengas. La publicación mediante OAuth requiere permisos de la plataforma y confirmación explícita del usuario.
