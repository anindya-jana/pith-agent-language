# Handoff accuracy: qwen3.5-4b, hops=1

420 graded runs, 0 failed attempts logged in errors.jsonl. Accuracy in %, 95% bootstrap interval over cases. Tokens are the server's own counts.

| arm | n | accuracy | status | constraint | detail | decoy | msg tokens | total tokens | reader prompt | notes |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| oracle | 60 | 100.0 (100.0-100.0) | 100.0 | 100.0 | 100.0 | 100.0 | - | 1055 | 950 |  |
| english | 60 | 90.5 (87.9-92.9) | 88.3 | 95.0 | 89.4 | 100.0 | 228 | 1589 | 930 |  |
| terse | 60 | 94.2 (92.9-95.6) | 88.3 | 97.9 | 95.6 | 100.0 | 119 | 1384 | 822 |  |
| json | 60 | 93.5 (91.8-95.3) | 87.9 | 87.1 | 97.7 | 100.0 | 285 | 1709 | 986 | valid JSON 60/60 |
| pith_skill | 60 | 88.2 (85.5-90.8) | 91.2 | 67.5 | 95.3 | 100.0 | 109 | 6274 | 3274 | lint-clean 26/60 |
| pith_primer | 59 | 63.3 (57.8-68.7) | 66.5 | 56.4 | 61.9 | 100.0 | 52 | 1460 | 866 | 1 truncated; lint-clean 59/59 |
| null | 60 | 17.1 (15.2-19.1) | 0.0 | 0.0 | 19.7 | 100.0 | - | 807 | 702 |  |

## Paired against english

| arm | pairs | accuracy diff (points) | msg tokens | total tokens |
|---|---:|---|---:|---:|
| terse | 60 | +3.8 (+1.2 to +6.4) | -48% | -13% |
| json | 60 | +3.0 (+0.5 to +5.6) | +25% | +8% |
| pith_skill | 60 | -2.3 (-5.0 to +0.5) | -52% | +295% |
| pith_primer | 59 | -27.3 (-33.0 to -22.0) | -77% | -8% |

## Paired against terse

| arm | pairs | accuracy diff (points) | msg tokens | total tokens |
|---|---:|---|---:|---:|
| english | 60 | -3.8 (-6.4 to -1.2) | +92% | +15% |
| json | 60 | -0.8 (-3.0 to +1.7) | +139% | +23% |
| pith_skill | 60 | -6.1 (-8.8 to -3.2) | -8% | +353% |
| pith_primer | 59 | -30.8 (-36.5 to -25.4) | -56% | +6% |
