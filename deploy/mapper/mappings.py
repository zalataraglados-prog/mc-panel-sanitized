"""
Canonical parameter → legacy ConfigModel field mapping.

Left side:
  Canonical parameter key used by Claims / Planner / Renderer.

Right side:
  Tuple path locating the target field inside legacy config dict.

All mappings must be explicitly declared here.
"""

PARAMETER_MAPPINGS = {
    # ─────────────────────────
    # Instance
    # ─────────────────────────
    "instance.name": ("instance", "name"),
    "instance.profile": ("instance", "profile"),

    # ─────────────────────────
    # Network
    # ─────────────────────────
    "network.mc_port": ("network", "mc_port"),
    "network.rcon_port": ("network", "rcon_port"),
    "network.query_port": ("network", "query_port"),
    "server-port": ("network", "mc_port"),
    "rcon.port": ("network", "rcon_port"),
    "panel.port": ("network", "panel_port"),
    "query.port": ("network", "query_port"),

    # ─────────────────────────
    # Minecraft Core
    # ─────────────────────────
    "minecraft.version": ("minecraft", "version"),
    "minecraft.type": ("minecraft", "type"),
    "minecraft.max_players": ("minecraft", "max_players"),
    "minecraft.motd": ("minecraft", "motd"),
    "minecraft.online_mode": ("minecraft", "online_mode"),
    "minecraft.difficulty": ("minecraft", "difficulty"),
    "minecraft.gamemode": ("minecraft", "gamemode"),
    "minecraft.view_distance": ("minecraft", "view_distance"),
    "minecraft.simulation_distance": ("minecraft", "simulation_distance"),
    "max-players": ("minecraft", "max_players"),
    "motd": ("minecraft", "motd"),
    "online-mode": ("minecraft", "online_mode"),
    "difficulty": ("minecraft", "difficulty"),
    "gamemode": ("minecraft", "game_mode"),
    "view-distance": ("minecraft", "view_distance"),
    "simulation-distance": ("minecraft", "simulation_distance"),

    # ─────────────────────────
    # Docker / JVM
    # ─────────────────────────
    "docker.env.MEMORY": ("minecraft", "jvm", "memory"),
    "docker.env.TYPE": ("docker", "type"),
    "docker.env.JVM_OPTS": ("docker", "jvm_opts"),
    "docker.restart_policy": ("docker", "restart"),

    # ─────────────────────────
    # Security
    # ─────────────────────────
    "security.eula": ("security", "eula"),
    "security.whitelist": ("security", "whitelist"),
    "security.ops": ("security", "ops"),

    # ─────────────────────────
    # Features
    # ─────────────────────────
    "features.enable_rcon": ("features", "enable_rcon"),
    "features.enable_query": ("features", "enable_query"),
    "features.enable_panel": ("features", "enable_panel"),
}

# Planner-only parameter markers (not rendered into legacy config).
PLUGIN_PARAM_PREFIXES = ("plugins.",)
MOD_PARAM_PREFIXES = ("mods.",)


def is_plugin_param(key: str) -> bool:
    return any(key.startswith(prefix) for prefix in PLUGIN_PARAM_PREFIXES)


def is_mod_param(key: str) -> bool:
    return any(key.startswith(prefix) for prefix in MOD_PARAM_PREFIXES)


def capability_from_param_key(param_key: str) -> str:
    """
    Resolve capability id for a parameter key.

    Uses the mapping table to normalize aliases (e.g. server-port, panel.port)
    to their canonical capability root (network, minecraft, docker, features).
    """
    mapping = PARAMETER_MAPPINGS.get(param_key)
    if mapping:
        return mapping[0]
    return param_key.split(".", 1)[0]
