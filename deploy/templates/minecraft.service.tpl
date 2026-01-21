[Unit]
Description=Minecraft Instance {{INSTANCE_NAME}}
After=network.target

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory={{INSTANCE_DIR}}
ExecStartPre=/bin/sh -c 'docker info >/dev/null 2>&1'
ExecStart=/bin/sh -c 'if docker compose version >/dev/null 2>&1; then docker compose -p {{INSTANCE_NAME}} up -d minecraft; elif command -v docker-compose >/dev/null 2>&1; then docker-compose -p {{INSTANCE_NAME}} up -d minecraft; else exit 127; fi'
ExecStop=/bin/sh -c 'if docker compose version >/dev/null 2>&1; then docker compose -p {{INSTANCE_NAME}} stop minecraft; elif command -v docker-compose >/dev/null 2>&1; then docker-compose -p {{INSTANCE_NAME}} stop minecraft; else exit 127; fi'
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
