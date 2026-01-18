services:

  minecraft:
    image: {{DOCKER_IMAGE}}:{{DOCKER_TAG}}
    container_name: {{INSTANCE_NAME}}-minecraft
    restart: {{RESTART_POLICY}}
    ports:
{{PORTS_BLOCK}}
    environment:
      - EULA=TRUE
      - VERSION={{MC_VERSION}}
      - MEMORY={{MC_MEMORY}}
      - ENABLE_RCON=TRUE
      - RCON_PASSWORD={{RCON_PASSWORD}}
      - RCON_PORT={{RCON_PORT}}
{{ENV_BLOCK}}
    volumes:
{{VOLUME_BLOCK}}
    networks:
      - default
      
networks:
  default:
    driver: bridge
