"""Interactive setup wizard — purple themed."""
import getpass, sys
from typing import List, Optional

from . import ui, config as cfg, client
from .providers import PROVIDERS, menu_order


def _ask(prompt: str, default: str = "") -> str:
    suffix = f" {ui.dim('[' + default + ']')}" if default else ""
    try:
        v = input(f"  {ui.accent('›')} {prompt}{suffix}: ").strip()
    except EOFError:
        print(); sys.exit(1)
    return v or default


def _ask_key(prompt: str = "Paste API key") -> str:
    try:
        return getpass.getpass(f"  {ui.accent('›')} {prompt} "
                               f"{ui.dim('(hidden)')}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print(); sys.exit(1)


def _pick(prompt: str, options: List[str], default: int = 1) -> int:
    for i, o in enumerate(options, 1):
        marker = "  " + ui.hot("←") if i == default else ""
        print(f"    {ui.dim(str(i).rjust(2))}) {o}{marker}")
    while True:
        raw = _ask(prompt, str(default))
        try:
            n = int(raw)
            if 1 <= n <= len(options):
                return n - 1
        except ValueError:
            pass
        ui.bad("pick a number in range")


def _probe_models(base: str, key: str) -> List[str]:
    import os
    old = {k: os.environ.get(k) for k in ("FORGE_BASE", "FORGE_KEY")}
    try:
        os.environ["FORGE_BASE"] = base
        if key:
            os.environ["FORGE_KEY"] = key
        elif "FORGE_KEY" in os.environ:
            del os.environ["FORGE_KEY"]
        return client.list_models()
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _test_call(base: str, key: str, model: str) -> bool:
    import os
    os.environ["FORGE_BASE"] = base
    if key:
        os.environ["FORGE_KEY"] = key
    os.environ["FORGE_MODEL"] = model
    try:
        out = client.call("Reply with exactly: ok")
        return len(out) > 0 and not out.startswith("[HTTP") and not out.startswith("[error")
    except Exception:
        return False


def add_provider_interactive(name: Optional[str] = None) -> None:
    order = menu_order()
    if name is None:
        print()
        print("  " + ui.bold(ui.accent("Provider")))
        labels = [PROVIDERS[k]["label"] for k in order]
        idx = _pick(ui.accent("›"), labels)
        name = order[idx]

    info = PROVIDERS.get(name)
    if not info:
        ui.bad(f"unknown provider: {name}"); return

    print()
    print(f"  {ui.hot('●')} {ui.bold(info['label'])}")

    base = info["base"]
    if not base:
        base = _ask("Base URL (e.g. https://api.example.com/v1)")

    key = ""
    if info.get("key_url"):
        print(f"  {ui.dim('get a key at')} {ui.soft(info['key_url'])}")
        key = _ask_key()
    else:
        print(f"  {ui.dim('(no key needed)')}")

    print(f"  {ui.dim('probing models…')}")
    detected = _probe_models(base, key)
    if detected and not detected[0].startswith("[error]"):
        ui.info(f"found {len(detected)} models")
        models = detected[:30]
    else:
        models = list(info["models"])

    if not models:
        custom = _ask("Model name (comma-separated)")
        models = [m.strip() for m in custom.split(",") if m.strip()]

    print()
    print("  " + ui.bold(ui.accent("Model")))
    models = models[:20]
    idx = _pick(ui.accent("›"), models)
    chosen = models[idx]

    print(f"  {ui.dim('testing call…')}")
    if _test_call(base, key, chosen):
        ui.good("ok")
    else:
        ui.warn_("test failed, saving anyway")

    cfg.add_provider(name, base, key, models)
    if not cfg.load()["active"]:
        cfg.set_active(f"{name}:{chosen}")

    print()
    ui.good(f"saved to {ui.soft(str(cfg.CONFIG_FILE))}")
    ui.info(f"active: {ui.hot(cfg.load()['active'] or '')}")


def run_setup() -> None:
    print(ui.banner())
    print("  " + ui.bold(ui.accent("setup")))
    add_provider_interactive()
    print()
    ui.info("run: " + ui.hot("forge"))
