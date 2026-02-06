[Unit]
Description=Minecraft Panel
After=network.target

[Service]
Type=simple
WorkingDirectory={{PANEL_ROOT}}
Environment=MC_PANEL_BASE_DIR={{BASE_DIR}}
Environment=MC_PANEL_STATIC_DIR={{PANEL_STATIC_DIR}}
ExecStartPre=/bin/sh -c 'test -f "{{PANEL_STATIC_DIR}}/index.html" || echo "[mc-panel] 前端构建缺失：{{PANEL_STATIC_DIR}}（请运行 npm install && npm run build）"'
ExecStart={{PANEL_ROOT}}/.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port {{PANEL_PORT}}
Restart=on-failure

[Install]
WantedBy=multi-user.target
