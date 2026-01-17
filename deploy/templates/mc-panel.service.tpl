[Unit]
Description=Minecraft Panel
After=network.target

[Service]
Type=simple
WorkingDirectory={{PANEL_ROOT}}
Environment=MC_PANEL_BASE_DIR={{BASE_DIR}}
Environment=MC_PANEL_STATIC_DIR={{PANEL_STATIC_DIR}}
ExecStart={{PANEL_ROOT}}/.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port {{PANEL_PORT}}
Restart=on-failure

[Install]
WantedBy=multi-user.target
