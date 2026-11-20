# Handoff accuracy: gemma-4-e4b-it, hops=1

135 graded runs, 0 failed attempts logged in errors.jsonl. Accuracy in %, 95% bootstrap interval over cases. Tokens are the server's own counts.

| arm | n | accuracy | status | constraint | detail | decoy | msg tokens | total tokens | reader prompt | notes |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| oracle | 19 | 100.0 (100.0-100.0) | 100.0 | 100.0 | 100.0 | 100.0 | - | 1066 | 956 |  |
| english | 20 | 92.7 (89.1-95.9) | 83.8 | 95.0 | 93.8 | 100.0 | 247 | 1639 | 955 |  |
| terse | 20 | 85.0 (80.0-90.5) | 55.0 | 81.2 | 97.0 | 100.0 | 116 | 1389 | 825 |  |
| json | 19 | 91.9 (89.0-94.7) | 73.7 | 81.6 | 94.5 | 100.0 | 301 | 1750 | 1006 | valid JSON 19/19 |
| pith_skill | 19 | 90.0 (86.1-93.3) | 98.7 | 80.3 | 87.6 | 100.0 | 114 | 6268 | 3273 | lint-clean 0/19 |
| pith_primer | 19 | 73.7 (64.6-80.9) | 38.2 | 55.3 | 77.9 | 100.0 | 137 | 1630 | 950 | lint-clean 0/19 |
| null | 19 | 12.0 (9.6-14.8) | 0.0 | 2.6 | 5.3 | 100.0 | - | 808 | 706 |  |

## Paired against english

| arm | pairs | accuracy diff (points) | msg tokens | total tokens |
|---|---:|---|---:|---:|
| terse | 20 | -7.7 (-13.2 to -1.8) | -53% | -15% |
| json | 19 | -0.5 (-3.8 to +2.4) | +22% | +7% |
| pith_skill | 19 | -2.4 (-6.2 to +1.0) | -53% | +284% |
| pith_primer | 19 | -18.7 (-27.3 to -11.0) | -44% | -0% |

## Paired against terse

| arm | pairs | accuracy diff (points) | msg tokens | total tokens |
|---|---:|---|---:|---:|
| english | 20 | +7.7 (+1.8 to +13.2) | +113% | +18% |
| json | 19 | +7.2 (+0.5 to +13.9) | +163% | +27% |
| pith_skill | 19 | +5.3 (-0.5 to +11.5) | -0% | +353% |
| pith_primer | 19 | -11.0 (-19.1 to -3.8) | +20% | +18% |
