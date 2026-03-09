{
  "schema_version": 1,

  "instance": {
    "name": "{{INSTANCE_NAME}}",
    "display_name": "{{INSTANCE_NAME}}",
    "description": "",
    "tags": [],
    "created_at": "{{CREATED_AT}}",
    "updated_at": "{{CREATED_AT}}",
    "enabled": true
  },

  "paths": {
    "instance_dir": "{{INSTANCE_DIR}}",
    "data_dir": "{{INSTANCE_DIR}}/data",
    "logs_dir": "{{INSTANCE_DIR}}/logs",
    "backups_dir": "{{INSTANCE_DIR}}/backups",
    "world_dir": "{{INSTANCE_DIR}}/data/world",
    "panel_dir": "{{INSTANCE_DIR}}/panel"
  },

  "network": {
    "bind_address": "0.0.0.0",
    "host": "",
    "mc_port": {{MC_PORT}},
    "panel_port": {{PANEL_PORT}},
    "rcon_port": {{RCON_PORT}},
    "rcon_bind": "{{RCON_BIND}}",
    "query_port": {{MC_PORT}},
    "use_https": false
  },

  "minecraft": {
    "engine": "paper",
    "version": "{{MC_VERSION}}",
    "world_name": "world",
    "difficulty": "hard",
    "game_mode": "survival",
    "max_players": 20,
    "online_mode": true,
    "view_distance": 10,
    "whitelist": false,
    "allow_flight": false,
    "level_type": "default",
    "motd": "{{INSTANCE_NAME}}",

    "jvm": {
      "memory": "{{MC_MEMORY}}",
      "extra_args": "-XX:+UseG1GC"
    },

    "properties": {
      "spawn-protection": 0,
      "pvp": true
    }
  },

  "panel": {
    "enabled": {{PANEL_ENABLED}},
    "port": {{PANEL_PORT}},
    "public_url": "",
    "secret_key": "{{PANEL_SECRET_KEY}}",
    "auth_enabled": false
  },

  "docker": {
    "image": "{{DOCKER_IMAGE}}",
    "tag": "{{DOCKER_TAG}}",
    "restart_policy": "always",
    "networks": ["default"],
    "extra_env": {
      "TZ": "Asia/Shanghai"
    },
    "volumes": {
      "data": "./data:/data",
      "logs": "./logs:/logs"
    }
  },

  "deployment": {
    "deployer_version": "{{DEPLOYER_VERSION}}",
    "git_repo": "",
    "git_commit": "",
    "installed_by": "root",
    "installed_at": "{{CREATED_AT}}",
    "auto_update": {
      "enabled": false,
      "channel": "stable"
    }
  },

  "security": {
    "rcon_enabled": true,
    "rcon_public": {{RCON_PUBLIC}},
    "rcon_password": "{{RCON_PASSWORD}}",
    "api_key": "",
    "allowed_ips": [],
    "allow_remote_panel": true
  },

  "features": {
    "enable_backups": false,
    "backup_cron": "0 4 * * *",
    "enable_metrics": false,
    "allow_offline_start": true,
    "auto_restart_on_crash": true
  }
}
