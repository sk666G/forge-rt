"""Config: ~/.forge/config.json — providers, keys, active model, settings."""
import json, os, stat
from pathlib import Path
from typing import Any, Dict, List, Optional

CONFIG_DIR = Path(os.environ.get("FORGE_HOME", Path.home() / ".forge"))
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT = {
    "active": None,
    "strategy": "stream",
    "session": "default",
    "providers": {},
}


def load() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return dict(DEFAULT)
    try:
        with open(CONFIG_FILE) as f:
            data = json.load(f)
        for k, v in DEFAULT.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return dict(DEFAULT)


def save(cfg: Dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    try:
        os.chmod(CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)  # 0600
    except Exception:
        pass


def add_provider(name: str, base: str, key: str, models: List[str],
                 extra: Optional[Dict[str, str]] = None) -> None:
    cfg = load()
    cfg["providers"][name] = {
        "base": base.rstrip("/"),
        "key": key,
        "models": models,
        "extra": extra or {},
    }
    if not cfg["active"]:
        cfg["active"] = f"{name}:{models[0]}" if models else None
    save(cfg)


def remove_provider(name: str) -> bool:
    cfg = load()
    if name not in cfg["providers"]:
        return False
    del cfg["providers"][name]
    if cfg["active"] and cfg["active"].startswith(f"{name}:"):
        remaining = list(cfg["providers"].items())
        cfg["active"] = (f"{remaining[0][0]}:{remaining[0][1]['models'][0]}"
                         if remaining and remaining[0][1].get("models") else None)
    save(cfg)
    return True


def set_active(spec: str) -> Optional[str]:
    """spec = 'provider:model' or bare 'model' for unique match."""
    cfg = load()
    if ":" in spec:
        provider, model = spec.split(":", 1)
        if provider in cfg["providers"]:
            p = cfg["providers"][provider]
            if model not in p["models"]:
                p["models"].append(model)
            cfg["active"] = f"{provider}:{model}"
            save(cfg)
            return cfg["active"]
        return None
    matches = []
    for pname, p in cfg["providers"].items():
        for m in p["models"]:
            if m == spec or m.endswith(f"/{spec}") or m.endswith(f"-{spec}"):
                matches.append(f"{pname}:{m}")
    if len(matches) == 1:
        cfg["active"] = matches[0]
        save(cfg)
        return matches[0]
    return None


def resolve_active() -> Optional[Dict[str, str]]:
    """Return {'provider','model','base','key','extra'} for the active model."""
    cfg = load()
    if not cfg["active"]:
        return None
    provider, model = cfg["active"].split(":", 1)
    p = cfg["providers"].get(provider)
    if not p:
        return None
    return {
        "provider": provider,
        "model": model,
        "base": p["base"],
        "key": p.get("key", ""),
        "extra": p.get("extra", {}),
    }


def masked_key(key: str) -> str:
    if not key:
        return "(none)"
    if len(key) <= 12:
        return "*" * len(key)
    return key[:8] + "…" + key[-4:]
