services:

  minecraft:
    image: {{DOCKER_IMAGE}}:{{DOCKER_TAG}}
    container_name: {{INSTANCE_NAME}}-minecraft
    restart: {{RESTART_POLICY}}
    ports:
      - "{{MC_PORT}}:25565"
      - "{{RCON_PORT}}:25575"
    environment:
      - EULA=TRUE
      - VERSION={{MC_VERSION}}
      - MEMORY={{MC_MEMORY}}
      - ENABLE_RCON=TRUE
      - RCON_PASSWORD={{RCON_PASSWORD}}
      - RCON_PORT=25575
{{ENV_BLOCK}}
    volumes:
{{VOLUME_BLOCK}}
    networks:
      - default
      
networks:
  default:
    driver: bridge
