---
tags: [pith]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I'm about to hand a task to a subagent and want the brief in pith so it's short. The task: tests/payments/refund.test.ts fails maybe 1 run in 5 on CI, never locally. Probably a race in the mock clock but nobody has checked. The subagent must not edit anything under src/billing/ (another team owns it) and shouldn't just bump timeouts. I want back the root cause and a patch. It's done when the test passes 20 runs in a row with `npx jest tests/payments/refund.test.ts --runInBand`. Keep it under 30 tool calls. Save the brief to brief.txt.
