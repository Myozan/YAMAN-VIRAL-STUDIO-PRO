<div align="center">

# YAMAN VIRAL STUDIO PRO

[TR Turco](README.md) | [EN Inglés](README.en.md) | [DE Alemán](README.de.md) | [ES Español](README.es.md)

**Estudio local de producción de vídeo con IA**

Desarrollado por [Ozan Yaman](https://github.com/Myozan) | Versión 1.4.0

</div>

## Descripción

YAMAN VIRAL STUDIO PRO analiza vídeos localmente, crea transcripciones con Whisper, selecciona clips cortos y genera resúmenes de vídeo con IA. Utiliza FastAPI, Ollama, Faster-Whisper y FFmpeg.

## Funciones

- Importación de enlaces de YouTube y vídeos locales de Descargas.
- Transcripciones con marcas de tiempo y exportación TXT.
- Doce agentes especializados con informes independientes.
- Historial persistente de tareas, auditoría de eventos, cancelación, reintento y recuperación tras reinicio.
- Selector de idioma turco/inglés.
- Conexión OAuth y publicación confirmada por el usuario para YouTube, TikTok e Instagram.
- Almacenamiento local cifrado para credenciales y tokens OAuth.
- Perfiles de exportación para YouTube Shorts, Instagram Reels y TikTok.

## Instalación en Windows

Instala Python 3.12, FFmpeg y Ollama. Ejecuta ollama pull qwen3:1.7b, inicia run_windows.bat y abre http://127.0.0.1:8765.

## OAuth y publicación

Configura las credenciales de las aplicaciones de desarrollador en Perfiles de plataforma; se cifran localmente. YouTube requiere youtube.upload. TikTok Direct Post requiere el permiso aprobado video.publish; las aplicaciones no auditadas solo pueden publicar en privado. Instagram Reels necesita una cuenta profesional vinculada a una página de Facebook y una URL HTTPS pública para el vídeo. Cada publicación exige confirmación explícita.

## Seguridad

Los secretos y tokens OAuth se cifran localmente con Fernet. Conserva una copia de .oauth.key. No incluyas secretos ni tokens en Git.

## Licencia

MIT. Consulta LICENSE.
