# Handoff accuracy: gemma-3-1b-it, hops=1

140 graded runs, 0 failed attempts logged in errors.jsonl. Accuracy in %, 95% bootstrap interval over cases. Tokens are the server's own counts.

| arm | n | accuracy | status | constraint | detail | decoy | msg tokens | total tokens | reader prompt | notes |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| oracle | 20 | 48.6 (44.1-53.2) | 48.8 | 30.0 | 63.7 | 15.0 | - | 1065 | 956 |  |
| english | 20 | 35.5 (30.5-40.5) | 23.8 | 30.0 | 51.2 | 0.0 | 225 | 1586 | 928 |  |
| terse | 20 | 37.3 (34.1-41.4) | 27.5 | 27.5 | 46.3 | 10.0 | 109 | 1367 | 814 |  |
| json | 20 | 32.7 (26.8-38.6) | 37.5 | 36.2 | 37.5 | 10.0 | 224 | 1592 | 926 | valid JSON 20/20 |
| pith_skill | 20 | 45.0 (40.9-49.5) | 78.8 | 45.0 | 40.2 | 0.0 | 103 | 6246 | 3260 | lint-clean 14/20 |
| pith_primer | 20 | 24.5 (20.9-28.6) | 3.8 | 23.8 | 30.5 | 30.0 | 9 | 1367 | 820 | lint-clean 0/20 |
| null | 20 | 25.9 (21.8-30.5) | 2.5 | 27.5 | 33.0 | 25.0 | - | 812 | 704 |  |

## Paired against english

| arm | pairs | accuracy diff (points) | msg tokens | total tokens |
|---|---:|---|---:|---:|
| terse | 20 | +1.8 (-4.5 to +8.2) | -51% | -14% |
| json | 20 | -2.7 (-8.2 to +2.7) | -1% | +0% |
| pith_skill | 20 | +9.5 (+2.7 to +16.8) | -54% | +294% |
| pith_primer | 20 | -10.9 (-15.9 to -5.0) | -96% | -14% |

## Paired against terse

| arm | pairs | accuracy diff (points) | msg tokens | total tokens |
|---|---:|---|---:|---:|
| english | 20 | -1.8 (-8.2 to +4.5) | +106% | +16% |
| json | 20 | -4.5 (-10.9 to +1.8) | +105% | +16% |
| pith_skill | 20 | +7.7 (+5.0 to +10.5) | -6% | +357% |
| pith_primer | 20 | -12.7 (-17.3 to -8.2) | -92% | +0% |
