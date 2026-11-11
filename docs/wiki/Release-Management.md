# Release Management

## Version source of truth

The v1.8.0 application version is declared in FastAPI metadata and the repository README/CHANGELOG. Release documentation should keep these aligned.

## Before a release

- [ ] Update application version and CHANGELOG.
- [ ] Verify README screenshots and version badges.
- [ ] Run Python compile and frontend syntax checks.
- [ ] Test install from a clean Python 3.12 environment.
- [ ] Test Ollama unavailable and available states.
- [ ] Test FFmpeg probing, transcription, clip render and export.
- [ ] Test Autopilot schedule creation and manual run.
- [ ] Test update check and user-approved update flow.
- [ ] Verify no credentials, workspace files or private media are included.
- [ ] Review third-party dependency and asset licenses.

## Release artifacts

Provide a tagged source release and clearly describe:
- supported operating system and Python version
- installation and upgrade path
- known limitations
- optional provider setup
- database/workspace backup guidance
- breaking changes and migration notes

## Update safety

The launcher checks the configured GitHub update branch. The update process is designed to request user approval and preserve local data. Users should still back up the workspace and settings before updating.

## Documentation quality gate

Every shipped feature should have:
1. user-facing guide
2. configuration reference
3. API reference when applicable
4. troubleshooting entry
5. release note
6. test evidence or explicit known limitation
