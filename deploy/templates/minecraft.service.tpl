[Unit]
Description=Minecraft Instance {{INSTANCE_NAME}}
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory={{INSTANCE_DIR}}
ExecStart=/usr/local/lib/docker/cli-plugins/docker-compose -p {{INSTANCE_NAME}} up -d minecraft
ExecStop=/usr/local/lib/docker/cli-plugins/docker-compose -p {{INSTANCE_NAME}} stop minecraft
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
