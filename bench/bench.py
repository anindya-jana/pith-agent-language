#!/usr/bin/env python3
"""Count tokens for the corpus in each encoding and lint every Pith sample.

    python bench/bench.py            print the table
    python bench/bench.py --write    also write bench/results.md

Tokenizers are OpenAI's o200k_base and cl100k_base (via tiktoken). They are a
proxy: Claude's tokenizer gives different absolute counts.
"""
import os
import sys

import tiktoken

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "pith", "scripts"))

from corpus import SCENARIOS  # noqa: E402
from pith import PRIMER, lint  # noqa: E402

FORMS = ("english", "terse", "json", "pith")
ENCODINGS = ("o200k_base", "cl100k_base")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = []
    lint_errors = 0
    for s in SCENARIOS:
        for n, level, code, msg in lint("\n".join(s["pith"])):
            print(f"lint {s['name']}:{n}: {code} {msg}")
            lint_errors += level == "E"

    for enc_name in ENCODINGS:
        enc = tiktoken.get_encoding(enc_name)
        count = lambda msgs: sum(len(enc.encode(m)) for m in msgs)  # noqa: E731
        out.append(f"### {enc_name}\n")
        out.append("| scenario | english | terse | json | pith | vs english | vs terse | vs json |")
        out.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        totals = dict.fromkeys(FORMS, 0)
        for s in SCENARIOS:
            c = {f: count(s[f]) for f in FORMS}
            for f in FORMS:
                totals[f] += c[f]
            out.append(row(s["name"], c))
        out.append(row("**total**", totals))
        out.append("")
        out.append(f"First-contact primer: {len(enc.encode(PRIMER))} tokens, sent once per peer.\n")

    text = "\n".join(out)
    print(text)
    print(f"lint errors in pith samples: {lint_errors}")
    if "--write" in sys.argv:
        head = ("# Pith 1 benchmark\n\n"
                "Token counts for eight inter-agent exchanges (14 messages), each written four ways "
                "with the same facts. Source: `bench/corpus.py`. Regenerate: `python bench/bench.py --write`.\n\n"
                "Negative percentages mean Pith used fewer tokens. The tokenizers are OpenAI's, used as a "
                "proxy; Claude's tokenizer gives different absolute numbers. This measures size only, "
                "not how accurately a receiver decodes the message.\n\n")
        with open(os.path.join(HERE, "results.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(head + text + "\n")
    return 1 if lint_errors else 0


def row(name, c):
    pct = lambda base: f"{(c['pith'] - c[base]) / c[base] * 100:+.0f}%"  # noqa: E731
    return (f"| {name} | {c['english']} | {c['terse']} | {c['json']} | {c['pith']} "
            f"| {pct('english')} | {pct('terse')} | {pct('json')} |")


if __name__ == "__main__":
    sys.exit(main())
