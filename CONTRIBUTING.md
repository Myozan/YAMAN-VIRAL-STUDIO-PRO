# Contributing to YAMAN VIRAL STUDIO PRO

Thank you for helping improve the project.

## Before you start

1. Search existing issues and pull requests before opening a duplicate.
2. For bugs, include your Windows version, Python version, relevant logs and exact reproduction steps. Remove tokens, personal data and local file paths from logs.
3. For feature proposals, describe the user problem, expected behavior and acceptance criteria.
4. Keep changes focused. Avoid unrelated formatting or generated workspace files.

## Development setup

- Windows 10/11
- Python 3.12
- FFmpeg / FFprobe
- Ollama (only for local AI features)
- Node.js (for frontend syntax checks)

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the app with `run_windows.bat`. The default local address is `http://127.0.0.1:8765`.

## Before submitting a pull request

Run the checks that apply to your change:

```powershell
python -m compileall -q app
node --check web/app.js
node --check web/sw.js
```

For UI changes, verify desktop and narrow mobile layouts. For API or media changes, include a clear manual test plan.

## Pull request checklist

- [ ] The change solves one clearly described problem.
- [ ] No secrets, OAuth tokens, personal data or generated media are committed.
- [ ] Documentation and screenshots are updated when behavior or UI changes.
- [ ] Relevant checks pass.
- [ ] Breaking changes and limitations are documented.

By contributing, you agree that your contributions are provided under the repository's MIT license unless a different written agreement is explicitly made.
