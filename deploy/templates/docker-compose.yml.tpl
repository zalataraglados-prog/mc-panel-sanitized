version: '3'

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
      - VERSION="{{MC_VERSION}}"
      - MEMORY="{{MC_MEMORY}}"
{{ENV_BLOCK}}
    volumes:
{{VOLUME_BLOCK}}
    networks:
      - default

  mc-panel:
    build: {{PANEL_BUILD_PATH}}
    container_name: {{INSTANCE_NAME}}-panel
    restart: always
    ports:
      - "{{PANEL_PORT}}:5000"
    networks:
      - default

networks:
  default:
    driver: bridge