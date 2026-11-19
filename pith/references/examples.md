# Pith 1 worked examples

Each example shows the prose an agent would normally write, the Pith for the same facts, and a
note on the choices. Token counts are `o200k_base`. Read this file when you want a pattern to
copy for a message type you have not written before.

## Contents

1. Task brief
2. Completion report
3. Blocked
4. Question and answer
5. Review findings in a table
6. Plan and amended approval
7. Failure report
8. Several turns with handles
9. Common mistakes, corrected

## 1. Task brief

Prose (156 tokens):

> I need you to fix a bug in our API. Users have been getting a 500 error when they try to log in,
> and it started happening right after the deploy of commit 4f2a91c. I think the problem is
> somewhere in the session handling code, most likely in src/auth/session.ts between lines 40 and
> 90, but I haven't confirmed that. Please make sure you don't change the public API of the auth
> module, and do not touch anything in the migrations/ directory. I'd prefer a minimal fix rather
> than a refactor. When you're done, give me the diff and a one-line explanation of the root
> cause. The task is complete when `npm test auth` passes. Please don't spend more than about 20
> tool calls on this.

Pith (82 tokens):

```pith
pith 1
#1 do fix login 500
 why users locked out since deploy 4f2a91c
 at api
 not change auth public API
 not touch migrations/
 should minimal fix, not refactor
 out diff, 1-line root cause
 check `npm test auth` pass
 cap ~20 tool calls
guess bug at src/auth/session.ts:40-90
```

The sender's hunch about the location is a separate `guess`, not part of the brief. The receiver
can see at a glance that it is a lead to test and not a fact to build on.

## 2. Completion report

Prose (147 tokens):

> I've finished fixing the login bug. The root cause was that the token expiry check in
> src/auth/session.ts on line 57 used a strict less-than comparison instead of
> less-than-or-equal, so tokens that expired at exactly the current second were treated as valid
> and then failed later during the refresh, which raised an unhandled exception. I changed the
> comparison to `<=` and added a regression test in tests/auth/session.test.ts. I ran
> `npm test auth` and all 41 tests pass. I didn't run the full test suite, so I can't confirm that
> nothing else was affected. I'd also suggest looking at src/auth/refresh.ts, since I think it may
> have the same comparison problem, but I haven't checked it.

Pith (81 tokens):

```pith
done #1
 did edit src/auth/session.ts:57 `<` -> `<=`
 did add regression test at tests/auth/session.test.ts
 left full suite not run
fact 41/41 pass <- `npm test auth`
think cause = expiry check `<`: token expiring at exact current second passed as valid -> refresh threw unhandled exception
guess src/auth/refresh.ts has same compare bug
```

Three claims, three evidence levels. The test result was observed, so it is a `fact` with the
command as its source. The causal story is reasoning, so it is `think`. The second file was never
opened, so it is `guess`. In the prose all three sit in one paragraph and the reader has to sort
them out.

## 3. Blocked

Prose (103 tokens):

> I'm blocked on the database migration task. To run the migration against staging I need the
> staging database connection string, and the STAGING_DATABASE_URL variable isn't set in the .env
> file. I checked .env and .env.example and it's missing from both. Could you either give me the
> connection string, or let me know if I should run the migration against the local database
> instead? So far I've written the migration file at migrations/0042_add_user_locale.sql, but I
> haven't been able to run it anywhere.

Pith (48 tokens):

```pith
need #2 staging db url, or ok to run at local db
 did write migrations/0042_add_user_locale.sql
 left migration not run anywhere
fact `STAGING_DATABASE_URL` not set <- .env, .env.example
```

`need` leads with exactly what unblocks the work, and offers the alternative in the same line.

## 4. Question and answer

Prose (135 tokens for both messages):

> Can you find out which version of PostgreSQL the production database is running, and whether
> the pg_trgm extension is installed? I need to know because I'm deciding whether we can use
> trigram indexes for the search feature. Please don't change anything on the server; this should
> be read-only.

> The production database is running PostgreSQL 15.4. I confirmed this by running
> `select version()` through psql. The pg_trgm extension is not installed at the moment; it
> doesn't appear in the output of `\dx`. However, it is listed in pg_available_extensions, so I
> believe it could be installed without needing a server upgrade, although I haven't tried it.

Pith (77 tokens for both):

```pith
#3 ask postgres version = ?, pg_trgm installed = ?
 at prod db
 why decide trigram index for search
 not change server
```

```pith
fact #3 postgres version = 15.4 <- `select version()` via psql
fact #3 pg_trgm not installed <- absent from `\dx`
think pg_trgm installable without server upgrade <- listed in pg_available_extensions
```

"I believe ... although I haven't tried it" disappears: `think` says exactly that in one word.

## 5. Review findings in a table

Pith (116 tokens, against 186 in prose):

```pith
done #5
 left code not run, tests not run
fact 4 issues <- read diff
 tab at | sev | problem | fix
 | src/api/users.ts:88 | critical | sql injection, email concat into query | use param query
 | src/api/users.ts:132 | high | db error swallowed by empty catch | log, rethrow
 | src/lib/cache.ts:41 | low | cache ttl hardcoded 60s | move to config
 | tests/users.test.ts:15 | medium | delete endpoint test skipped | enable or remove with reason
```

The column names are written once. `left` states plainly what the review did not cover.

## 6. Plan and amended approval

```pith
#6 plan add rate limit to public api
 1 add redis token bucket middleware at src/middleware/rateLimit.ts
 2 apply to /api/v1/*, default 100 req/min per api key
 3 add limit, window options to config/default.json
 4 write integration tests: limit exceeded, limit reset
think risk = redis becomes hard dep; redis down -> requests fail
ask ok #6?
```

```pith
ok #6
 must fail open if redis down: pass requests, no error
 not limit /api/v1/health
```

The approval reuses the brief slots to amend the plan. Nothing new to learn.

## 7. Failure report

```pith
err #7 deploy staging
 did build pass
 did retry deploy 3x over ~5 min -> same error
 next confirm vpn up -> retry
fact deploy step -> "Error: ECONNREFUSED 10.0.4.12:443" <- deploy log
guess vpn down at agent host <- 10.0.4.12 = private address
think staging unchanged, old version still running <- deploy never connected
```

The error text is in double quotes, so it is carried character for character.

## 8. Several turns with handles

Two long names recur across four messages, so each gets a handle. Agent A opens:

```pith
pith 1
$job = jobs/reconcile_payments.py
$db = pg-staging-replica-02.internal:5432/payments
#1 ask $job main query time at $db = ?
 why $job nightly run slow
 not write to $db
```

Agent B answers:

```pith
fact #1 = 48.2s <- `EXPLAIN ANALYZE` at $db
fact seq scan on ledger_entries, ~310M rows <- query plan
think slow <- missing index on ledger_entries.settled_at; query filters on settled_at
```

Agent A follows up, defining one more handle:

```pith
$col = ledger_entries.settled_at
#2 ask index on $col exists at prod = ?
#3 ask index on $col exists at $db = ?
 not create index; migration will add
```

Agent B:

```pith
no #2 <- no prod credentials
fact #3 = no index on $col <- `\d ledger_entries` at $db
 did read only, created nothing
```

The whole exchange is 188 tokens against 275 in prose and 324 in JSON. `no #2` refuses one
question with its reason and answers the other, and neither can be confused with the other.

## 9. Common mistakes, corrected

**A claim with no evidence level.** Wrong:

```text
done #1
 did fix bug, tests pass
```

"tests pass" is hidden in a `did` slot, so the receiver cannot tell whether the tests were run.
Right:

```pith
done #1
 did fix expiry compare at src/auth/session.ts:57
fact 41/41 pass <- `npm test auth`
```

**A fact with no source.** Wrong: `fact cache is the cause`. Nothing was observed. Right:

```pith
think cause = cache <- error stops when cache disabled
```

**A pronoun.** Wrong: `do update it and restart them`. Right:

```pith
do update nginx config, restart web workers
 check `curl -I https://example.test` -> 200
```

**A handle that does not pay.** Wrong: `$f = a.ts` then one use of `$f`. The definition costs more
than writing `a.ts` twice. Use a handle only for a long value used at least twice.

**Compressing payload.** Wrong: `fact error = econnrefused` when the log said
`Error: ECONNREFUSED 10.0.4.12:443`. The address was the useful part. Right:

```pith
fact deploy -> "Error: ECONNREFUSED 10.0.4.12:443" <- deploy log
```

**Invented abbreviations.** Wrong: `do rfctr auth mw`. It costs more tokens than the real words
and the receiver must guess. Right:

```pith
do refactor auth middleware
 check `npm test auth` pass
```
