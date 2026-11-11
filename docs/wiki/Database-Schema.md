# Database Schema

Bu doküman, v1.8.0 kodunda görülen yerel SQLite veri depolarını açıklar. PostgreSQL/Redis gibi mimari tasarım seçenekleri mevcut yerel kurulumun zorunlu bağımlılığı değildir.

## Storage locations

- `workspace/orchestration.sqlite3` — görevler, görev olayları, Autopilot ve OAuth state kayıtları.
- `workspace/viral_learning.sqlite3` — performans örnekleri.
- `workspace/<job_id>/job.json` — tamamlanmış analiz işinin yeniden yüklenebilir özeti.
- `workspace/oauth_tokens.enc` — şifreli OAuth token kasası.
- `workspace/oauth_apps.enc` — şifreli OAuth uygulama kimlik bilgileri.
- `workspace/visual_providers.enc` — şifreli görsel sağlayıcı anahtarları.
- `settings.local.json` — yerel Ollama/Whisper ayarları.
- `.oauth.key` — varsayılan Fernet anahtar dosyası; ortam değişkeniyle dışarı alınabilir.

## Tables

### orchestration.sqlite3

**tasks**
- task_id (primary key)
- created_at, updated_at
- status, percent, stage
- payload_json

**task_events**
- id (primary key)
- task_id, event_type, created_at
- payload_json

**autopilots**
- id (primary key), name, niche, language
- clips, min_seconds, max_seconds
- platforms_json, frequency, publish_time, timezone
- enabled, next_run, last_run, last_status, last_message
- processed_json, created_at, updated_at

**autopilot_runs**
- id (primary key), autopilot_id
- started_at, finished_at, status, message
- task_id, job_id, output_json

**oauth_states**
- state (primary key), platform, verifier, redirect_uri, created_at

### viral_learning.sqlite3

**performance**
- id (primary key), fingerprint, platform
- views, likes, comments, shares
- watch, duration, created_at

## Relationships

- task_events.task_id refers logically to tasks.task_id.
- autopilot_runs.autopilot_id refers logically to autopilots.id.
- job.json files are filesystem-backed job records; they are not relational rows.
- SQLite schema currently relies on application-level relationships in the inspected code.

## Backup and restore

1. Stop the application before copying SQLite files for a consistent offline backup.
2. Back up the complete workspace, settings.local.json and .oauth.key together.
3. Protect the backup with access controls and encryption; it may contain private media and credentials.
4. Restore the key file and encrypted vault files as a matched set.
5. Start the application and verify task history, media paths and OAuth status.

Never commit workspace databases, OAuth vaults, private media or encryption keys to Git.
