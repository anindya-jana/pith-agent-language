# Handoff accuracy: qwen3.5-9b, hops=1

420 graded runs, 0 failed attempts logged in errors.jsonl. Accuracy in %, 95% bootstrap interval over cases. Tokens are the server's own counts.

| arm | n | accuracy | status | constraint | detail | decoy | msg tokens | total tokens | reader prompt | notes |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| oracle | 60 | 100.0 (100.0-100.0) | 100.0 | 100.0 | 100.0 | 100.0 | - | 1055 | 950 |  |
| english | 60 | 96.7 (95.6-97.7) | 93.8 | 95.8 | 96.2 | 100.0 | 250 | 1631 | 952 |  |
| terse | 60 | 95.8 (94.2-97.1) | 98.3 | 95.0 | 93.8 | 100.0 | 128 | 1401 | 831 |  |
| json | 60 | 95.6 (93.8-97.3) | 91.7 | 89.2 | 97.8 | 100.0 | 270 | 1679 | 971 | valid JSON 60/60 |
| pith_skill | 60 | 90.0 (87.7-92.1) | 96.2 | 76.2 | 90.8 | 100.0 | 106 | 6263 | 3271 | lint-clean 31/60 |
| pith_primer | 60 | 88.6 (85.8-91.5) | 92.1 | 75.4 | 91.5 | 100.0 | 106 | 1564 | 920 | lint-clean 0/60 |
| null | 60 | 14.4 (12.4-16.5) | 0.0 | 0.0 | 14.6 | 100.0 | - | 807 | 702 |  |

## Paired against english

| arm | pairs | accuracy diff (points) | msg tokens | total tokens |
|---|---:|---|---:|---:|
| terse | 60 | -0.9 (-2.9 to +1.1) | -49% | -14% |
| json | 60 | -1.1 (-2.9 to +0.8) | +8% | +3% |
| pith_skill | 60 | -6.7 (-9.2 to -4.2) | -58% | +284% |
| pith_primer | 60 | -8.0 (-10.9 to -5.0) | -58% | -4% |

## Paired against terse

| arm | pairs | accuracy diff (points) | msg tokens | total tokens |
|---|---:|---|---:|---:|
| english | 60 | +0.9 (-1.1 to +2.9) | +95% | +16% |
| json | 60 | -0.2 (-2.6 to +2.0) | +111% | +20% |
| pith_skill | 60 | -5.8 (-8.3 to -3.2) | -17% | +347% |
| pith_primer | 60 | -7.1 (-10.0 to -4.2) | -18% | +12% |
