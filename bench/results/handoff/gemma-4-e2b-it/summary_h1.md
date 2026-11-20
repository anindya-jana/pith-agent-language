# Handoff accuracy: gemma-4-e2b-it, hops=1

420 graded runs, 0 failed attempts logged in errors.jsonl. Accuracy in %, 95% bootstrap interval over cases. Tokens are the server's own counts.

| arm | n | accuracy | status | constraint | detail | decoy | msg tokens | total tokens | reader prompt | notes |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| oracle | 60 | 100.0 (100.0-100.0) | 100.0 | 100.0 | 100.0 | 100.0 | - | 1070 | 960 |  |
| english | 60 | 83.8 (80.8-86.7) | 41.2 | 86.2 | 86.7 | 100.0 | 170 | 1484 | 877 |  |
| terse | 60 | 85.9 (83.0-88.6) | 64.2 | 86.2 | 90.9 | 100.0 | 104 | 1366 | 813 |  |
| json | 60 | 92.1 (90.3-93.8) | 79.2 | 95.0 | 97.3 | 100.0 | 259 | 1670 | 966 | valid JSON 60/60 |
| pith_skill | 60 | 82.0 (79.1-84.5) | 89.6 | 58.3 | 92.7 | 100.0 | 104 | 6256 | 3265 | lint-clean 0/60 |
| pith_primer | 60 | 88.9 (85.9-91.5) | 74.2 | 90.0 | 89.4 | 100.0 | 153 | 1665 | 967 | lint-clean 1/60 |
| null | 60 | 38.3 (34.4-42.1) | 18.3 | 61.7 | 27.9 | 68.3 | - | 818 | 708 |  |

## Paired against english

| arm | pairs | accuracy diff (points) | msg tokens | total tokens |
|---|---:|---|---:|---:|
| terse | 60 | +2.1 (-0.8 to +4.8) | -38% | -8% |
| json | 60 | +8.3 (+4.5 to +11.8) | +53% | +13% |
| pith_skill | 60 | -1.8 (-5.8 to +2.0) | -39% | +321% |
| pith_primer | 60 | +5.2 (+1.7 to +8.6) | -10% | +12% |

## Paired against terse

| arm | pairs | accuracy diff (points) | msg tokens | total tokens |
|---|---:|---|---:|---:|
| english | 60 | -2.1 (-4.8 to +0.8) | +62% | +9% |
| json | 60 | +6.2 (+2.9 to +9.5) | +148% | +22% |
| pith_skill | 60 | -3.9 (-7.6 to -0.2) | -1% | +358% |
| pith_primer | 60 | +3.0 (-0.2 to +6.4) | +46% | +22% |
