[Unit]
Description=Minecraft Panel for {{INSTANCE_NAME}}
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory={{INSTANCE_DIR}}
ExecStart=/usr/bin/docker compose -p {{INSTANCE_NAME}} up -d mc-panel
ExecStop=/usr/bin/docker compose -p {{INSTANCE_NAME}} stop mc-panel
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target