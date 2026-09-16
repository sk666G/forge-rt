"""Model client — any chat-completions endpoint."""
import json, os, urllib.request, urllib.error
from typing import Iterator


def _base() -> str:
    return os.environ.get("FORGE_BASE", "http://localhost:11434/v1").rstrip("/")


def _key() -> str:
    return os.environ.get("FORGE_KEY", "")


def _model() -> str:
    return os.environ.get("FORGE_MODEL", "huihui_ai/qwen2.5-abliterate:14b")


def _timeout() -> int:
    return int(os.environ.get("FORGE_TIMEOUT", "1800"))


def _headers_and_url():
    base = _base()
    key = _key()
    if "anthropic.com" in base:
        h = {"Content-Type": "application/json",
             "anthropic-version": "2023-06-01"}
        if key:
            h["x-api-key"] = key
        return h, base + "/chat/completions"
    if "googleapis.com" in base:
        url = base + "/chat/completions"
        if key:
            url += f"?key={key}"
        return {"Content-Type": "application/json"}, url
    h = {"Content-Type": "application/json"}
    if key and key != "ollama":
        h["Authorization"] = f"Bearer {key}"
    return h, base + "/chat/completions"


def call(prompt: str, model: str = None, system: str = None) -> str:
    headers, url = _headers_and_url()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = json.dumps({
        "model": model or _model(),
        "messages": messages,
        "temperature": 0.7,
        "stream": False,
    }).encode()
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=_timeout()) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return f"[HTTP {e.code}] {e.read().decode()[:500]}"
    except Exception as e:
        return f"[error] {e}"
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return f"[bad response] {json.dumps(data)[:500]}"


def call_stream(prompt: str, model: str = None) -> Iterator[str]:
    headers, url = _headers_and_url()
    body = json.dumps({
        "model": model or _model(),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "stream": True,
    }).encode()
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=_timeout())
    except urllib.error.HTTPError as e:
        yield f"[HTTP {e.code}] {e.read().decode()[:500]}"
        return
    except Exception as e:
        yield f"[error] {e}"
        return
    for raw in resp:
        line = raw.decode().strip()
        if not line.startswith("data:"):
            continue
        chunk = line[5:].strip()
        if chunk == "[DONE]":
            break
        try:
            delta = json.loads(chunk)["choices"][0]["delta"].get("content", "")
        except Exception:
            continue
        if delta:
            yield delta


def list_models():
    base = _base()
    h, _ = _headers_and_url()
    url = base + "/models"
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
    except Exception as e:
        return [f"[error] {e}"]
    return [m.get("id", "?") for m in data.get("data", [])]
