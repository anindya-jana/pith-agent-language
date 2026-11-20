"""The message formats under test. The format is the only thing that differs
between arms: tasks, models, decoding and questions are identical.

Each arm says how a sender must write and what a reader is told about the
format. In the Pith arms the reader gets the same skill or primer as the
sender, so its cost is counted on both sides.

Pith arms read frozen copies of each released version from skills/<version>/,
never the live pith/SKILL.md, so every result names the exact text it used.
`pith_skill` and `pith_primer` are version 1.0 (their original names); later
versions are `pith_skill_<version>` and `pith_primer_<version>`.
"""
import os

SKILLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")


def _read(version, name):
    with open(os.path.join(SKILLS, version, name), encoding="utf-8") as f:
        text = f.read()
    if name == "SKILL.md" and text.startswith("---"):
        text = text.split("---", 2)[2]
    return text.strip()


VERSIONS = sorted(os.listdir(SKILLS), key=lambda v: [int(x) for x in v.split(".")])

ARMS = {
    "english": {
        "write": "Write the message in clear, natural English, the way you normally would.",
        "read": "Messages from other agents are written in English.",
        "doc": "",
    },
    "terse": {
        "write": ("Write the message in terse, telegraphic English. Drop filler, "
                  "pleasantries and articles, but keep every fact the reader needs."),
        "read": "Messages from other agents are written in terse English.",
        "doc": "",
    },
    "json": {
        "write": ("Write the message as a single JSON object with keys you choose. "
                  "Output only the JSON object, no other text."),
        "read": "Messages from other agents are JSON objects.",
        "doc": "",
    },
}

for _v in VERSIONS:
    _suffix = "" if _v == "1.0" else "_" + _v
    ARMS["pith_skill" + _suffix] = {
        "write": "Write the message in Pith, following the language guide below. Output only the Pith message.",
        "read": "Messages from other agents are written in Pith, described in the language guide below.",
        "doc": "# Pith language guide\n\n" + _read(_v, "SKILL.md"),
    }
    ARMS["pith_primer" + _suffix] = {
        "write": "Write the message in Pith, using the summary below. Output only the Pith message.",
        "read": "Messages from other agents are written in Pith, summarised below.",
        "doc": "Pith summary: " + _read(_v, "PRIMER.txt"),
    }

# Calibration arms: no sender. `oracle` hands the reader the sender's full
# notes (upper bound, and proof every question is answerable). `null` hands
# the reader an empty message (floor, and proof the grader is not lenient).
CALIBRATION = ("oracle", "null")


def system_prompt(role, arm):
    spec = ARMS.get(arm, ARMS["english"])
    if role == "sender":
        base = ("You are an AI agent in a multi-agent system. You write messages that "
                "another AI agent will read. The reader sees only your message, not your "
                "notes. " + spec["write"])
    elif role == "relay":
        base = ("You are an AI agent in a multi-agent system. You received a message and "
                "must pass it on to the next agent, who sees only what you write. Keep "
                "everything the next agent needs. " + spec["write"])
    else:
        base = ("You are an AI agent in a multi-agent system. You received a message from "
                "another agent. " + spec["read"] + " Answer each question using only what the "
                "message says. If the message does not say, choose the 'not stated' option. "
                "Do not guess.")
    return base + ("\n\n" + spec["doc"] if spec["doc"] else "")
