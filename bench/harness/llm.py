"""Minimal client for an OpenAI-compatible chat endpoint (LM Studio by default).

Standard library only. Every call returns the text, any reasoning the server
split out, the server's own token usage, the model that served the request,
and timing, so the runner never has to estimate tokens.
"""
import json
import os
import random
import re
import threading
import time
import urllib.error
import urllib.request

DEFAULT_URL = os.environ.get("LLM_BASE_URL", "http://127.0.0.1:1234/v1")
API_KEY = os.environ.get("LLM_API_KEY", "")  # only for hosted endpoints; never written to results
MIN_INTERVAL = 0.0  # seconds between calls, for rate-limited free tiers
OPTIONAL_FIELDS = ("seed", "reasoning_effort")
UNSUPPORTED = set()  # optional fields this server has rejected
_last_call = [0.0]
_spacing = threading.Lock()


def set_api_key_file(path):
    """Read the key from a file outside the repo, so it never appears on a command line."""
    global API_KEY
    with open(os.path.expanduser(path), encoding="utf-8") as f:
        API_KEY = f.read().strip()
    if not API_KEY:
        raise ValueError(f"{path} is empty")


def _headers():
    h = {"Content-Type": "application/json"}
    if API_KEY:
        h["Authorization"] = "Bearer " + API_KEY
    return h


THINK = re.compile(r"<think>(.*?)</think>", re.S)


class LLMError(Exception):
    """A call that produced no usable output. `kind` is the failure class."""

    def __init__(self, kind, message, attempts=0):
        super().__init__(message)
        self.kind = kind
        self.attempts = attempts


def chat(messages, model, *, base_url=DEFAULT_URL, max_tokens=1500, seed=7,
         json_schema=None, timeout=600, retries=3, reasoning_effort=None):
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "seed": seed,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if reasoning_effort:
        body["reasoning_effort"] = reasoning_effort
    if json_schema is not None:
        body["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "answer", "strict": True, "schema": json_schema},
        }
    for field in UNSUPPORTED:
        body.pop(field, None)
    data = json.dumps(body).encode("utf-8")
    last = None
    for attempt in range(1, retries + 2):
        with _spacing:  # one call starts at a time, MIN_INTERVAL apart, across threads
            wait = MIN_INTERVAL - (time.monotonic() - _last_call[0])
            if wait > 0:
                time.sleep(wait)
            _last_call[0] = time.monotonic()
        start = time.monotonic()
        try:
            req = urllib.request.Request(
                base_url.rstrip("/") + "/chat/completions", data=data,
                headers=_headers())
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.load(resp)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:600]
            last = LLMError("http_%d" % e.code, detail, attempt)
            dropped = [f for f in OPTIONAL_FIELDS if f in body and re.search(r'\\?"%s\\?"' % f, detail)]
            if e.code == 400 and dropped:
                # The server rejects an optional field (Gemini has no `seed`): drop it for
                # every later call too, and retry at once.
                UNSUPPORTED.update(dropped)
                return chat(messages, model, base_url=base_url, max_tokens=max_tokens, seed=seed,
                            json_schema=json_schema, timeout=timeout, retries=retries,
                            reasoning_effort=reasoning_effort)
            if e.code not in (408, 409, 429) and e.code < 500:
                raise last
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = LLMError("connection", str(e), attempt)
        else:
            latency = time.monotonic() - start
            return _parse(payload, model, latency, attempt)
        time.sleep(min(60, 2 ** attempt) * (0.5 + random.random()))
    raise last


def _parse(payload, requested, latency, attempts):
    if "error" in payload:
        raise LLMError("server_error", str(payload["error"])[:300], attempts)
    choice = payload["choices"][0]
    msg = choice.get("message") or {}
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning_content") or msg.get("reasoning") or ""
    inline = THINK.findall(content)
    if inline:
        reasoning = (reasoning + "\n" + "\n".join(inline)).strip()
        content = THINK.sub("", content)
    content = content.strip()
    served = payload.get("model") or ""
    if served and _norm(served) != _norm(requested) and _norm(requested) not in _norm(served):
        raise LLMError("model_mismatch", f"asked {requested}, served {served}", attempts)
    usage = payload.get("usage") or {}
    if not usage.get("completion_tokens") and content:
        raise LLMError("missing_usage", "server returned no token usage", attempts)
    return {
        "content": content,
        "reasoning": reasoning,
        "finish_reason": choice.get("finish_reason"),
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens", 0),
        },
        "model": served or requested,
        "latency_s": round(latency, 3),
        "attempts": attempts,
    }


def _norm(name):
    return re.sub(r"[^a-z0-9.]", "", name.lower().split("/")[-1])


def list_models(base_url=DEFAULT_URL):
    req = urllib.request.Request(base_url.rstrip("/") + "/models", headers=_headers())
    with urllib.request.urlopen(req, timeout=10) as resp:
        return [m["id"].split("/", 1)[1] if m["id"].startswith("models/") else m["id"]
                for m in json.load(resp).get("data", [])]
