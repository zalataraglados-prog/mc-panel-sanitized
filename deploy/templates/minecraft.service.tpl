[Unit]
Description=Minecraft Instance {{INSTANCE_NAME}}
After=network.target

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory={{INSTANCE_DIR}}
ExecStartPre=/usr/bin/env docker info > /dev/null 2>&1
ExecStart=/usr/bin/env docker compose -p {{INSTANCE_NAME}} up -d minecraft
ExecStop=/usr/bin/env docker compose -p {{INSTANCE_NAME}} stop minecraft
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
