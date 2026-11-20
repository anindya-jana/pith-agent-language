"""Suite A: handoff accuracy.

A sender agent gets private notes whose every fact has a known status. It
writes one message in the arm's format. A fresh reader agent sees only that
message and answers multiple-choice questions. Answers are graded against the
notes, so no judge model is involved.

Two kinds of handoff, alternating:
  brief   an orchestrator hands a task to a worker (constraints, check, budget)
  report  a worker reports back (what was done, verified, believed, left)

Every name, path, command and error is invented, so a reader cannot answer
from memory. Each question has a 'not stated' option, and decoy questions ask
about things the notes never mention: choosing anything but 'not stated' there
is a hallucination.
"""
import random

SERVICES = ["quillstack", "marrowd", "fennelgate", "ostrander", "briarlink", "cobaltine",
            "tamsin", "vellum", "harrowmere", "pikeway", "juniperd", "sablecourt"]
MODULES = ["auth", "billing", "ingest", "search", "export", "sched", "notify", "ledger",
           "cache", "upload"]
FILES = ["session", "handler", "worker", "client", "router", "store", "parser", "limits",
         "retry", "queue"]
EXTS = ["ts", "py", "go", "rs"]
TEAMS = ["payments", "platform", "security", "data", "mobile"]
LIBS = ["axios", "requests", "protobuf", "lodash", "tokio", "pydantic"]
LOGS = ["the service log", "the error dashboard", "the worker log", "the API gateway log"]
ERROR_PHRASES = ["lease expired", "connection reset by peer", "checksum mismatch",
                 "deadline exceeded", "stale handle"]

BUGS = [
    ("login returns HTTP 500 for some users",
     "the token expiry check uses < instead of <=", "changed the expiry comparison from < to <="),
    ("customers are billed twice for one order",
     "the retry loop re-sends a charge after a timeout without an idempotency key",
     "added an idempotency key to retried charges"),
    ("CSV export hangs at 99%",
     "the last chunk is never flushed when the file size is a multiple of 4096 bytes",
     "added a final flush after the write loop"),
    ("search shows results in the wrong language",
     "the cache key ignores the user's locale", "added the locale to the cache key"),
    ("uploads larger than 2 GB fail",
     "the upload length is stored in a 32-bit integer", "changed the length field from int32 to int64"),
    ("nightly jobs sometimes run twice",
     "the job lock is released before the database commit", "moved the lock release to after the commit"),
    ("notifications arrive about 10 minutes late",
     "the batch timer resets on every new enqueue", "replaced the resetting timer with a fixed batch deadline"),
    ("invoice totals are off by one cent",
     "amounts are rounded before they are summed", "moved rounding to after the sum"),
    ("password reset emails link to the wrong host",
     "the reset URL is built from the request Host header",
     "switched the reset link to the configured public base URL"),
    ("the dashboard times out for large accounts",
     "the summary query has no index on account_id", "added an index on account_id"),
]

WHYS = ["{n} customers opened support tickets since release {ver}",
        "finance flagged it during the month-end close",
        "it blocks the {ver} release",
        "the on-call engineer was paged {n} times this week"]
MUSTS = ["keep the public API of the {module} module unchanged",
         "keep backward compatibility with clients on version {old}",
         "keep the database schema unchanged",
         "keep every existing test passing"]
SHOULDS = ["make a minimal fix rather than a refactor",
           "reuse the existing retry helper",
           "put the change behind a feature flag",
           "keep the change under 50 lines"]
MAYS = ["add new test files", "add temporary debug logging",
        "upgrade the {lib} dependency", "create a new helper module"]
OUTS = ["the diff and a one-line root cause",
        "a short report with the test output before and after",
        "a pull request link and a summary of the change",
        "the patch and the list of files touched"]
NEXTS = ["run the full test suite", "deploy to staging and watch error rates for an hour",
         "ask the {team} team to review the change", "check the other services for the same pattern"]
NOTDONES = ["the full test suite", "the load test", "the staging deploy", "the migration dry run"]
DECOYS = ["the bug also affects the {svc} service", "the {lib} dependency is out of date",
          "the issue only happens on Windows clients", "the bug was introduced by the {team} team"]

STATUS = ["verified (the sender checked it directly)",
          "unverified (the sender believes or suspects it, but did not check)"]
YESNO = ["yes", "no"]
ALLOWED = ["yes, allowed", "no, forbidden"]
REQUIRED = ["mandatory", "a preference, not mandatory"]
NOT_STATED = "not stated"


def commands(ext, module, file):
    cap = file.capitalize()
    return {
        "ts": [f"npm test {module}", f"npm run test:{module}", f"npx jest tests/{module}"],
        "py": [f"pytest tests/{module}", f"pytest tests/{module} -q", f"python -m pytest tests/{module}"],
        "go": [f"go test ./{module}/...", f"go test ./internal/{module}/...", f"go test -run {cap} ./{module}"],
        "rs": [f"cargo test {module}", f"cargo test -p {module}", f"cargo test --test {module}"],
    }[ext]


class Builder:
    """Collects multiple-choice questions for one case."""

    def __init__(self, rng):
        self.rng = rng
        self.items = []

    def mc(self, qtype, question, gold, distractors):
        """Options: gold plus distractors, shuffled, then 'not stated' last."""
        opts = [gold] + [d for d in dict.fromkeys(distractors) if d != gold][:3]
        self.rng.shuffle(opts)
        self.items.append({"type": qtype, "question": question,
                           "options": opts + [NOT_STATED], "gold": opts.index(gold)})

    def fixed(self, qtype, question, choices, gold):
        """Options in a fixed order, then 'not stated'. gold may be NOT_STATED."""
        opts = list(choices) + [NOT_STATED]
        self.items.append({"type": qtype, "question": question, "options": opts,
                           "gold": opts.index(gold)})

    def done(self):
        for i, q in enumerate(self.items, 1):
            q["id"] = f"q{i}"
        return self.items


def _common(rng):
    module, ext = rng.choice(MODULES), rng.choice(EXTS)
    f1, f2, f3 = rng.sample(FILES, 3)
    svc, decoy_svc = rng.sample(SERVICES, 2)
    return {
        "svc": svc, "decoy_svc": decoy_svc, "module": module, "ext": ext,
        "path": f"src/{module}/{f1}.{ext}", "line": rng.randint(20, 400),
        "other": f"src/{module}/{f2}.{ext}", "third": f"src/{module}/{f3}.{ext}",
        "file": f1, "bug": rng.choice(BUGS), "team": rng.choice(TEAMS),
        "lib": rng.choice(LIBS), "tid": rng.randint(10, 99),
        "ver": f"{rng.randint(2, 9)}.{rng.randint(0, 19)}",
        "old": f"{rng.randint(1, 3)}.{rng.randint(0, 9)}",
        "n": rng.randint(3, 60),
    }


def _fill(template, c):
    return template.format(n=c["n"], ver=c["ver"], old=c["old"], module=c["module"],
                           lib=c["lib"], team=c["team"], svc=c["decoy_svc"])


def make_brief(rng):
    c = _common(rng)
    symptom = c["bug"][0]
    cmds = commands(c["ext"], c["module"], c["file"])
    cmd = rng.choice(cmds)
    others = [s for s in SERVICES if s != c["svc"]]
    where = f"services/{c['svc']}/"
    protected = rng.choice(["migrations", "vendor", "deploy", "config/prod"])
    why, must, should, may, out = (_fill(rng.choice(x), c) for x in (WHYS, MUSTS, SHOULDS, MAYS, OUTS))
    cap = rng.choice([15, 20, 25, 30, 40, 50])

    notes = f"""You are the orchestrator. You are handing task #{c['tid']} to a worker agent.
These are your notes. The worker will not see them, only your message.

- The task: fix the bug where {symptom} in the {c['svc']} service.
- Why it matters: {why}.
- The worker must work only inside {where}.
- Hard requirement: {must}.
- Forbidden: the worker must not modify anything under {protected}/.
- Preference, not mandatory: {should}.
- Permission: the worker may {may}.
- What to send back: {out}.
- The task counts as done when `{cmd}` passes.
- Budget: at most {cap} tool calls.
- Your own hunch, which you have NOT checked: the bug is probably in {c['other']}."""

    b = Builder(rng)
    b.mc("detail", "Which command shows the task is done?", f"`{cmd}`",
         [f"`{x}`" for x in cmds if x != cmd] + [f"`{cmd} --all`"])
    b.fixed("constraint", f"May the worker modify files under {protected}/?", ALLOWED, ALLOWED[1])
    b.fixed("constraint", f"May the worker {may}?", ALLOWED, ALLOWED[0])
    b.fixed("constraint", f"Is this mandatory or only a preference: \"{should}\"?", REQUIRED, REQUIRED[1])
    b.fixed("constraint", f"Is this mandatory or only a preference: \"{must}\"?", REQUIRED, REQUIRED[0])
    b.mc("detail", "What is the budget for the task?", f"{cap} tool calls",
         [f"{x} tool calls" for x in (cap - 5, cap + 10, cap * 2)])
    b.fixed("status", f"What is the status of the claim that the bug is in {c['other']}?",
            STATUS, STATUS[1])
    b.mc("detail", "What should the worker send back?", out, [x for x in (_fill(o, c) for o in OUTS)])
    b.fixed("decoy", f"Must the worker get approval from the {c['team']} team before merging?",
            YESNO, NOT_STATED)
    b.mc("detail", "Where must the worker work?", where,
         [f"services/{s}/" for s in rng.sample(others, 3)])
    b.mc("detail", "Why does the task matter?", why,
         [x for x in (_fill(w, c) for w in WHYS) if x != why])
    task = f"Write the message that hands task #{c['tid']} to the worker agent."
    return notes, task, b.done()


def make_report(rng):
    c = _common(rng)
    symptom, cause, change = c["bug"]
    cmds = commands(c["ext"], c["module"], c["file"])
    cmd = rng.choice(cmds)
    total = rng.randint(12, 180)
    code = f"{rng.choice('QXZKV')}{rng.choice('RTMPW')}-{rng.randint(1000, 9999)}"
    err = f"{code}: {rng.choice(ERROR_PHRASES)}"
    log = rng.choice(LOGS)
    protected = rng.choice(["migrations", "vendor", "deploy", "config/prod"])
    notdone = rng.choice(NOTDONES)
    nxt = _fill(rng.choice(NEXTS), c)
    decoy = _fill(rng.choice(DECOYS), c)
    test_path = f"tests/{c['module']}/test_{c['file']}.{c['ext']}"

    notes = f"""You are a worker agent. You just finished task #{c['tid']}: fix the bug where {symptom} in the {c['svc']} service.
These are your notes. The orchestrator will not see them, only your message.

What you did:
- You edited {c['path']} at line {c['line']}: you {change}.
- You added a regression test in {test_path}.
- You did not modify anything under {protected}/, as instructed.

What you checked yourself:
- After the edit you ran `{cmd}`: {total} of {total} tests passed.
- Before the fix, {log} showed the error "{err}". After the fix you watched {log} for ten minutes and the error did not appear.

What you believe but did not check:
- You think the root cause was that {cause}. You reasoned this from reading the code; you did not prove it.
- You suspect {c['other']} has the same bug. You have not opened that file.

What you did not do:
- You did not run {notdone}.

Recommended next step: {nxt}."""

    b = Builder(rng)
    b.fixed("status", f"What is the status of the claim that `{cmd}` passes?", STATUS, STATUS[0])
    b.fixed("status", f"What is the status of the claim that the error \"{err}\" stopped appearing after the fix?",
            STATUS, STATUS[0])
    b.fixed("status", f"What is the status of the claim that the root cause was that {cause}?",
            STATUS, STATUS[1])
    b.fixed("status", f"What is the status of the claim that {c['other']} has the same bug?",
            STATUS, STATUS[1])
    b.fixed("decoy", f"What is the status of the claim that {decoy}?", STATUS, NOT_STATED)
    b.mc("detail", "How many tests passed after the edit?", f"{total} of {total}",
         [f"{total - 1} of {total}", f"{total} of {total + 3}", f"{max(1, total - 10)} of {total}"])
    b.mc("detail", "Which file and line did the worker edit?", f"{c['path']} line {c['line']}",
         [f"{c['path']} line {c['line'] + 7}", f"{c['other']} line {c['line']}",
          f"{c['third']} line {c['line']}"])
    alt_code = code[:3] + code[3:][::-1] if code[3:] != code[3:][::-1] else code[:3] + "1" + code[4:]
    b.mc("detail", "What exact error did the worker see before the fix?", err,
         [f"{alt_code}: {err.split(': ')[1]}",
          f"{code}: {[p for p in ERROR_PHRASES if p not in err][0]}",
          f"{code[:-1]}{(int(code[-1]) + 1) % 10}: {err.split(': ')[1]}"])
    b.fixed("constraint", f"Did the worker run {notdone}?", YESNO, YESNO[1])
    b.fixed("constraint", f"Did the worker modify anything under {protected}/?", YESNO, YESNO[1])
    b.mc("detail", "What next step does the worker recommend?", nxt,
         [x for x in (_fill(n, c) for n in NEXTS) if x != nxt])
    task = f"Write your report on task #{c['tid']} to the orchestrator."
    return notes, task, b.done()


# Short labels for each question, in the order make_brief / make_report ask them.
QUESTION_NAMES = {
    "brief": ["done-check command", "forbidden path respected", "permission understood",
              "preference not taken as rule", "requirement taken as rule", "budget",
              "hunch marked unverified", "deliverable", "decoy: approval rule", "work directory",
              "purpose"],
    "report": ["test result marked verified", "observed fix marked verified",
               "root cause marked unverified", "other-file suspicion marked unverified",
               "decoy: unrelated claim", "test count", "file and line edited", "exact error text",
               "skipped work reported", "kept prohibition reported", "next step"],
}


def make_cases(n, seed=2026):
    cases = []
    for i in range(n):
        rng = random.Random(seed * 1000 + i)
        kind = "brief" if i % 2 == 0 else "report"
        notes, task, questions = (make_brief if kind == "brief" else make_report)(rng)
        cid = f"h{i:03d}" if seed == 2026 else f"s{seed}-{i:03d}"  # 2026 = the original set
        cases.append({"id": cid, "kind": kind, "notes": notes, "task": task,
                      "questions": questions})
    return cases


def answer_schema(questions):
    letters = "ABCDEFG"
    props = {q["id"]: {"type": "string", "enum": list(letters[:len(q["options"])])} for q in questions}
    return {"type": "object", "properties": props, "required": list(props),
            "additionalProperties": False}


def render_questions(questions):
    letters = "ABCDEFG"
    lines = []
    for q in questions:
        lines.append(f"{q['id']}. {q['question']}")
        for j, opt in enumerate(q["options"]):
            lines.append(f"   {letters[j]}) {opt}")
    return "\n".join(lines)


def grade(questions, answers):
    """Return per-type accuracy and the per-question record."""
    letters = "ABCDEFG"
    per_q, by_type = [], {}
    for q in questions:
        got = answers.get(q["id"])
        idx = letters.index(got) if isinstance(got, str) and got in letters else None
        ok = idx == q["gold"]
        per_q.append({"id": q["id"], "type": q["type"], "gold": letters[q["gold"]],
                      "got": got, "ok": ok})
        by_type.setdefault(q["type"], []).append(ok)
    score = {"acc": sum(p["ok"] for p in per_q) / len(per_q)}
    for t, oks in sorted(by_type.items()):
        score[f"acc_{t}"] = sum(oks) / len(oks)
    return score, per_q
