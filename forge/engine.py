"""Orchestrator — jailbreak() runs enabled strategies, picks best."""
import time
from typing import Callable, Optional

from . import state as st
from .judges import score_response, multi_judge_score
from .strategies import (load_arsenal, static_attempt, bpj_attempt,
                         pair_attempt, tap_attempt, crescendo_attempt)


def jailbreak(
    prompt: str,
    *,
    call: Optional[Callable[[str], str]] = None,
    model: str = "user-choice",
    strategy: str = "adaptive",
    attacker_call: Optional[Callable[[str], str]] = None,
    session_id: str = "default",
    record: bool = True,
) -> str:
    arsenal = load_arsenal()
    if call is None:
        return static_attempt(prompt, model, arsenal)[2]

    t0 = time.time()
    results = []

    r, s, _ = static_attempt(prompt, model, arsenal, call)
    results.append((r, s, "static"))

    if strategy in ("adaptive", "bpj"):
        r, s = bpj_attempt(prompt, call)
        results.append((r, s, "bpj"))

    if strategy in ("adaptive", "pair"):
        r, s = pair_attempt(prompt, call, attacker_call=attacker_call)
        results.append((r, s, "pair"))

    if strategy in ("adaptive", "tap"):
        r, s = tap_attempt(prompt, call, attacker_call=attacker_call)
        results.append((r, s, "tap"))

    if strategy in ("adaptive", "crescendo"):
        r, s = crescendo_attempt(prompt, call, session_id=session_id)
        results.append((r, s, "crescendo"))

    best_r, best_s, best_name = "", -1, ""
    for r, s, name in results:
        mj = multi_judge_score(r)
        combined = s * 0.5 + mj * 50
        if combined > best_s:
            best_s, best_r, best_name = combined, r, name

    if record:
        st.record_run(model, prompt, best_name,
                      best_r, int(best_s), time.time() - t0)

    return best_r or static_attempt(prompt, model, arsenal)[2]


jailbreak_prompt = jailbreak
