---
tags: [pith]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Bash]
---

You're the worker agent. The orchestrator sent the message below about the project in this folder. Answer it the way it expects and save your reply to reply.txt.

```
pith 1
#1 ask node version required by package.json = ?
#2 ask redis url in config/default.json = ?
#3 ask test runner = ?
 not install anything
 not run tests
```

Input files: package.json, config/default.json
