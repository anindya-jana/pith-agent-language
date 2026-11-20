#!/usr/bin/env python3
"""Summarise handoff results: accuracy with 95% intervals, tokens, and paired
differences against the English and terse-English arms.

    python bench/harness/report.py bench/results/handoff/qwen3.5-9b [--hops 1] [--write]

Intervals are bootstrap over cases (2000 resamples, fixed seed). Paired
differences use only cases where both arms finished with status ok.
"""
import argparse
import json
import os
import random
import sys
from collections import defaultdict

ORDER = ["oracle", "english", "terse", "json", "pith_skill", "pith_primer",
         "pith_skill_1.1", "pith_primer_1.1", "null"]
METRICS = ["acc", "acc_status", "acc_constraint", "acc_detail", "acc_decoy"]


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def boot_ci(xs, reps=2000, seed=1):
    if len(xs) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    ms = sorted(mean([rng.choice(xs) for _ in xs]) for _ in range(reps))
    return ms[int(0.025 * reps)], ms[int(0.975 * reps) - 1]


def in_set(case_id, cases):
    """original = the seed-2026 cases (ids h000...); heldout = cases from any other seed."""
    return cases == "all" or (cases == "original") == case_id.startswith("h")


def load(path, hops, cases="original"):
    rows = []
    with open(os.path.join(path, "results.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["hops"] == hops and in_set(r["case"], cases):
                rows.append(r)
    errors = 0
    epath = os.path.join(path, "errors.jsonl")
    if os.path.exists(epath):
        with open(epath, encoding="utf-8") as f:
            for line in f:
                e = json.loads(line)
                errors += e["hops"] == hops and in_set(e["case"], cases)
    return rows, errors


def pct(x):
    return f"{x * 100:.1f}"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("path")
    p.add_argument("--hops", type=int, default=1)
    p.add_argument("--cases", default="original", choices=["original", "heldout", "all"],
                   help="original = seed-2026 cases, heldout = cases from any other seed")
    p.add_argument("--write", action="store_true", help="also write summary_h<hops>.md")
    args = p.parse_args()
    rows, n_errors = load(args.path, args.hops, args.cases)
    by_arm = defaultdict(dict)
    for r in rows:
        by_arm[r["arm"]][r["case"]] = r
    arms = [a for a in ORDER if a in by_arm] + sorted(a for a in by_arm if a not in ORDER)
    model = rows[0]["model"] if rows else "?"
    out = [f"# Handoff accuracy: {model}, hops={args.hops}", "",
           f"{len(rows)} graded runs, {n_errors} failed attempts logged in errors.jsonl. "
           "Accuracy in %, 95% bootstrap interval over cases. Tokens are the server's own counts.", "",
           "| arm | n | accuracy | status | constraint | detail | decoy | msg tokens | total tokens | reader prompt | notes |",
           "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for a in arms:
        rs = [r for r in by_arm[a].values()]
        ok = [r for r in rs if r["status"] == "ok"]
        acc = [r["grade"]["acc"] for r in ok]
        lo, hi = boot_ci(acc)
        cols = [pct(mean([r["grade"].get(m, float("nan")) for r in ok])) for m in METRICS[1:]]
        msg = [r["msg_tokens"] for r in ok if r["msg_tokens"] is not None]
        notes = []
        if len(ok) < len(rs):
            notes.append(f"{len(rs) - len(ok)} truncated")
        if any("lint_errors" in r for r in ok):
            clean = sum(1 for r in ok if r.get("lint_errors") == 0)
            notes.append(f"lint-clean {clean}/{len(ok)}")
        if any("json_valid" in r for r in ok):
            notes.append(f"valid JSON {sum(1 for r in ok if r.get('json_valid'))}/{len(ok)}")
        if any(r.get("reasoning_tokens") for r in ok):
            notes.append(f"reasoning {mean([r['reasoning_tokens'] for r in ok]):.0f} tok/run")
        out.append(f"| {a} | {len(ok)} | {pct(mean(acc))} ({pct(lo)}-{pct(hi)}) | " + " | ".join(cols)
                   + f" | {mean(msg):.0f} | {mean([r['total_tokens'] for r in ok]):.0f} | "
                   f"{mean([r['reader_prompt_tokens'] for r in ok]):.0f} | {'; '.join(notes)} |"
                   if msg else
                   f"| {a} | {len(ok)} | {pct(mean(acc))} ({pct(lo)}-{pct(hi)}) | " + " | ".join(cols)
                   + f" | - | {mean([r['total_tokens'] for r in ok]):.0f} | "
                   f"{mean([r['reader_prompt_tokens'] for r in ok]):.0f} | {'; '.join(notes)} |")

    for base in ("english", "terse"):
        if base not in by_arm:
            continue
        out += ["", f"## Paired against {base}", "",
                "| arm | pairs | accuracy diff (points) | msg tokens | total tokens |",
                "|---|---:|---|---:|---:|"]
        for a in arms:
            if a in (base, "oracle", "null") or a in CALIB:
                continue
            pairs = [(by_arm[base][c], by_arm[a][c]) for c in by_arm[a]
                     if c in by_arm[base] and by_arm[base][c]["status"] == "ok" and by_arm[a][c]["status"] == "ok"]
            if not pairs:
                continue
            d = [y["grade"]["acc"] - x["grade"]["acc"] for x, y in pairs]
            lo, hi = boot_ci(d)
            mt = (mean([y["msg_tokens"] for x, y in pairs]) / mean([x["msg_tokens"] for x, y in pairs]) - 1) * 100
            tt = (mean([y["total_tokens"] for x, y in pairs]) / mean([x["total_tokens"] for x, y in pairs]) - 1) * 100
            out.append(f"| {a} | {len(pairs)} | {mean(d) * 100:+.1f} ({lo * 100:+.1f} to {hi * 100:+.1f}) "
                       f"| {mt:+.0f}% | {tt:+.0f}% |")
    text = "\n".join(out)
    print(text)
    if args.write:
        suffix = "" if args.cases == "original" else "_" + args.cases
        with open(os.path.join(args.path, f"summary_h{args.hops}{suffix}.md"), "w", encoding="utf-8",
                  newline="\n") as f:
            f.write(text + "\n")
        export_messages(args.path, rows)


def export_messages(path, rows):
    """messages.jsonl: what each sender actually wrote, small enough to commit
    (the full traces repeat the skill text in every file)."""
    out = []
    for r in sorted(rows, key=lambda r: (r["case"], r["arm"])):
        tp = os.path.join(path, "traces", f"{r['case']}_{r['arm']}_h{r['hops']}.json")
        if not os.path.exists(tp):
            continue
        with open(tp, encoding="utf-8") as f:
            trace = json.load(f)
        sent = [t["content"] for t in trace if t["role"] == "assistant" and t.get("agent") in ("sender", "relay")]
        if sent:
            out.append({"case": r["case"], "kind": r["kind"], "arm": r["arm"], "hops": r["hops"],
                        "acc": r["grade"]["acc"], "messages": sent})
    with open(os.path.join(path, "messages.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for m in out:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")


CALIB = ("oracle", "null")

if __name__ == "__main__":
    main()
