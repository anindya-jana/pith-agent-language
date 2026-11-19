# Pith 1 benchmark

Token counts for eight inter-agent exchanges (14 messages), each written four ways with the same facts. Source: `bench/corpus.py`. Regenerate: `python bench/bench.py --write`.

Negative percentages mean Pith used fewer tokens. The tokenizers are OpenAI's, used as a proxy; Claude's tokenizer gives different absolute numbers. This measures size only, not how accurately a receiver decodes the message.

### o200k_base

| scenario | english | terse | json | pith | vs english | vs terse | vs json |
|---|---:|---:|---:|---:|---:|---:|---:|
| task brief | 156 | 77 | 105 | 82 | -47% | +6% | -22% |
| completion report | 147 | 96 | 136 | 81 | -45% | -16% | -40% |
| blocked, needs input | 103 | 62 | 85 | 48 | -53% | -23% | -44% |
| question and answer | 135 | 82 | 140 | 77 | -43% | -6% | -45% |
| review findings | 186 | 111 | 156 | 116 | -38% | +5% | -26% |
| plan and approval | 172 | 121 | 140 | 113 | -34% | -7% | -19% |
| failure report | 130 | 86 | 118 | 88 | -32% | +2% | -25% |
| four-turn investigation | 275 | 201 | 324 | 188 | -32% | -6% | -42% |
| **total** | 1304 | 836 | 1204 | 793 | -39% | -5% | -34% |

First-contact primer: 103 tokens, sent once per peer.

### cl100k_base

| scenario | english | terse | json | pith | vs english | vs terse | vs json |
|---|---:|---:|---:|---:|---:|---:|---:|
| task brief | 160 | 78 | 103 | 81 | -49% | +4% | -21% |
| completion report | 152 | 96 | 131 | 81 | -47% | -16% | -38% |
| blocked, needs input | 108 | 62 | 83 | 48 | -56% | -23% | -42% |
| question and answer | 136 | 79 | 134 | 76 | -44% | -4% | -43% |
| review findings | 183 | 109 | 153 | 116 | -37% | +6% | -24% |
| plan and approval | 178 | 120 | 136 | 113 | -37% | -6% | -17% |
| failure report | 132 | 88 | 116 | 88 | -33% | +0% | -24% |
| four-turn investigation | 278 | 201 | 318 | 186 | -33% | -7% | -42% |
| **total** | 1327 | 833 | 1174 | 789 | -41% | -5% | -33% |

First-contact primer: 103 tokens, sent once per peer.

