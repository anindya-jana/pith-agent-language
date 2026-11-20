# How to test a model with the Pith benchmark

This guide shows how to run the Pith handoff benchmark on any model you can reach through an
OpenAI-compatible chat endpoint, whether it runs on your own GPU, in LM Studio, Ollama,
llama.cpp, vLLM, or on a hosted service. You get the same numbers we report: how accurately one
agent's message is understood by another, and how many tokens the message costs, for each message
format.

## What the benchmark measures

**Suite A, handoff accuracy.** One agent (the sender) receives private notes. It writes a single
message to another agent in the format being tested. A fresh agent (the reader) sees only that
message and answers 11 multiple-choice questions about it. The answers are graded against the
notes by code, so no judge model is involved.

There are two kinds of handoff, alternating:

- **brief:** an orchestrator hands a task to a worker. Questions cover the done-check command,
  what is forbidden or allowed, mandatory versus preferred, the budget, the deliverable, and where
  to work.
- **report:** a worker reports back. Questions cover what was verified versus only believed, exact
  numbers, the file and line edited, the exact error text, what was not done, and the next step.

Every service name, path, command and error code is invented, so a model cannot answer from
memory. Every question offers "not stated". Decoy questions ask about things the notes never
mention, so any answer other than "not stated" is a hallucination.

**The formats compared (arms):**

| Arm | The sender is told to write | The reader is told |
|---|---|---|
| `english` | Clear, natural English | Messages are in English |
| `terse` | Terse, telegraphic English that keeps every fact | Messages are in terse English |
| `json` | One JSON object, keys of its choice | Messages are JSON |
| `pith_skill` | Pith 1.0, with the full skill in its system prompt | Same, with the full skill |
| `pith_primer` | Pith 1.0, with only its 103-token primer | Same, with the primer |
| `pith_skill_1.1` | Pith 1.1, with the full skill | Same |
| `pith_primer_1.1` | Pith 1.1, with only its 144-token primer | Same |
| `oracle` | No sender: the reader gets the sender's full notes | Calibration: the ceiling |
| `null` | No sender: the reader gets an empty message | Calibration: the floor |

The model, the notes, the questions and the decoding settings are identical in every arm. Only the
format changes. Each Pith version is a frozen copy in `bench/harness/skills/<version>/`, so a
result always names the exact text it used. By default the runner uses the five original arms plus
the two calibration arms; pass `--arms` to choose others.

**Scores reported per arm:**

| Column | Meaning |
|---|---|
| `accuracy` | Share of the 11 questions answered correctly, with a 95% interval |
| `status` | Did the reader know which claims were verified and which were only believed? |
| `constraint` | Did the reader keep the rules: forbidden, allowed, mandatory, preferred, done or not done? |
| `detail` | Exact commands, numbers, paths, error strings, deliverables |
| `decoy` | Did the reader correctly answer "not stated" for things never mentioned? |
| `msg tokens` | Length of the message, from the server's own tokenizer |
| `total tokens` | Every prompt and completion token for the sender and reader, including the skill or primer |
| `reader prompt` | What the reader had to read, which shows the cost of carrying the skill |

The report also gives paired differences against `english` and against `terse`: the change in
accuracy (in points, with an interval) and the change in tokens. Only cases where both arms
finished cleanly are paired.

## Requirements

- Python 3.9 or later. The harness uses only the standard library.
- An OpenAI-compatible `/v1/chat/completions` endpoint serving your model.
- Around 8k tokens of context. The `pith_skill` arms put about 2,500 to 3,000 tokens of skill text in the
  system prompt.
- Ideally, server support for JSON-schema output (`response_format` with `json_schema`). LM
  Studio, recent Ollama, the llama.cpp server and vLLM support it. If yours does not, add
  `--no-schema`.

## Step 1: serve your model

Pick the line that matches how you run models. Note the base URL and the model ID the server
lists.

**LM Studio**

```bash
lms server start
```

```bash
lms load qwen3.5-9b --context-length 16384 --gpu max -y
```

The server prints its port. The base URL is `http://127.0.0.1:<port>/v1`.

**Ollama**

```bash
ollama pull qwen3:8b
```

The base URL is `http://127.0.0.1:11434/v1`, and the model ID is `qwen3:8b`.

**llama.cpp server**

```bash
llama-server -m your-model.gguf -c 16384 --port 8080
```

The base URL is `http://127.0.0.1:8080/v1`.

**A hosted endpoint** (Gemini, OpenRouter, Together, Groq, your company's gateway). Keep the key
in a file outside this repo, and never paste it into a command line or a chat. This one-liner asks
for the key without echoing it and saves it to `~/.pith/api_key`:

```bash
python -c "import getpass,pathlib; p=pathlib.Path.home()/'.pith'; p.mkdir(exist_ok=True); (p/'api_key').write_text(getpass.getpass('API key: ').strip())"
```

Then pass `--api-key-file ~/.pith/api_key` and the provider's OpenAI-compatible base URL. For
Gemini that is `https://generativelanguage.googleapis.com/v1beta/openai`. Hosted APIs are slow per
call but take parallel requests, so add `--workers 4`. On a free tier, add `--min-interval 2`
(seconds between call starts) and `--retries 6`, because busy models answer "high demand" (503)
or "quota exceeded" (429) and need retrying.

A Gemini example, as used for the published Gemini results:

```bash
python bench/harness/run.py --model gemini-3.5-flash --base-url https://generativelanguage.googleapis.com/v1beta/openai --api-key-file ~/.pith/gemini_key --reasoning-effort low --workers 4 --retries 6 --min-interval 1 --n 30
```

Gemini rejects the `seed` field; the runner notices and drops it automatically. Gemini models
take `--reasoning-effort low` (not `none`); Gemma models served by Gemini take no reasoning setting,
so pass `--reasoning-effort ""` for them.

Check that the model is listed:

```bash
curl -s http://127.0.0.1:1234/v1/models
```

## Step 2: check the grader

This makes no model calls. It confirms that perfect answers score 100% and empty answers score 0%.

```bash
python bench/harness/run.py --selftest --n 200
```

Expect `selftest PASS`. For reference, always answering "not stated" scores about 9%, and random
guessing about 28%.

## Step 3: run a pilot

Run 10 cases across every arm. This shows the speed and catches setup problems before a long run.

```bash
python bench/harness/run.py --model qwen3.5-9b --base-url http://127.0.0.1:1234/v1 --n 10
```

Then read the summary:

```bash
python bench/harness/report.py bench/results/handoff/qwen3.5-9b
```

Before going further, check two calibration rows:

- **`oracle` should be well above 90%.** If it is not, the model cannot answer the questions even
  with the full facts in front of it, so differences between formats are not meaningful for that
  model.
- **`null` should be near 9%.** That means only the decoys are right. If it is much higher, the
  reader is guessing instead of answering "not stated".

If the `reasoning` note shows many tokens per run, the model is thinking before it answers, which
mixes reasoning tokens into the message count. The runner sends `reasoning_effort: "none"` by
default, which turns thinking off on LM Studio (tested with Qwen3.5). If your server rejects that
field, pass `--reasoning-effort ""` to leave it out, and turn thinking off in the server or model
settings instead.

## Step 4: run the full benchmark

Rows are saved as each run finishes. If a run stops, the same command resumes where it left off.

```bash
python bench/harness/run.py --model qwen3.5-9b --base-url http://127.0.0.1:1234/v1 --n 100
```

How many cases you need depends on the size of difference you want to detect:

| Cases | Roughly the smallest accuracy difference you can trust |
|---:|---|
| 20 | 20 points (pilot only) |
| 60 | 12 points |
| 100 | 10 points |
| 200 | 7 points |

Decoding is greedy (temperature 0), so repeating a case gives the same answer. Add cases rather
than repeats.

**Optional: relay drift.** Pass each message through two relay agents before the reader, which
shows how much each format loses per hop:

```bash
python bench/harness/run.py --model qwen3.5-9b --base-url http://127.0.0.1:1234/v1 --n 60 --hops 3 --arms english,terse,json,pith_skill
```

**Optional: two different models.** Have one model write and another read, for example a strong
orchestrator briefing a small worker:

```bash
python bench/harness/run.py --model qwen3.5-9b --reader-model gemma-4-e2b-it --base-url http://127.0.0.1:1234/v1 --n 60
```

Both models must be loaded on the same server.

## Step 5: write the report

```bash
python bench/harness/report.py bench/results/handoff/qwen3.5-9b --write
```

This writes `summary_h1.md` next to the results. Use `--hops 3` for the relay run.

## Reading the result

Pith does its job for a model if both of these hold:

1. **Accuracy holds.** The `pith_skill` accuracy difference against `english` is no worse than
   about -2 points, and its interval includes zero or is above it.
2. **Tokens drop.** `msg tokens` falls substantially against `english` and is at or below `terse`.

Then look at `total tokens`. The skill costs about 3,000 tokens of system prompt per agent. A
single short exchange can therefore cost more in total even when every message is shorter.
Caching the system prompt, or using the primer arm, changes that. The `pith_primer` row shows
whether the model can use Pith without the full guide.

Check `lint-clean` too. A low share means the model writes something Pith-like but does not follow
the rules, and the `status` column will show whether that costs accuracy.

## Where the files are

```
bench/results/handoff/<model>/
  results.jsonl      one row per case and arm: scores, per-question answers, tokens, timing
  errors.jsonl       attempts that failed (server error, timeout, unreadable answer); rerun to retry
  traces/            the full conversation for each case and arm: system prompts, notes, message, answers
  summary_h1.md      written by report.py --write
```

To see exactly what a model wrote, open a trace file, for example
`traces/h001_pith_skill_h1.json`.

## Adding your own format

Add an entry to `ARMS` in `bench/harness/protocols.py` with three fields: `write` (the sender's
instruction), `read` (what the reader is told), and `doc` (any guide both of them get). Then pass
its name in `--arms`. Keep the other arms unchanged, so the new format is compared on the same
footing.

## Rules for a fair comparison

- Use the same model, server, quantization and settings for every arm in one comparison.
- Leave the decoding settings alone: temperature 0, fixed seed.
- Do not edit the notes, questions or arm instructions between arms or between models. If you
  change them, rerun every arm.
- Report the `oracle` and `null` rows together with your result. They show whether the model could
  take the test at all.
- Report failed attempts from `errors.jsonl`. Do not drop them silently.
