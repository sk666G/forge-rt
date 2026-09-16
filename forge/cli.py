"""forge CLI."""
import argparse, sys, time

from . import ui, client, config as cfg, state as st
from .engine import jailbreak
from .strategies import load_arsenal


def _out_stream(prompt):
    out = []
    for chunk in client.call_stream(prompt):
        sys.stdout.write(chunk); sys.stdout.flush()
        out.append(chunk)
    sys.stdout.write("\n")
    return "".join(out)


def _resolve_env():
    import os
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


def cmd_ask(a):
    if not _resolve_env():
        print("no config — run: forge setup", file=sys.stderr); sys.exit(1)
    prompt = " ".join(a.prompt)
    if a.strategy in ("static", "stream"):
        wrapped = (jailbreak(prompt, model=client._model())
                   if a.strategy == "static" else prompt)
        t0 = time.time()
        full = _out_stream(wrapped)
        from .judges import score_response
        st.record_run(client._model(), prompt, a.strategy, full,
                      score_response(full), time.time() - t0)
    else:
        out = jailbreak(prompt, call=client.call, attacker_call=client.call,
                        model=client._model(), strategy=a.strategy)
        print(out)


def cmd_raw(a):
    if not _resolve_env():
        print("no config — run: forge setup", file=sys.stderr); sys.exit(1)
    _out_stream(" ".join(a.prompt))


def cmd_models(a):
    if not _resolve_env():
        print("no config — run: forge setup", file=sys.stderr); sys.exit(1)
    for m in client.list_models():
        print(m)


def cmd_arsenal(a):
    arsenal = load_arsenal()
    if a.show is not None:
        import json
        print(json.dumps(arsenal[a.show], indent=2)); return
    for i, t in enumerate(arsenal):
        print(f"{i:3d}  {t.get('name','?')[:55]:55s}  eff={t.get('effectiveness','?')}")


def cmd_stats(a):
    rows = st.stats_table()
    if not rows:
        print("no runs yet"); return
    for m, s, w, p, b in rows:
        print(f"  {ui.hot(m):35s} {ui.accent(s):10s} "
              f"{w}/{p:<3d} {ui.dim(str(round(100*w/max(1,p),1)) + '%')} "
              f"best={ui.hot(str(b))}")


def cmd_history(a):
    for ts, m, s, sc, pr in st.history(a.n):
        print(f"{time.strftime('%H:%M:%S', time.localtime(ts))}  "
              f"{m[:25]:25s} {s:10s} score={sc:3d}  {pr}")


def cmd_db(a):
    if a.reset:
        st.reset(); print("state reset")


def cmd_setup(a):
    from .onboard import run_setup
    run_setup()


def cmd_provider(a):
    from .onboard import add_provider_interactive
    if a.action == "add":
        add_provider_interactive(a.name)
    elif a.action == "list":
        c = cfg.load()
        if not c["providers"]:
            print("none configured"); return
        for pname, p in c["providers"].items():
            print(f"{pname:12s} key={cfg.masked_key(p.get('key',''))} "
                  f"models={len(p.get('models',[]))}")
    elif a.action == "rm":
        if cfg.remove_provider(a.name):
            print(f"removed {a.name}")
        else:
            print(f"no such provider: {a.name}")


def cmd_model(a):
    if a.action == "list":
        c = cfg.load()
        active = c.get("active")
        for pname, p in c["providers"].items():
            for m in p["models"]:
                mark = "  ←" if f"{pname}:{m}" == active else ""
                print(f"{pname}:{m}{mark}")
    elif a.action == "use":
        new = cfg.set_active(a.spec)
        if new:
            print(f"active: {new}")
        else:
            print(f"no match for {a.spec}"); sys.exit(1)
    elif a.action == "add":
        c = cfg.load()
        p = c["providers"].get(a.provider)
        if not p:
            print(f"unknown provider: {a.provider}"); sys.exit(1)
        if a.model not in p["models"]:
            p["models"].append(a.model)
            cfg.save(c)
        print(f"added {a.provider}:{a.model}")


def cmd_chat(a):
    from .repl import run as repl_run
    repl_run(session=a.session)


def cmd_web(a):
    if not _resolve_env():
        print("no config — run: forge setup", file=sys.stderr); sys.exit(1)
    from .server import serve
    serve(a.port)


def main():
    p = argparse.ArgumentParser(prog="forge")
    sub = p.add_subparsers(dest="cmd")

    a = sub.add_parser("ask")
    a.add_argument("prompt", nargs="+")
    a.add_argument("--strategy", "-s", default=None,
                   choices=["static", "stream", "adaptive", "bpj",
                            "pair", "tap", "crescendo"])
    a.set_defaults(fn=cmd_ask)

    r = sub.add_parser("raw"); r.add_argument("prompt", nargs="+"); r.set_defaults(fn=cmd_raw)
    m = sub.add_parser("models"); m.set_defaults(fn=cmd_models)
    ar = sub.add_parser("arsenal"); ar.add_argument("--show", type=int, default=None); ar.set_defaults(fn=cmd_arsenal)
    s = sub.add_parser("stats"); s.set_defaults(fn=cmd_stats)
    h = sub.add_parser("history"); h.add_argument("-n", type=int, default=20); h.set_defaults(fn=cmd_history)
    d = sub.add_parser("db"); d.add_argument("--reset", action="store_true"); d.set_defaults(fn=cmd_db)
    su = sub.add_parser("setup"); su.set_defaults(fn=cmd_setup)

    pr = sub.add_parser("provider")
    pr.add_argument("action", choices=["add", "list", "rm"])
    pr.add_argument("name", nargs="?", default=None)
    pr.set_defaults(fn=cmd_provider)

    mo = sub.add_parser("model")
    mo.add_argument("action", choices=["list", "use", "add"])
    mo.add_argument("spec", nargs="?", default=None)
    mo.add_argument("model", nargs="?", default=None)
    mo.add_argument("--provider", dest="provider", default=None)
    mo.set_defaults(fn=cmd_model)

    ch = sub.add_parser("chat"); ch.add_argument("--session", default=None); ch.set_defaults(fn=cmd_chat)
    w = sub.add_parser("web"); w.add_argument("--port", type=int, default=8765); w.set_defaults(fn=cmd_web)

    args = p.parse_args()

    # no subcommand -> REPL
    if not args.cmd:
        cmd_chat(argparse.Namespace(session=None))
        return

    # resolve strategy: cli flag > config
    if args.cmd == "ask" and args.strategy is None:
        args.strategy = cfg.load().get("strategy", "stream")

    # model subcommand uses 'spec' as provider when action == add
    if args.cmd == "model" and args.action == "add":
        args.provider = args.spec

    args.fn(args)


if __name__ == "__main__":
    main()
