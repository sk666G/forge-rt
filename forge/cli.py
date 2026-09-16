"""forge CLI."""
import argparse, sys, time

from . import client, state as st
from .engine import jailbreak
from .strategies import load_arsenal


def _out_stream(prompt):
    for chunk in client.call_stream(prompt):
        sys.stdout.write(chunk)
        sys.stdout.flush()
    sys.stdout.write("\n")


def cmd_ask(a):
    prompt = " ".join(a.prompt)
    if a.strategy in ("static", "stream"):
        wrapped = (jailbreak(prompt, model=client._model()) if a.strategy == "static" else prompt)
        t0 = time.time()
        out = []
        for chunk in client.call_stream(wrapped):
            sys.stdout.write(chunk); sys.stdout.flush()
            out.append(chunk)
        sys.stdout.write("\n")
        full = "".join(out)
        from .judges import score_response
        s = score_response(full)
        st.record_run(client._model(), prompt, a.strategy, full, s, time.time() - t0)
        print(f"\n[score={s}]", file=sys.stderr)
    else:
        out = jailbreak(prompt, call=client.call, attacker_call=client.call,
                        model=client._model(), strategy=a.strategy)
        print(out)


def cmd_raw(a):
    prompt = " ".join(a.prompt)
    _out_stream(prompt)


def cmd_models(a):
    for m in client.list_models():
        print(m)


def cmd_arsenal(a):
    arsenal = load_arsenal()
    if a.show is not None:
        import json
        print(json.dumps(arsenal[a.show], indent=2))
        return
    for i, t in enumerate(arsenal):
        print(f"{i:3d}  {t.get('name','?')[:55]:55s}  "
              f"eff={t.get('effectiveness','?')}")


def cmd_stats(a):
    rows = st.stats_table()
    if not rows:
        print("no runs yet")
        return
    print(f"{'model':35.35s} {'strategy':10s} {'winrate':>8s} {'best':>5s}")
    for m, s, w, p, b in rows:
        print(f"{m:35.35s} {s:10s} {w}/{p:<3d} {100*w/max(1,p):5.1f}% {b:5d}")


def cmd_history(a):
    for ts, m, s, sc, pr in st.history(a.n):
        print(f"{time.strftime('%H:%M:%S', time.localtime(ts))}  "
              f"{m[:25]:25s} {s:10s} score={sc:3d}  {pr}")


def cmd_db(a):
    if a.reset:
        st.reset()
        print("state reset")


def cmd_chat(a):
    session = a.session or "default"
    print(f"[forge chat] session={session}  ctrl-d to exit", file=sys.stderr)
    while True:
        try:
            q = input("> ")
        except EOFError:
            print()
            break
        if not q.strip():
            continue
        sys.stdout.write("[forge] ")
        _out_stream(q)


def cmd_web(a):
    from .server import serve
    serve(a.port)


def main():
    p = argparse.ArgumentParser(prog="forge")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("ask")
    a.add_argument("prompt", nargs="+")
    a.add_argument("--strategy", "-s", default="static",
                   choices=["static", "stream", "adaptive", "bpj",
                            "pair", "tap", "crescendo"])
    a.set_defaults(fn=cmd_ask)

    r = sub.add_parser("raw")
    r.add_argument("prompt", nargs="+")
    r.set_defaults(fn=cmd_raw)

    m = sub.add_parser("models")
    m.set_defaults(fn=cmd_models)

    ar = sub.add_parser("arsenal")
    ar.add_argument("--show", type=int, default=None)
    ar.set_defaults(fn=cmd_arsenal)

    s = sub.add_parser("stats")
    s.set_defaults(fn=cmd_stats)

    h = sub.add_parser("history")
    h.add_argument("-n", type=int, default=20)
    h.set_defaults(fn=cmd_history)

    d = sub.add_parser("db")
    d.add_argument("--reset", action="store_true")
    d.set_defaults(fn=cmd_db)

    c = sub.add_parser("chat")
    c.add_argument("--session", default="default")
    c.set_defaults(fn=cmd_chat)

    w = sub.add_parser("web")
    w.add_argument("--port", type=int, default=8765)
    w.set_defaults(fn=cmd_web)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
