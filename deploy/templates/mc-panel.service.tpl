[Unit]
Description=Minecraft Panel for {{INSTANCE_NAME}}
After=network.target

[Service]
Type=simple
WorkingDirectory={{PANEL_ROOT}}
Environment=MC_PANEL_INSTANCE_DIR={{INSTANCE_DIR}}
Environment=MC_PANEL_STATIC_DIR={{PANEL_STATIC_DIR}}
ExecStart=/usr/bin/python3 -m uvicorn backend.main:app --host 0.0.0.0 --port {{PANEL_PORT}}
Restart=on-failure

[Install]
WantedBy=multi-user.target
