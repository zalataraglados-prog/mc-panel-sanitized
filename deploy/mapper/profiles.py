"""
Profile-based configuration overlays.

These overlays are applied AFTER Planner approval
and BEFORE execution.

They must be:
- conservative
- predictable
- reversible
"""

PROFILE_OVERRIDES = {
    "beginner": {
        # JVM / Docker
        "docker.env.MEMORY": "2G",
        "docker.env.JVM_OPTS": None,

        # Minecraft Core
        "minecraft.view_distance": 6,
        "minecraft.simulation_distance": 6,
        "minecraft.max_players": 10,
        "minecraft.online_mode": True,

        # Features
        "features.enable_rcon": False,
        "features.enable_query": False,
    },

    "normal": {
        # JVM / Docker
        "docker.env.MEMORY": "4G",

        # Minecraft Core
        "minecraft.view_distance": 8,
        "minecraft.simulation_distance": 8,
    },

    "advanced": {
        # Advanced users keep full control.
        # Only minimal safety defaults may apply.
    },
}
