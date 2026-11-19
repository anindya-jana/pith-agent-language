# Pith 1 lexicon

Pith's vocabulary is open: any common English root is a legal word. This file exists for one
reason, rule 7 of the spec: **one word per thing**. When two agents use "locate", "search for" and
"look up" for the same action, the receiver has to wonder whether they differ. Pick the canonical
word in the left column and the question never comes up.

Every canonical word below is a single token in both tokenizers tested, with the one exception
noted. Do not shorten them further: `cfg`, `impl` and `fn` save characters, not tokens, and cost
clarity.

## Contents

1. Reserved words
2. Actions
3. States
4. Things
5. Quantity, time, order
6. Words Pith does not use

## 1. Reserved words

These have fixed roles at the start of a line. Inside content they are ordinary words.

Acts: `do` `ask` `stop` `fact` `think` `guess` `ok` `no` `done` `part` `err` `need` `plan`

Slots: `why` `at` `with` `must` `not` `should` `may` `out` `check` `cap` `did` `left` `next` `tab`

## 2. Actions

| Use | Instead of |
|---|---|
| `find` | locate, search for, look up, look for, discover |
| `read` | inspect, view, open and look at, examine |
| `write` | create (a file or text), author, draft, generate |
| `edit` | modify, change, alter, tweak, adjust |
| `add` | insert, append, include, introduce |
| `remove` | delete, drop, strip, get rid of, take out |
| `move` | relocate, transfer |
| `rename` | change the name of |
| `replace` | swap, substitute |
| `run` | execute, invoke, launch, call (a command) |
| `test` | exercise with tests, run the tests for |
| `check` | verify, validate, confirm, make sure |
| `fix` | repair, resolve, correct, patch |
| `build` | compile, bundle, assemble |
| `deploy` | ship, release to, roll out |
| `revert` | undo, roll back, restore the previous |
| `retry` | try again, re-run |
| `fetch` | download, retrieve, pull (data), get from |
| `send` | post, submit, deliver, forward |
| `list` | enumerate, show all |
| `count` | tally, how many |
| `compare` | diff against, contrast |
| `merge` | combine, consolidate |
| `split` | divide, break up, separate |
| `summarize` | condense, give an overview of |
| `explain` | describe why, clarify |
| `review` | audit, critique, look over |
| `decide` | choose, settle, determine which |
| `estimate` | approximate, size up |
| `measure` | time, profile, benchmark |
| `keep` | preserve, leave unchanged, retain |
| `skip` | omit, leave out, pass over |
| `use` | apply, employ, rely on |
| `wait` | pause, hold |
| `start` / `kill` / `restart` | launch / terminate / bounce (a process) |
| `refactor` | restructure (two tokens in `o200k_base`; still the clearest word) |

## 3. States

| Use | Instead of |
|---|---|
| `pass` / `fail` | succeed, green / break, red, not work |
| `broken` | not working, malfunctioning |
| `missing` | absent, not present, not found |
| `extra` | unexpected, surplus, unneeded |
| `same` / `changed` | identical, unchanged / different, modified |
| `new` / `old` | fresh, latest / previous, former, legacy |
| `stale` | out of date, outdated |
| `slow` / `fast` | sluggish / quick |
| `safe` / `risky` | harmless / dangerous, may break things |
| `blocked` | stuck, cannot proceed |
| `ready` / `pending` | prepared / waiting, queued, not yet started |
| `open` / `closed` | unresolved / resolved, finished |
| `valid` / `invalid` | well-formed / malformed |
| `likely` / `unlikely` | probable / improbable (inside a `think` or `guess`) |
| `unknown` | not known, unclear, to be determined |
| `public` / `private` | exposed / internal |
| `local` / `remote` | on this host / on another host |

## 4. Things

| Use | Instead of |
|---|---|
| `file` / `dir` / `path` | document / folder, directory / location |
| `line` | row of source text |
| `function` | method, routine, procedure |
| `arg` | parameter, argument |
| `value` | setting, amount |
| `error` | exception, fault (the act is `err`; the noun is `error`) |
| `bug` | defect, issue in code |
| `test` | spec, test case |
| `db` / `table` / `row` / `col` | database / relation / record / column, field |
| `query` | SQL statement, lookup |
| `api` / `route` | interface / endpoint |
| `request` / `response` | call / reply (over a network) |
| `config` / `env` / `flag` | settings / environment / switch, option |
| `secret` | credential, password, API key (never write the secret's value) |
| `branch` / `commit` / `diff` / `pr` / `repo` | as in git |
| `dep` | dependency, package, library |
| `version` | release number |
| `cache` / `queue` / `job` | as usual |
| `task` / `step` | piece of work / one stage of a plan |
| `goal` | objective, aim, desired outcome |
| `cause` / `effect` | root cause, reason / consequence, impact |
| `risk` | danger, downside |
| `cost` | price, expense, overhead |
| `scope` | boundary of the work |
| `input` / `output` / `result` | as usual |
| `source` | origin, where it came from |
| `doc` / `spec` | documentation / specification |

## 5. Quantity, time, order

| Write | Meaning |
|---|---|
| `48.2s` `200ms` `5 min` `2h` `3d` | durations: number then unit |
| `310M rows` `4KB` `12 files` | counts and sizes: number then unit |
| `41/41` | passed out of total |
| `3x` | three times |
| `~200ms` | about 200ms |
| `<= 20 calls` | at most 20 |
| `all` `none` `some` `each` `only` | quantifiers |
| `first` `last` `next` `before` `after` `since` `until` `now` | order and time |
| `2026-11-16` `14:30 UTC` | dates and times are absolute, never "yesterday" or "in an hour" |

Relative dates rot: the receiver may read the message later or in another time zone, so always
write the absolute date.

## 6. Words Pith does not use

| Kind | Examples | Why |
|---|---|---|
| Articles | a, an, the | They carry no information here. |
| Pronouns | it, this, that, they | The referent is the most common thing a receiver gets wrong. |
| Politeness | please, thanks, sorry, kindly | The act word already sets the stance. |
| Hedges | maybe, perhaps, I believe, it seems | Use `think` or `guess` instead; the act carries the certainty. |
| Intensifiers | very, really, quite, just | They add tokens and no fact. |
| Relative time | today, yesterday, soon, recently | Write the absolute date or time. |
