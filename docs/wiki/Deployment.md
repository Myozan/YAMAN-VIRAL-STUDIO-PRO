# Deployment Guide

## Supported local deployment

The documented launcher is Windows 10/11 + Python 3.12 + FastAPI/Uvicorn, started by `run_windows.bat`.

Default bind:
- Host: 127.0.0.1
- Port: 8765

This is suitable for local use on the same computer. It is not a hardened multi-user production deployment.

## Local startup

    .\run_windows.bat

Open:

    http://127.0.0.1:8765

## Optional services

| Service | Use | Requirement |
|---|---|---|
| Ollama | Local LLM analysis and script generation | Installed model and local service |
| FFmpeg/FFprobe | Video probing and rendering | Installed binaries on PATH |
| Auto-Editor | Optional silence removal | Separate official binary on PATH |
| Runway | Optional remote visual generation | Provider API key and network access |
| Pexels | Optional stock video search | Provider API key and network access |
| Edge TTS | Neural narration | Network/service availability |

## LAN access

Do not change the host binding to 0.0.0.0 for convenience without first implementing authentication, authorization, private media access controls, HTTPS and firewall restrictions. Current code should be treated as a single-user local application.

## Docker and server deployment

A verified Docker production recipe is not included in the inspected v1.8.0 launcher and dependency files. Do not treat Docker, PostgreSQL, Redis, or NAS object storage as ready-to-run deployment components merely because they appear in an extended architecture proposal.

Before production packaging, define:
- supported OS and hardware matrix
- service user and file permissions
- secret/key provisioning
- database and media volume strategy
- health checks and graceful shutdown
- backup/restore and upgrade/rollback
- authentication, HTTPS and monitoring
- platform API review and quota handling

## Backup recommendation

Stop the app before copying SQLite databases. Back up workspace media, SQLite databases, local settings and encryption keys as one protected set. Encrypt backups and periodically test restore.
