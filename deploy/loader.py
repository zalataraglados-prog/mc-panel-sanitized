import json
import os
import subprocess
import urllib.request


DEFAULT_RULES_BASE = "https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main"


def _fetch_json(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            if resp.status != 200:
                raise ValueError(f"HTTP {resp.status} for {url}")
            raw = resp.read().decode("utf-8")
        return json.loads(raw)
    except Exception:
        # Fallback to curl when available.
        try:
            result = subprocess.run(
                ["curl", "-fsSL", url],
                check=True,
                capture_output=True,
                text=True,
            )
            return json.loads(result.stdout)
        except FileNotFoundError as exc:
            raise RuntimeError("curl is not available and urllib fetch failed") from exc


def _fetch_optional_json(url: str) -> dict:
    try:
        return _fetch_json(url)
    except Exception:
        return {}


def load_rules(version: str, *, base_url: str | None = None) -> tuple[dict, dict]:
    base = base_url or os.environ.get("RULES_BASE_URL", DEFAULT_RULES_BASE)
    catalog_url = f"{base}/catalog/vanilla_{version}.json"
    taxonomy_url = f"{base}/taxonomy/vanilla_{version}.json"

    catalog = _fetch_json(catalog_url)
    taxonomy = _fetch_json(taxonomy_url)

    if not isinstance(catalog, dict) or not isinstance(taxonomy, dict):
        raise ValueError("Invalid rules payload")

    return catalog, taxonomy


def load_rules_bundle(version: str, *, base_url: str | None = None) -> dict:
    base = base_url or os.environ.get("RULES_BASE_URL", DEFAULT_RULES_BASE)
    catalog_url = f"{base}/catalog/vanilla_{version}.json"
    taxonomy_url = f"{base}/taxonomy/vanilla_{version}.json"
    usability_url = f"{base}/usability/vanilla_{version}.json"

    catalog = _fetch_json(catalog_url)
    taxonomy = _fetch_json(taxonomy_url)
    usability = _fetch_optional_json(usability_url)

    if not isinstance(catalog, dict) or not isinstance(taxonomy, dict):
        raise ValueError("Invalid rules payload")
    if not isinstance(usability, dict):
        usability = {}

    return {
        "catalog": catalog,
        "taxonomy": taxonomy,
        "usability": usability,
    }
