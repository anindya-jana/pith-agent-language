#!/usr/bin/env python3
"""Run the handoff-accuracy suite against a local OpenAI-compatible server.

    python bench/harness/run.py --model qwen3.5-9b --n 20
    python bench/harness/run.py --model qwen3.5-9b --n 60 --arms english,terse,pith_skill --hops 3
    python bench/harness/run.py --selftest            grader checks, no model calls

Each (case, arm, hops) writes one row to results.jsonl as soon as it finishes,
so a crash loses nothing and a rerun skips what is done. Attempts that never
produced a gradable answer go to errors.jsonl and are retried on the next run.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "pith", "scripts"))

import suite_handoff as suite  # noqa: E402
import llm  # noqa: E402
from llm import DEFAULT_URL, LLMError, chat, list_models  # noqa: E402
from pith import lint  # noqa: E402
from protocols import ARMS, CALIBRATION, system_prompt  # noqa: E402

ALL_ARMS = list(ARMS) + list(CALIBRATION)
DEFAULT_ARMS = ["english", "terse", "json", "pith_skill", "pith_primer", "oracle", "null"]


def slug(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


def acquire_lock(path):
    """Hold an OS file lock for this results directory. The OS frees it when
    the process exits, so a crash never leaves a stale lock behind."""
    f = open(path, "a+")
    f.seek(0)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return None
    return f


def load_done(path):
    done = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                done.add((r["case"], r["arm"], r["hops"]))
    return done


def append(path, row):
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def extract_json(text):
    """For servers without schema support: take the outermost {...} in the reply."""
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no JSON object")
    return json.loads(text[start:end + 1])


FENCE = re.compile(r"^\s*```[\w-]*\n(.*?)\n```\s*$", re.S)


def unfence(text):
    """Models often wrap the whole message in a code fence; check what is inside."""
    m = FENCE.match(text)
    return m.group(1) if m else text


def run_case(case, arm, hops, model, args):
    trace, calls = [], []
    reader_model = args.reader_model or model

    def call(role, system, user, **kw):
        trace.append({"role": "system", "content": system, "agent": role})
        trace.append({"role": "user", "content": user, "agent": role})
        out = chat([{"role": "system", "content": system}, {"role": "user", "content": user}],
                   reader_model if role == "reader" else model,
                   base_url=args.base_url, timeout=args.timeout,
                   reasoning_effort=args.reasoning_effort or None, **kw)
        trace.append({"role": "assistant", "content": out["content"], "thinking": out["reasoning"],
                      "agent": role, "usage": out["usage"], "finish_reason": out["finish_reason"]})
        calls.append({"role": role, **out["usage"], "latency_s": out["latency_s"],
                      "finish_reason": out["finish_reason"], "model": out["model"],
                      "attempts": out["attempts"]})
        return out

    status = "ok"
    msg_tokens = []
    if arm == "oracle":
        message = case["notes"]
    elif arm == "null":
        message = ""
    else:
        out = call("sender", system_prompt("sender", arm), case["notes"] + "\n\n" + case["task"],
                   max_tokens=args.max_msg_tokens)
        message = out["content"]
        msg_tokens.append(out["usage"]["completion_tokens"] - out["usage"]["reasoning_tokens"])
        if out["finish_reason"] == "length":
            status = "truncated"
        for _ in range(hops - 1):
            out = call("relay", system_prompt("relay", arm),
                       "Message you received:\n\n" + message + "\n\nWrite the message for the next agent.",
                       max_tokens=args.max_msg_tokens)
            message = out["content"]
            msg_tokens.append(out["usage"]["completion_tokens"] - out["usage"]["reasoning_tokens"])
            if out["finish_reason"] == "length":
                status = "truncated"

    reader_arm = arm if arm in ARMS else "english"
    prompt = ("Message:\n<<<\n" + message + "\n>>>\n\nQuestions:\n" + suite.render_questions(case["questions"])
              + "\n\nAnswer every question with the letter of exactly one option, as JSON.")
    out = call("reader", system_prompt("reader", reader_arm), prompt,
               max_tokens=args.max_answer_tokens,
               json_schema=None if args.no_schema else suite.answer_schema(case["questions"]))
    try:
        answers = extract_json(out["content"]) if args.no_schema else json.loads(out["content"])
        if not isinstance(answers, dict):
            raise ValueError("not an object")
    except (ValueError, json.JSONDecodeError):
        raise LLMError("bad_answer", out["content"][:200])
    score, per_q = suite.grade(case["questions"], answers)

    row = {
        "case": case["id"], "kind": case["kind"], "arm": arm, "hops": hops, "model": model,
        "reader_model": reader_model,
        "served_model": calls[-1]["model"], "status": status, "grade": score, "per_q": per_q,
        "msg_tokens": msg_tokens[-1] if msg_tokens else None, "msg_tokens_hops": msg_tokens,
        "msg_chars": len(message),
        "prompt_tokens": sum(c["prompt_tokens"] for c in calls),
        "completion_tokens": sum(c["completion_tokens"] for c in calls),
        "reasoning_tokens": sum(c["reasoning_tokens"] for c in calls),
        "reader_prompt_tokens": calls[-1]["prompt_tokens"],
        "latency_s": round(sum(c["latency_s"] for c in calls), 2),
        "attempts": sum(c["attempts"] for c in calls),
        "calls": calls,
    }
    row["total_tokens"] = row["prompt_tokens"] + row["completion_tokens"]
    if arm.startswith("pith"):
        issues = lint(unfence(message))
        row["lint_errors"] = sum(1 for i in issues if i[1] == "E")
        row["lint_warnings"] = sum(1 for i in issues if i[1] == "W")
    if arm == "json":
        try:
            json.loads(unfence(message))
            row["json_valid"] = True
        except json.JSONDecodeError:
            row["json_valid"] = False
    return row, trace


def selftest(n):
    cases = suite.make_cases(n)
    letters = "ABCDEFG"
    totals = {"oracle": [], "empty": [], "always_not_stated": [], "always_A": []}
    for c in cases:
        qs = c["questions"]
        totals["oracle"].append(suite.grade(qs, {q["id"]: letters[q["gold"]] for q in qs})[0]["acc"])
        totals["empty"].append(suite.grade(qs, {})[0]["acc"])
        ns = {q["id"]: letters[len(q["options"]) - 1] for q in qs}
        totals["always_not_stated"].append(suite.grade(qs, ns)[0]["acc"])
        totals["always_A"].append(suite.grade(qs, {q["id"]: "A" for q in qs})[0]["acc"])
    chance = sum(sum(1 / len(q["options"]) for q in c["questions"]) / len(c["questions"]) for c in cases) / n
    for k, v in totals.items():
        print(f"{k:18} mean acc {sum(v) / len(v):.3f}")
    print(f"{'random guessing':18} mean acc {chance:.3f}")
    ok = all(a == 1.0 for a in totals["oracle"]) and all(a == 0.0 for a in totals["empty"])
    print("selftest", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", help="model id as the server lists it; writes every message")
    p.add_argument("--reader-model", help="different model for the reader (default: same as --model)")
    p.add_argument("--no-schema", action="store_true",
                   help="server lacks JSON-schema output: ask for JSON in the prompt and extract it")
    p.add_argument("--n", type=int, default=20, help="number of cases")
    p.add_argument("--start", type=int, default=0, help="first case index")
    p.add_argument("--arms", default=",".join(DEFAULT_ARMS),
                   help="comma-separated; all: " + ",".join(ALL_ARMS))
    p.add_argument("--hops", type=int, default=1, help="1 = sender to reader; 3 = two relays in between")
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--base-url", default=DEFAULT_URL)
    p.add_argument("--api-key-file", help="file holding the API key for a hosted endpoint (kept out of the repo)")
    p.add_argument("--min-interval", type=float, default=0.0,
                   help="seconds to wait between calls, for rate-limited free tiers")
    p.add_argument("--timeout", type=int, default=600, help="per-call wall-clock ceiling, seconds")
    p.add_argument("--reasoning-effort", default="none",
                   help="sent as reasoning_effort; 'none' turns thinking off on LM Studio. Pass '' to omit")
    p.add_argument("--max-msg-tokens", type=int, default=1500)
    p.add_argument("--max-answer-tokens", type=int, default=600)
    p.add_argument("--out", default=os.path.join(ROOT, "bench", "results", "handoff"))
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        return selftest(args.n)
    if not args.model:
        p.error("--model is required")
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    unknown = [a for a in arms if a not in ALL_ARMS]
    if unknown:
        p.error(f"unknown arms: {unknown}")
    try:
        if args.api_key_file:
            llm.set_api_key_file(args.api_key_file)
        llm.MIN_INTERVAL = args.min_interval
        available = list_models(args.base_url)
    except OSError as e:
        print(f"cannot reach {args.base_url}: {e}")
        return 2
    for m in filter(None, (args.model, args.reader_model)):
        if m not in available:
            print(f"model {m!r} not loaded; server has: {available}")
            return 2

    name = args.model if not args.reader_model else f"{args.model}__to__{args.reader_model}"
    out_dir = os.path.join(args.out, slug(name))
    os.makedirs(os.path.join(out_dir, "traces"), exist_ok=True)
    results, errors = os.path.join(out_dir, "results.jsonl"), os.path.join(out_dir, "errors.jsonl")
    lock = acquire_lock(os.path.join(out_dir, ".lock"))
    if lock is None:
        print(f"another run is already writing to {out_dir}; not starting a second one")
        return 3
    done = load_done(results)
    cases = suite.make_cases(args.start + args.n, seed=args.seed)[args.start:]
    todo = [(c, a) for c in cases for a in arms if (c["id"], a, args.hops) not in done]
    print(f"{len(todo)} runs to do ({len(cases)} cases x {len(arms)} arms, hops={args.hops}); "
          f"{len(cases) * len(arms) - len(todo)} already done")
    t0 = time.monotonic()
    for i, (case, arm) in enumerate(todo, 1):
        try:
            row, trace = run_case(case, arm, args.hops, args.model, args)
        except LLMError as e:
            append(errors, {"case": case["id"], "arm": arm, "hops": args.hops, "model": args.model,
                            "kind": e.kind, "error": str(e)[:300], "attempts": e.attempts,
                            "time": time.strftime("%Y-%m-%dT%H:%M:%S")})
            print(f"[{i}/{len(todo)}] {case['id']} {arm}: ERROR {e.kind}")
            continue
        with open(os.path.join(out_dir, "traces", f"{case['id']}_{arm}_h{args.hops}.json"), "w",
                  encoding="utf-8", newline="\n") as f:
            json.dump(trace, f, ensure_ascii=False, indent=1)
        append(results, row)
        rate = (time.monotonic() - t0) / i
        print(f"[{i}/{len(todo)}] {case['id']} {arm:12} acc={row['grade']['acc']:.2f} "
              f"msg={row['msg_tokens']} total={row['total_tokens']} {row['status']} "
              f"eta {rate * (len(todo) - i) / 60:.0f} min", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
