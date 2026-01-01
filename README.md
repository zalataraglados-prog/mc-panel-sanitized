# MC Panel (demon1.1)

This project is a configuration decision engine for Minecraft deployments with an optional runtime panel.

## Quick start (plan + dry-run)

```
curl -fsSL https://raw.githubusercontent.com/zalataraglados-prog/mc-panel-sanitized/demon1.1/install.sh | sudo bash
```

## Optional Web Panel

The panel is optional. It can be installed during deploy or added later without affecting the server.

### Panel prerequisites

- Python packages: `fastapi`, `uvicorn`
- Frontend build output: `frontend/dist` (build with Node.js + npm)

### Install panel during deploy

When running `install.sh`, choose:
`Install Web Panel? [y/N]`

### Panel maintenance mode (existing instance)

`install.sh` offers a maintenance menu before deploy:

- Install panel for an existing instance
- Uninstall panel from an existing instance

### Add panel to an existing instance

```
sudo python3 -m deploy.cli panel install --instance-dir /opt/mc-instances/<instance-name>
```

Options:

- `--panel-port 15000` to override port
- `--no-start` to avoid starting the service immediately
- `--no-build` to skip frontend build
- `--panel-root /opt/mc-panel-sanitized` to point to the repo root

## Map plugins

During deploy, you can optionally enable Dynmap or BlueMap. The deployer can configure:

- plugin port (`map.plugin_port`)
- render interval (`map.render_interval`)
- optional world file copy (`map.file`, `map.target`, `map.overwrite`)

## Inventory plugins

During deploy, you can optionally install an inventory plugin for richer inventory editing.
Supported choices: InvSee++ or OpenInv. Provide a download URL when prompted.

## Plugin download logging

Download failures are appended to `logs/plugin_download.log`. If log push is enabled,
the deployer will attempt to push updates to the `logs` branch in the repo.

### Uninstall panel from an instance

```
sudo python3 -m deploy.cli panel uninstall --instance-dir /opt/mc-instances/<instance-name>
```

## Rules data source

Catalog/Taxonomy are stored in the external rules repository.

- https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/catalog/vanilla_1.21.4.json
- https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/taxonomy/vanilla_1.21.4.json
