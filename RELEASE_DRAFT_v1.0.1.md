# MC Panel v1.0.1

This patch release fixes deploy flow issues reported after v1.0.0.

AI Usage Notice
This project was developed by a single person (freshman year). Due to limited time and technical resources, AI assistance was heavily used throughout the implementation.

Fixes
- Language selection added at the start of install flow.
- Minecraft version input is now a menu + validated custom entry.
- Map plugin choice validates download URL; failed option no longer proceeds.
- Blocked plan now allows interactive adjustments before exit.
- Player-scope block rule relaxed to warn with recommendations (e.g., allow-flight).

Quick start
```
curl -fsSL https://raw.githubusercontent.com/zalataraglados-prog/mc-panel-sanitized/v1.0.1/install.sh | sudo bash
```
