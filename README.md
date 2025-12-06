attention!!! this branch is only used as a storage of this version. demo-1 will continue change.this branch will stay still.





# MC Panel Deploy (PoC)

This branch only keeps the deploy tooling: a Python-based, opinionated bootstrapper that provisions a Minecraft server instance with Docker and systemd using the templates in `deploy/templates/`.

## What it does
- Checks prerequisites (root, Docker, Compose).
- Asks for an instance name, creates structure under `/opt/mc-instances/<name>/`.
- Auto-generates `config.json`, `docker-compose.yml`, and a `mc-<name>.service` unit.
- Brings the stack up and enables/starts the systemd service.

## Prerequisites
- Linux host with Docker and docker-compose available in PATH.
- Run as root (the script enforces this).
- The web panel build is expected at `../web-panel` relative to `deploy/` (see `WEB_PANEL_PATH` in `deploy/setup.py`).

## Quick start
```bash
git checkout deploy-only
python3 deploy/setup.py
```

The script will prompt for an instance name, generate files, run `docker-compose up`, and configure `systemd` for `mc-<name>.service`.

## Layout
- `deploy/core/` runtime logic: env checks, naming, instance creation, compose/systemd generators, deployer.
- `deploy/templates/` Jinja-free templates for compose and systemd units.
- `deploy/utils/` helpers for logging and file operations.
- `deploy/setup.py` entry point.

## Notes / caveats
- Paths and ports are generated; defaults: `/opt/mc-instances`, MC `25565`, panel `5000` (mapped from container).
- Update `WEB_PANEL_PATH` or template contents if your panel build lives elsewhere.
- This is a PoC; tighten security (RCON password, API keys, HTTPS) before production use.
