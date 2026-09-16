"""Interactive REPL — purple themed."""
import os, sys, time as _t

from . import ui, client, config as cfg, state as st
from .engine import jailbreak
from .onboard import add_provider_interactive


HELP = f"""\
  {ui.accent('/model')} [spec]      list or switch model
  {ui.accent('/provider')} [add]    list or add a provider
  {ui.accent('/strategy')} [name]   show or set strategy
  {ui.accent('/session')} [name]    show or switch session
  {ui.accent('/stats')}             win rates
  {ui.accent('/history')} [n]       recent runs
  {ui.accent('/keys')}              masked API keys
  {ui.accent('/clear')}             clear session memory
  {ui.accent('/help')}              this
  {ui.accent('/quit')}              exit
"""


def _resolve_env():
    r = cfg.resolve_active()
    if not r:
        return None
    os.environ["FORGE_BASE"] = r["base"]
    os.environ["FORGE_MODEL"] = r["model"]
    if r["key"]:
        os.environ["FORGE_KEY"] = r["key"]
    elif "FORGE_KEY" in os.environ:
        del os.environ["FORGE_KEY"]
    return r


def _print_models():
    c = cfg.load()
    active = c.get("active")
    if not c["providers"]:
        ui.bad("no providers — /provider add")
        return
    for pname, p in c["providers"].items():
        print(f"  {ui.hot(pname)}:")
        for m in p["models"]:
            marker = "  " + ui.hot("←") if f"{pname}:{m}" == active else ""
            print(f"    {m}{marker}")


def _stream(prompt: str) -> str:
    out = []
    for chunk in client.call_stream(prompt):
        sys.stdout.write(ui.soft(chunk))
        sys.stdout.flush()
        out.append(chunk)
    sys.stdout.write("\n")
    return "".join(out)


def run(session: str = None) -> None:
    c = cfg.load()
    if not c["providers"] or not c["active"]:
        print(ui.banner())
        ui.info("no config, running setup")
        add_provider_interactive()
        c = cfg.load()

    session = session or c.get("session", "default")
    strategy = c.get("strategy", "stream")

    r = _resolve_env()
    if not r:
        ui.bad("config broken — run: forge setup")
        return

    print(ui.banner())
    print(f"  {ui.hot('forge-rt')} {ui.dim('v0.1.0')}  "
          f"{ui.accent(r['provider'] + ':' + r['model'])}")
    print(f"  {ui.dim('/help for commands · ctrl-d to exit')}")
    print()

    while True:
        try:
            line = input(f"{ui.prompt_marker()} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not line:
            continue

        if line.startswith("/"):
            cmd, _, arg = line[1:].partition(" ")
            arg = arg.strip()

            if cmd in ("quit", "q"):
                break
            elif cmd == "help":
                print(HELP)
            elif cmd == "model":
                if not arg:
                    _print_models()
                else:
                    new = cfg.set_active(arg)
                    if new:
                        _resolve_env()
                        ui.good(f"switched to {ui.hot(new)}")
                    else:
                        ui.bad(f"no unique match for '{arg}' — use provider:model")
            elif cmd == "provider":
                if arg == "add":
                    add_provider_interactive(); _resolve_env()
                else:
                    cc = cfg.load()
                    if not cc["providers"]:
                        ui.info("none — '/provider add'")
                    for pname, p in cc["providers"].items():
                        print(f"  {ui.hot(pname):20s} key={ui.dim(cfg.masked_key(p.get('key','')))}  "
                              f"models={len(p.get('models',[]))}")
            elif cmd == "strategy":
                if not arg:
                    ui.info(f"strategy = {ui.hot(strategy)}")
                else:
                    strategy = arg
                    cc = cfg.load(); cc["strategy"] = arg; cfg.save(cc)
                    ui.good(f"strategy = {ui.hot(arg)}")
            elif cmd == "session":
                if arg:
                    session = arg
                    cc = cfg.load(); cc["session"] = arg; cfg.save(cc)
                ui.info(f"session = {ui.hot(session)}")
            elif cmd == "stats":
                rows = st.stats_table()
                if not rows:
                    ui.info("no runs yet")
                for m, s, w, p, b in rows:
                    print(f"  {m:35.35s} {ui.accent(s):10s} {w}/{p} best={b}")
            elif cmd == "history":
                n = int(arg) if arg.isdigit() else 10
                for ts, m, s, sc, pr in st.history(n):
                    when = _t.strftime("%H:%M:%S", _t.localtime(ts))
                    print(f"  {ui.dim(when)}  {m[:25]:25s} {ui.accent(s):10s} "
                          f"{ui.hot(str(sc)):>4s}  {pr}")
            elif cmd == "keys":
                cc = cfg.load()
                for pname, p in cc["providers"].items():
                    print(f"  {ui.hot(pname):20s} {ui.dim(cfg.masked_key(p.get('key','')))}")
            elif cmd == "clear":
                st.memory_append(session, "system", "(cleared)")
                ui.good("session memory cleared")
            else:
                ui.bad(f"unknown: /{cmd}")
            continue

        try:
            t0 = _t.time()
            if strategy == "stream":
                out = _stream(line)
            elif strategy == "static":
                wrapped = jailbreak(line, model=r["model"])
                out = _stream(wrapped)
            else:
                out = jailbreak(line, call=client.call, attacker_call=client.call,
                                model=r["model"], strategy=strategy)
                print(ui.soft(out))
            from .judges import score_response
            score = score_response(out)
            st.record_run(r["model"], line, strategy, out, score, _t.time() - t0)
            st.memory_append(session, "user", line)
            st.memory_append(session, "assistant", out)
            print(f"  {ui.dim('score=' + str(score))}")
        except Exception as e:
            ui.bad(str(e))
