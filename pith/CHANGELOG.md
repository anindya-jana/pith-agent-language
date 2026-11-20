# Pith changelog

Each version is tested with the handoff benchmark in `bench/`. A change is kept only if it fixes a
failure seen in the benchmark transcripts, and it is then re-tested on new cases the change was not
designed against.

## 1.1

Found by running Pith 1.0 on Qwen3.5-4B, Qwen3.5-9B and Gemma 4 E2B (60 cases each). The table in
`bench/MODEL_RESULTS.md` ("Where Pith gains and loses") shows the per-question error rates behind
each change.

| Failure in 1.0 | Error rate with Pith 1.0 vs English | Change in 1.1 |
|---|---|---|
| Reports left out rules the worker had kept ("did not modify vendor/"), so readers answered "not stated" | 60% vs 9% | Report checklist: one ` did not ...` line per prohibition kept |
| Readers took the `may` slot as "maybe", not as permission | 41% vs 1% | `may` renamed `allow` |
| Readers took `should` as a requirement, and senders put requirements outside `must` | 20% vs 7% | `should` renamed `prefer`; brief checklist puts each rule in its slot |
| Senders shortened error text to its code ("no KT-9602 error"), losing the message and the verified observation | 37% vs 0% | Error text quoted in full, with an example |
| Done-check commands written without backticks were misread (`-q pass`) | 13% vs 0% | Every command in backticks; lint warns (W08) |
| Senders put a recommended next step in `need`, which means blocked | 10% vs 6% | `need` is only for blockers; the next step goes in `next` |
| Readers did not map `guess` to "unverified" | part of the status errors | Reading table: `think` and `guess` are both unverified beliefs |
| The 103-token primer was too thin: Qwen3.5-4B lost 28 points with it | | Primer rewritten (144 tokens) to name each slot's meaning and the report rules |

`should` and `may` are still accepted; the linter warns (W07). The message header stays `pith 1`.

What 1.0 already did well, kept unchanged: readers knew which claims were unverified far more often
than with English (hunches 1% wrong vs 37%), and exact details such as budgets, file and line, and
test counts survived better than in English.

## 1.0

First release: 13 acts, 14 slots, handles, evidence acts, linter, token benchmark.
