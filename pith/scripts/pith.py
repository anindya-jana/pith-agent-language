#!/usr/bin/env python3
"""Pith 1 toolkit: lint messages, count tokens, print the first-contact primer.

Usage:
  python pith.py lint [FILE ...]          check Pith text (reads stdin if no file)
  python pith.py lint --md FILE ...       check every ```pith block in markdown files
  python pith.py lint --known db,job ...  treat these handles as already defined
  python pith.py count [FILE ...]         token count (tiktoken if installed, else estimate)
  python pith.py primer                   print the primer to send to a peer without the skill

Exit code is 1 when lint finds an error. Warnings do not change the exit code.
Standard library only; tiktoken is optional and used only by `count`.
"""
import argparse
import math
import re
import sys

ACTS = ("do", "ask", "stop", "fact", "think", "guess",
        "ok", "no", "done", "part", "err", "need", "plan")
SLOTS = ("why", "at", "with", "must", "not", "prefer", "allow", "out",
         "check", "cap", "did", "left", "next", "tab")
OLD_SLOTS = {"should": "prefer", "may": "allow"}  # Pith 1.0 names, still accepted
PRONOUNS = {"it", "its", "this", "that", "these", "those", "they", "them",
            "their", "he", "she", "him", "her", "his"}
FILLER = {"the", "a", "an", "please", "just", "really", "very", "basically",
          "actually", "simply", "kindly"}

PRIMER = (
    "pith 1. Each line starts with an act: do ask stop fact think guess ok no done part err "
    "need plan. fact = verified by sender, source after <-. think, guess = sender's belief, "
    "not verified. A line indented 1 space is a slot of the line above: why at with | must "
    "(required) not (forbidden) prefer (optional) allow (permitted) | out check cap | did left "
    "next. In reports: did not <x> = rule kept; left = not done. Commands in ``, errors in \"\" "
    "are exact. $x = defined name, #n = statement id, -> yields, ? = unknown. Reply in pith."
)

STMT = re.compile(r"^(?:#(\w+) )?([a-z]+)(?: (.*))?$")
DEFN = re.compile(r"^\$([a-z][a-z0-9_]*) = (.+)$")
HANDLE = re.compile(r"\$([a-z][a-z0-9_]*)")
VERBATIM = re.compile(r"`[^`]*`|\"[^\"]*\"")
WORD = re.compile(r"(?<![\w./-])[A-Za-z']+(?![\w./-])")
HEADER = re.compile(r"^pith \d+$")


def mask(text):
    """Blank out verbatim spans so their contents are never read as Pith."""
    return VERBATIM.sub("V", text)


def lint(text, known=()):
    """Return a list of (line_number, level, code, message). Level is 'E' or 'W'."""
    issues = []
    defined = set(known)
    ids = set()
    cur = None
    in_fence = False

    def add(n, level, code, msg):
        issues.append((n, level, code, msg))

    def check_words(n, content):
        m = mask(content)
        if not m.isascii():
            add(n, "E", "E11", "non-ASCII outside verbatim; use ASCII or quote it")
        for h in HANDLE.findall(m):
            if h not in defined:
                add(n, "W", "W03", f"handle ${h} not defined in this text")
        words = {w.lower() for w in WORD.findall(HANDLE.sub("", m))}
        hit = sorted(words & PRONOUNS)
        if hit:
            add(n, "W", "W02", f"pronoun {', '.join(hit)}: name the thing or use a handle")
        hit = sorted(words & FILLER)
        if hit:
            add(n, "W", "W06", f"filler {', '.join(hit)}: drop it")

    def close(stmt):
        if stmt is None:
            return
        n, act, content, slots = stmt["n"], stmt["act"], stmt["content"], stmt["slots"]
        m = mask(content)
        if act == "fact" and "<-" not in m:
            add(n, "E", "E06", "fact needs a source after <- (or downgrade to think)")
        if act == "part" and "left" not in slots:
            add(n, "E", "E07", "part needs a left slot saying what remains")
        if act in ("no", "err", "need"):
            body = re.sub(r"#\w+", "", m).strip()
            if not body and not slots:
                add(n, "E", "E08", f"{act} needs a reason or the thing needed")
        if act == "do" and "check" not in slots:
            add(n, "W", "W01", "do has no check slot: receiver cannot tell when it is done")
        if act == "ask" and "?" not in m:
            add(n, "W", "W04", "ask has no ? marking the unknown")

    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not line.strip():
            continue

        if line[0] not in " \t":
            if HEADER.match(line):
                continue
            d = DEFN.match(line)
            if d:
                name, value = d.groups()
                check_words(n, value)
                if name in defined:
                    add(n, "E", "E05", f"handle ${name} already defined; pick a new name")
                defined.add(name)
                continue
            s = STMT.match(line)
            if not s or s.group(2) not in ACTS:
                first = line.split(" ", 1)[0]
                add(n, "E", "E01", f"line must start with an act, got {first!r}")
                close(cur)
                cur = None
                continue
            close(cur)
            sid, act, content = s.group(1), s.group(2), s.group(3) or ""
            if sid:
                if sid in ids:
                    add(n, "E", "E10", f"statement id #{sid} used twice")
                ids.add(sid)
            cur = {"n": n, "act": act, "content": content, "slots": set(), "cols": None}
            check_words(n, content)
            continue

        if line.startswith("\t") or line.startswith("  "):
            add(n, "E", "E04", "indent must be exactly one space")
            continue
        body = line[1:]
        if cur is None:
            add(n, "E", "E02", "indented line has no statement above it")
            continue
        if body.startswith("|"):
            if cur["cols"] is None:
                add(n, "E", "E09", "table row without a tab header above")
            else:
                cols = mask(body).count("|")
                if cols != cur["cols"]:
                    add(n, "E", "E09", f"row has {cols} cells, header has {cur['cols']}")
            check_words(n, body)
            continue
        if re.match(r"\d+ ", body):
            check_words(n, body.split(" ", 1)[1])
            continue
        word, _, rest = body.partition(" ")
        if word in OLD_SLOTS:
            add(n, "W", "W07", f"slot {word!r} is the Pith 1.0 name; use {OLD_SLOTS[word]!r}")
        elif word not in SLOTS:
            add(n, "E", "E03", f"unknown slot {word!r}")
            continue
        if word == "check" and "`" not in rest:
            add(n, "W", "W08", "check has no command in backticks: copy the command exactly")
        cur["slots"].add(word)
        if word == "tab":
            cur["cols"] = mask(rest).count("|") + 1
        check_words(n, rest)

    close(cur)
    issues.sort()
    return issues


def md_blocks(text):
    """Yield (start_line, block_text, section_index) for each ```pith block."""
    section, block, start, inside = 0, [], 0, False
    for n, line in enumerate(text.splitlines(), 1):
        if not inside:
            if line.startswith("#"):
                section += 1
            if line.strip() == "```pith":
                inside, block, start = True, [], n
        elif line.strip() == "```":
            inside = False
            yield start, "\n".join(block), section
        else:
            block.append(line)


def count_tokens(text):
    try:
        import tiktoken
    except ImportError:
        return math.ceil(len(text) / 4), "estimate (chars/4)"
    return len(tiktoken.get_encoding("o200k_base").encode(text)), "o200k_base"


def read(path):
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as f:
        return f.read()


def cmd_lint(args):
    known = [k for k in args.known.split(",") if k]
    errors = warnings = 0
    for path in args.files or ["-"]:
        text = read(path)
        if args.md:
            runs, section, carried = [], None, set(known)
            for start, block, sec in md_blocks(text):
                if sec != section:
                    section, carried = sec, set(known)
                runs.append((start, block, set(carried)))
                carried |= {m.group(1) for m in map(DEFN.match, block.splitlines()) if m}
        else:
            runs = [(0, text, set(known))]
        for offset, block, have in runs:
            for n, level, code, msg in lint(block, have):
                print(f"{path}:{n + offset}: {code} {msg}")
                if level == "E":
                    errors += 1
                else:
                    warnings += 1
    print(f"{errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


def cmd_count(args):
    for path in args.files or ["-"]:
        tokens, how = count_tokens(read(path))
        print(f"{path}: {tokens} tokens [{how}]")
    return 0


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Pith 1 toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("lint", help="check Pith messages")
    pl.add_argument("files", nargs="*")
    pl.add_argument("--md", action="store_true", help="lint ```pith blocks in markdown")
    pl.add_argument("--known", default="", help="comma-separated handles defined earlier")
    pl.set_defaults(fn=cmd_lint)
    pc = sub.add_parser("count", help="count tokens")
    pc.add_argument("files", nargs="*")
    pc.set_defaults(fn=cmd_count)
    pp = sub.add_parser("primer", help="print the first-contact primer")
    pp.set_defaults(fn=lambda a: print(PRIMER) or 0)
    args = p.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
