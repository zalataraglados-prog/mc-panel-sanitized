# Changelog

## [Unreleased]

## [2026-01-06]
### Added
- RCON health check endpoint and UI status badge (`/api/rcon/health`, status tag in dashboard).
- Claims export API (`/api/claims/export`) and UI button to export the full defaults + overrides as a claims string.
- Gamerule export via RCON during claims export (fallback to defaults when RCON fails).
- Recommendation sampling tool for planner validation (`deploy/tools/recommendation_sampling.py`).

### Changed
- RCON connection now resolves host port from instance `config.json` or `docker-compose.yml` before falling back to `server.properties`.
- Planner scope warnings now trigger only when a parameter is explicitly changed (avoids default-noise warnings).
- Capacity guard: warn when `memory <= required` (keeps block thresholds intact).
- install.sh now pre-fills params with catalog defaults and merges imported claims; prompt loop uses defaults as visible values.

### Fixed
- Claims import no longer loses defaults when used in combination with manual overrides.
- Web UI now exposes clear RCON error feedback.

