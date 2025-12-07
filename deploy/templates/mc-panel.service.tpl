[Unit]
Description=Minecraft Panel for {{INSTANCE_NAME}}
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory={{INSTANCE_DIR}}
ExecStart=/usr/local/lib/docker/cli-plugins/docker-compose -p {{INSTANCE_NAME}} up -d --build
ExecStop=/usr/local/lib/docker/cli-plugins/docker-compose -p {{INSTANCE_NAME}} down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
