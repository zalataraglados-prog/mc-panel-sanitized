import hashlib
import json
import os
import subprocess
import urllib.request


DEFAULT_RULES_BASE = "https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main"


def _cache_dir() -> str:
    base = os.environ.get("RULES_CACHE_DIR")
    if base:
        return base
    home = os.path.expanduser("~")
    return os.path.join(home, ".cache", "mc-panel-rules")


def _cache_path(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return os.path.join(_cache_dir(), f"{digest}.json")


def _write_cache(url: str, payload: str) -> None:
    path = _cache_path(url)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(payload)


def _read_cache(url: str) -> dict | None:
    path = _cache_path(url)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return None


def _fetch_json(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            if resp.status != 200:
                raise ValueError(f"HTTP {resp.status} for {url}")
            raw = resp.read().decode("utf-8")
        _write_cache(url, raw)
        return json.loads(raw)
    except Exception:
        cached = _read_cache(url)
        if cached is not None:
            return cached
        # Fallback to curl when available.
        try:
            result = subprocess.run(
                ["curl", "-fsSL", url],
                check=True,
                capture_output=True,
                text=True,
            )
            _write_cache(url, result.stdout)
            return json.loads(result.stdout)
        except FileNotFoundError as exc:
            raise RuntimeError("curl is not available and urllib fetch failed") from exc


def _fetch_optional_json(url: str) -> dict:
    try:
        return _fetch_json(url)
    except Exception:
        return {}


def _apply_rules_ref(base: str, rules_ref: str | None) -> str:
    if not rules_ref:
        return base
    if base.endswith("/main"):
        return base.rsplit("/", 1)[0] + f"/{rules_ref}"
    return base


def load_rules(
    version: str,
    *,
    base_url: str | None = None,
    rules_ref: str | None = None,
) -> tuple[dict, dict]:
    base = base_url or os.environ.get("RULES_BASE_URL", DEFAULT_RULES_BASE)
    base = _apply_rules_ref(base, rules_ref or os.environ.get("RULES_REF"))
    catalog_url = f"{base}/catalog/vanilla_{version}.json"
    taxonomy_url = f"{base}/taxonomy/vanilla_{version}.json"

    catalog = _fetch_json(catalog_url)
    taxonomy = _fetch_json(taxonomy_url)

    if not isinstance(catalog, dict) or not isinstance(taxonomy, dict):
        raise ValueError("Invalid rules payload")

    return catalog, taxonomy


def load_rules_bundle(
    version: str,
    *,
    base_url: str | None = None,
    rules_ref: str | None = None,
) -> dict:
    base = base_url or os.environ.get("RULES_BASE_URL", DEFAULT_RULES_BASE)
    base = _apply_rules_ref(base, rules_ref or os.environ.get("RULES_REF"))
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
