# Pith: a language for messages between AI agents

Pith is a short, structured language that AI agents use to brief, question and report to each
other. A message is a few lines. Each line starts with a word that says what kind of line it is,
and the rest is telegraphic English.

```pith
pith 1
#1 do fix login 500
 why users locked out since deploy 4f2a91c
 not touch migrations/
 out diff, 1-line root cause
 check `npm test auth` pass
guess bug at src/auth/session.ts:40-90
```

```pith
done #1
 did edit src/auth/session.ts:57 `<` -> `<=`
 left full suite not run
fact 41/41 pass <- `npm test auth`
think cause = expiry check `<`: token expiring at exact current second passed as valid
guess src/auth/refresh.ts has same compare bug
```

It does two jobs:

- **Speed.** It uses about 39% fewer tokens than ordinary agent prose and about 34% fewer than
  the same facts in JSON (`bench/results.md`).
- **Accuracy.** Every claim is marked `fact` (verified, with its source), `think` (inferred) or
  `guess` (untested). Every task carries a `check` that says when it is done. Every report says
  what is `left`. Pronouns are banned, and long names become handles (`$db`).

The skill that teaches agents the language is in [pith/SKILL.md](pith/SKILL.md).

## Layout

| Path | What it is |
|---|---|
| [pith/SKILL.md](pith/SKILL.md) | The skill: the whole language on one screen, plus how to write and read it. |
| [pith/references/spec.md](pith/references/spec.md) | The full specification: rules, grammar, lint codes. |
| [pith/references/lexicon.md](pith/references/lexicon.md) | The canonical word for each common action, state and thing. |
| [pith/references/examples.md](pith/references/examples.md) | Eight worked exchanges with the prose they replace, and common mistakes. |
| [pith/scripts/pith.py](pith/scripts/pith.py) | Linter, token counter and first-contact primer. Standard library only. |
| [pith/evals/](pith/evals/) | Three test cases for the skill: write a brief, read a report, answer a question. |
| [pith/CHANGELOG.md](pith/CHANGELOG.md) | What changed in each version, and the benchmark evidence behind it. |
| [bench/MODEL_RESULTS.md](bench/MODEL_RESULTS.md) | Handoff benchmark scores, model by model. |
| [bench/HOW_TO_TEST.md](bench/HOW_TO_TEST.md) | How to run the handoff benchmark on your own model. |
| [bench/harness/](bench/harness/) | The handoff benchmark: case generator, runner, grader, reports. |
| [bench/results.md](bench/results.md) | Token counts for Pith against English, terse English and JSON. |
| [dist/pith.skill](dist/pith.skill) | The skill packaged for installing in the Claude app. |

## Install the skill

Download [dist/pith.skill](dist/pith.skill) and add it in the Claude app, or clone this repo:

```bash
git clone https://github.com/anindya-jana/pith-agent-language.git
```

Then copy the `pith` folder to one of these places:

- `~/.claude/skills/pith` to make it available in every project.
- `<project>/.claude/skills/pith` to make it available in one project.

Agents load it when they write a message for another agent, or when they receive one that starts
with `pith 1`. A peer that does not have the skill can be taught with the 144-token primer:

```bash
python pith/scripts/pith.py primer
```

Check a message:

```bash
python pith/scripts/pith.py lint message.txt
```

Check every Pith example in a markdown file:

```bash
python pith/scripts/pith.py lint --md pith/references/examples.md
```

Rerun the benchmark (needs `pip install tiktoken`):

```bash
python bench/bench.py --write
```

## What already exists

The research before the design looked for existing agent languages. There are many, and they fall
into five groups.

| Group | Examples | What Pith took | What Pith avoided |
|---|---|---|---|
| Classic agent communication languages | FIPA ACL, KQML | Speech acts: a fixed verb that says what a message does (request, inform, refuse). | Heavy envelopes and a separate logic content language. |
| Compact wire formats, 2025-2026 | PAIRL, DRIXL, AACP, LLMX, AICP, MLLANG, Vrext | Named references to long content (PAIRL, DRIXL context store), evidence and confidence records (PAIRL `#evid`). | Invented verb codes such as `XTRCT` and `ANLY`, which cost more tokens than the words they replace. Bracketed fields, which AACP measured at about 45% more tokens than English. |
| Data serialisation | TOON | A header-once table for repeated records. | A data-only format with no acts or evidence. |
| Emergent and model-native languages | CLSR, EcoLANG, BabelTele, Interlat | The finding that models compress well when the result is still built from tokens they know. | Learned codes that only one model pair can read, and that people cannot audit. |
| Non-text channels | Gibberlink (ggwave) | Nothing. | Data over sound solves a voice problem, not a token problem. |

Most size claims in these projects are self-reported, use different baselines, and do not measure
whether the receiver understood the message. The AACP draft is the most careful: it measured
about 23% savings against natural language, and its authors note that packing more into each
packet made messages longer, not shorter.

No existing format combined all four things Pith does: speech-act verbs, typed slots for the
fields receivers most often lack (done-check, scope, what is left), mandatory evidence levels, and
words chosen by measured token cost.

## How the design was chosen

Every symbol was chosen by counting tokens with OpenAI's `o200k_base` and `cl100k_base`
tokenizers. These are a proxy; Claude's tokenizer gives different absolute numbers.

| Finding | Measured | Rule |
|---|---|---|
| A common whole word is 1 token. A vowel-stripped code is more. | ` extract` 1, ` XTRCT` 3. ` validate` 1, ` VALD` 2. | Words are real English roots. |
| Non-Latin glyphs are never cheaper and often split. | ` fix` 1, ` 修` 1 to 2. ` because` 1, ` 因` 2. ` not` 1, ` ¬` 1 to 2. | ASCII only. |
| Brackets and quotes are overhead. | `[KEY:VALUE]` 5, `"key": "value",` 6, ` key value` 2. | A slot is a bare word, then content. |
| A one-space indent is free; two spaces cost a token per line. | `\n why x` 3, `\n  why x` 4. | Slot indent is exactly one space. |
| A sigil adds a token. | ` $db` 2. | A handle pays only for a long value used twice or more. |

The request was for something that might not be English. The measurements argue against it:
non-Latin letters and symbols cost the same or more than English words, and a model reads its own
training language most reliably. Pith's compression comes from structure (acts, slots, handles,
no filler), not from an alphabet.

## Benchmark results

The handoff benchmark tests whether a message is understood, not just how short it is. One agent
writes a message from private notes, and a fresh agent answers 11 questions about it, graded by
code. Full tables: [bench/MODEL_RESULTS.md](bench/MODEL_RESULTS.md). To test your own model, see
[bench/HOW_TO_TEST.md](bench/HOW_TO_TEST.md).

Results for Pith 1.0 on local models (60 cases each, 4-bit, RTX 3070):

| Model | English | Terse English | Pith 1.0 | Pith message tokens vs English |
|---|---:|---:|---:|---:|
| Qwen3.5-9B | 96.7% | 95.8% | 90.0% | -58% |
| Qwen3.5-4B | 90.5% | 94.2% | 88.2% | -52% |
| Gemma 4 E2B | 83.8% | 85.9% | 82.0% | -39% |
| Gemma 3 1B | too weak to take the test (48.6% even with the full notes) | | | |

What this shows:

- **Pith halves message size**, but Pith 1.0 cost 2 to 7 points of accuracy against English, and
  terse English did as well or better at a similar size.
- **Where Pith 1.0 helped:** readers knew which claims were only guesses far more often (37% wrong
  with English, 1% with Pith), and exact budgets, file lines and test counts survived better.
- **Where it hurt:** kept rules went unreported, `may` was read as "maybe", `should` as a
  requirement, and error text was shortened to its code.

Pith 1.1 fixes each of those failures ([pith/CHANGELOG.md](pith/CHANGELOG.md)) and is being
re-tested on new cases it was not tuned on.

## Limits

- Accuracy is measured on one task family (software-engineering briefs and reports) with
  generated cases. Real handoffs are messier.
- Against prose that is already telegraphic, Pith is only about 5% smaller. Its value there is
  the structure, not the size.
- The tokenizers used are OpenAI's. Relative savings should be similar for Claude; absolute
  counts will differ.
- Pith is for agent-to-agent messages only. Anything a person reads, and any request to confirm
  an irreversible action, stays in plain language.

## License

MIT. See [LICENSE](LICENSE).

## Sources

- FIPA ACL and KQML: [lecture notes, Univ. of Parma](https://www.ce.unipr.it/people/poggi/teaching/das/docs/0809/Communication.pdf), [FIPA ACL overview](https://jmvidal.cse.sc.edu/talks/fipaintro/communications.html)
- PAIRL: [github.com/dwehrmann/pairl](https://github.com/dwehrmann/pairl)
- DRIXL: [pypi.org/project/drixl](https://pypi.org/project/drixl/)
- AACP: [IETF draft-mackay-aacp-00](https://datatracker.ietf.org/doc/draft-mackay-aacp/00/)
- LLMX: [github.com/maiglesi/llmx](https://github.com/maiglesi/llmx)
- MLLANG: [github.com/jakeliu/mllang](https://github.com/jakeliu/mllang)
- Vrext: [github.com/devvrext/vrext](https://github.com/devvrext/vrext)
- AICP: [clawhub.ai/skills/aicp-protocol](https://clawhub.ai/skills/aicp-protocol)
- PAX: [dev.to article](https://dev.to/whoffagents/why-your-multi-agent-ai-system-needs-a-pax-protocol-253m)
- Esoteric AI Protocol: [ecosyste.ms listing](https://awesome.ecosyste.ms/projects/github.com%2Fkagioneko%2Fesoteric-ai-protocol)
- TOON: [github.com/telekom/toon](https://github.com/telekom/toon), [independent benchmark, arXiv 2603.03306](https://arxiv.org/pdf/2603.03306), [agentic benchmark, arXiv 2605.29676](https://arxiv.org/pdf/2605.29676)
- CLSR: [When LLMs Develop Languages, PMLR v306](https://proceedings.mlr.press/v306/pei26a.html)
- EcoLANG: [aitopics.org](https://aitopics.org/doc/arxivorg:5E936B10)
- BabelTele: [arXiv 2606.19857](https://arxiv.org/abs/2606.19857)
- Interlat: [arXiv 2511.09149](https://arxiv.org/pdf/2511.09149v2)
- Gibberlink: [TechCrunch](https://techcrunch.com/2025/03/05/gibberlink-lets-ai-agents-call-each-other-in-robo-language)
