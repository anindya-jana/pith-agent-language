"""Benchmark corpus: eight inter-agent exchanges, each written four ways.

english  what a careful agent writes by default
terse    the same facts in telegraphic English (no filler, fragments)
json     the same facts as a structured object
pith     the same facts in Pith 1

Every version of a scenario carries the same facts. A scenario with several
messages lists them in order; counts are summed over the messages.
"""

SCENARIOS = [
    {
        "name": "task brief",
        "english": [
            "I need you to fix a bug in our API. Users have been getting a 500 error when they try to log in, and it started happening right after the deploy of commit 4f2a91c. I think the problem is somewhere in the session handling code, most likely in src/auth/session.ts between lines 40 and 90, but I haven't confirmed that. Please make sure you don't change the public API of the auth module, and do not touch anything in the migrations/ directory. I'd prefer a minimal fix rather than a refactor. When you're done, give me the diff and a one-line explanation of the root cause. The task is complete when `npm test auth` passes. Please don't spend more than about 20 tool calls on this.",
        ],
        "terse": [
            "Fix login 500 in API. Started after deploy 4f2a91c; users locked out. Suspect src/auth/session.ts:40-90, unconfirmed. Don't change auth module public API. Don't touch migrations/. Prefer minimal fix over refactor. Return diff plus one-line root cause. Done when `npm test auth` passes. Max ~20 tool calls.",
        ],
        "json": [
            '{"type":"request","id":1,"task":"fix login 500 error in API","context":"users locked out since deploy 4f2a91c","suspected_location":{"file":"src/auth/session.ts","lines":"40-90","confirmed":false},"constraints":{"must_not":["change auth module public API","touch migrations/"],"prefer":["minimal fix over refactor"]},"output":"diff plus one-line root cause","done_when":"npm test auth passes","budget":"about 20 tool calls"}',
        ],
        "pith": [
            "pith 1\n"
            "#1 do fix login 500\n"
            " why users locked out since deploy 4f2a91c\n"
            " at api\n"
            " not change auth public API\n"
            " not touch migrations/\n"
            " prefer minimal fix, not refactor\n"
            " out diff, 1-line root cause\n"
            " check `npm test auth` pass\n"
            " cap ~20 tool calls\n"
            "guess bug at src/auth/session.ts:40-90",
        ],
    },
    {
        "name": "completion report",
        "english": [
            "I've finished fixing the login bug. The root cause was that the token expiry check in src/auth/session.ts on line 57 used a strict less-than comparison instead of less-than-or-equal, so tokens that expired at exactly the current second were treated as valid and then failed later during the refresh, which raised an unhandled exception. I changed the comparison to `<=` and added a regression test in tests/auth/session.test.ts. I ran `npm test auth` and all 41 tests pass. I didn't run the full test suite, so I can't confirm that nothing else was affected. I'd also suggest looking at src/auth/refresh.ts, since I think it may have the same comparison problem, but I haven't checked it.",
        ],
        "terse": [
            "Login bug fixed. Root cause: token expiry check at src/auth/session.ts:57 used `<` instead of `<=`; tokens expiring at exactly current second passed as valid, then failed in refresh with unhandled exception. Changed to `<=`. Added regression test in tests/auth/session.test.ts. Ran `npm test auth`: 41/41 pass. Full suite not run; other effects unverified. src/auth/refresh.ts may have same comparison bug, not checked.",
        ],
        "json": [
            '{"type":"report","re":1,"status":"done","root_cause":{"file":"src/auth/session.ts","line":57,"description":"token expiry check used < instead of <=; tokens expiring at exactly current second passed as valid, then failed in refresh with unhandled exception"},"changes":["changed comparison to <= at src/auth/session.ts:57","added regression test in tests/auth/session.test.ts"],"verification":{"command":"npm test auth","result":"41/41 pass"},"not_verified":["full test suite not run"],"suggestions":[{"file":"src/auth/refresh.ts","note":"may have same comparison bug","checked":false}]}',
        ],
        "pith": [
            "done #1\n"
            " did edit src/auth/session.ts:57 `<` -> `<=`\n"
            " did add regression test at tests/auth/session.test.ts\n"
            " left full suite not run\n"
            "fact 41/41 pass <- `npm test auth`\n"
            "think cause = expiry check `<`: token expiring at exact current second passed as valid -> refresh threw unhandled exception\n"
            "guess src/auth/refresh.ts has same compare bug",
        ],
    },
    {
        "name": "blocked, needs input",
        "english": [
            "I'm blocked on the database migration task. To run the migration against staging I need the staging database connection string, and the STAGING_DATABASE_URL variable isn't set in the .env file. I checked .env and .env.example and it's missing from both. Could you either give me the connection string, or let me know if I should run the migration against the local database instead? So far I've written the migration file at migrations/0042_add_user_locale.sql, but I haven't been able to run it anywhere.",
        ],
        "terse": [
            "Blocked on DB migration task. Need staging DB connection string: STAGING_DATABASE_URL not set; checked .env and .env.example, missing in both. Provide the string, or should I run against local DB instead? Migration file written at migrations/0042_add_user_locale.sql; not run anywhere yet.",
        ],
        "json": [
            '{"type":"blocked","re":2,"task":"database migration","need":"staging database connection string","reason":"STAGING_DATABASE_URL not set","evidence":"checked .env and .env.example, missing in both","options":["provide the connection string","run against local database instead"],"progress":{"done":["wrote migrations/0042_add_user_locale.sql"],"not_done":["migration not run anywhere"]}}',
        ],
        "pith": [
            "need #2 staging db url, or ok to run at local db\n"
            " did write migrations/0042_add_user_locale.sql\n"
            " left migration not run anywhere\n"
            "fact `STAGING_DATABASE_URL` not set <- .env, .env.example",
        ],
    },
    {
        "name": "question and answer",
        "english": [
            "Can you find out which version of PostgreSQL the production database is running, and whether the pg_trgm extension is installed? I need to know because I'm deciding whether we can use trigram indexes for the search feature. Please don't change anything on the server; this should be read-only.",
            "The production database is running PostgreSQL 15.4. I confirmed this by running `select version()` through psql. The pg_trgm extension is not installed at the moment; it doesn't appear in the output of `\\dx`. However, it is listed in pg_available_extensions, so I believe it could be installed without needing a server upgrade, although I haven't tried it.",
        ],
        "terse": [
            "Find prod PostgreSQL version and whether pg_trgm extension is installed. Purpose: deciding if trigram indexes usable for search. Read-only; change nothing on server.",
            "Prod runs PostgreSQL 15.4 (verified: `select version()` via psql). pg_trgm not installed (absent from `\\dx`). Listed in pg_available_extensions, so probably installable without server upgrade; not tried.",
        ],
        "json": [
            '{"type":"query","id":3,"questions":["production PostgreSQL version","is pg_trgm extension installed"],"purpose":"deciding if trigram indexes can be used for search","constraints":["read-only","change nothing on server"]}',
            '{"type":"answer","re":3,"answers":[{"question":"production PostgreSQL version","value":"15.4","verified":true,"source":"select version() via psql"},{"question":"is pg_trgm extension installed","value":false,"verified":true,"source":"absent from \\\\dx"}],"notes":[{"claim":"pg_trgm installable without server upgrade","verified":false,"basis":"listed in pg_available_extensions"}]}',
        ],
        "pith": [
            "#3 ask postgres version = ?, pg_trgm installed = ?\n"
            " at prod db\n"
            " why decide trigram index for search\n"
            " not change server",
            "fact #3 postgres version = 15.4 <- `select version()` via psql\n"
            "fact #3 pg_trgm not installed <- absent from `\\dx`\n"
            "think pg_trgm installable without server upgrade <- listed in pg_available_extensions",
        ],
    },
    {
        "name": "review findings",
        "english": [
            "I reviewed the pull request and found four issues. First, in src/api/users.ts on line 88 there is a SQL injection vulnerability, because the email parameter is concatenated directly into the query string; this is critical and should be fixed by using a parameterized query. Second, in src/api/users.ts on line 132 the error from the database call is swallowed by an empty catch block, which is a high severity problem; the error should be logged and rethrown. Third, in src/lib/cache.ts on line 41 the cache TTL is hardcoded to 60 seconds, which is a low severity issue; it should be moved into the config. Fourth, in tests/users.test.ts on line 15 the test for the delete endpoint is skipped, which is medium severity; it should be re-enabled or removed with an explanation. I only read the diff; I did not run the code or the tests.",
        ],
        "terse": [
            "PR review: 4 issues. (1) src/api/users.ts:88 critical: SQL injection, email concatenated into query; use parameterized query. (2) src/api/users.ts:132 high: DB error swallowed by empty catch; log and rethrow. (3) src/lib/cache.ts:41 low: cache TTL hardcoded 60s; move to config. (4) tests/users.test.ts:15 medium: delete endpoint test skipped; re-enable or remove with explanation. Read diff only; code and tests not run.",
        ],
        "json": [
            '{"type":"report","re":5,"status":"done","findings":[{"file":"src/api/users.ts","line":88,"severity":"critical","problem":"SQL injection, email concatenated into query","fix":"use parameterized query"},{"file":"src/api/users.ts","line":132,"severity":"high","problem":"DB error swallowed by empty catch","fix":"log and rethrow"},{"file":"src/lib/cache.ts","line":41,"severity":"low","problem":"cache TTL hardcoded 60s","fix":"move to config"},{"file":"tests/users.test.ts","line":15,"severity":"medium","problem":"delete endpoint test skipped","fix":"re-enable or remove with explanation"}],"method":"read diff only; code and tests not run"}',
        ],
        "pith": [
            "done #5\n"
            " left code not run, tests not run\n"
            "fact 4 issues <- read diff\n"
            " tab at | sev | problem | fix\n"
            " | src/api/users.ts:88 | critical | sql injection, email concat into query | use param query\n"
            " | src/api/users.ts:132 | high | db error swallowed by empty catch | log, rethrow\n"
            " | src/lib/cache.ts:41 | low | cache ttl hardcoded 60s | move to config\n"
            " | tests/users.test.ts:15 | medium | delete endpoint test skipped | enable or remove with reason",
        ],
    },
    {
        "name": "plan and approval",
        "english": [
            "Here's my plan for adding rate limiting to the public API. First, I'll add a Redis-backed token bucket middleware in src/middleware/rateLimit.ts. Second, I'll apply it to all routes under /api/v1 with a default limit of 100 requests per minute per API key. Third, I'll add configuration options for the limit and the window to config/default.json. Fourth, I'll write integration tests that cover the limit being exceeded and the limit resetting. The main risk is that Redis becomes a hard dependency for the API; if Redis is down, requests would fail. Do you want me to go ahead?",
            "The plan looks good, go ahead, but with two changes. If Redis is unavailable, the middleware must fail open and let requests through rather than returning errors. Also, please don't apply the limit to the /api/v1/health endpoint.",
        ],
        "terse": [
            "Plan: add rate limiting to public API. 1. Add Redis-backed token bucket middleware in src/middleware/rateLimit.ts. 2. Apply to all /api/v1 routes, default 100 req/min per API key. 3. Add limit and window options to config/default.json. 4. Write integration tests: limit exceeded, limit reset. Risk: Redis becomes hard dependency; Redis down means requests fail. Proceed?",
            "Approved with 2 changes. Redis unavailable: middleware must fail open, let requests through, no errors. Exclude /api/v1/health from limit.",
        ],
        "json": [
            '{"type":"plan","id":6,"goal":"add rate limiting to public API","steps":["add Redis-backed token bucket middleware in src/middleware/rateLimit.ts","apply to all /api/v1 routes, default 100 req/min per API key","add limit and window options to config/default.json","write integration tests: limit exceeded, limit reset"],"risks":["Redis becomes hard dependency; if Redis is down requests fail"],"awaiting_approval":true}',
            '{"type":"approval","re":6,"approved":true,"changes":["if Redis unavailable middleware must fail open and let requests through, no errors","do not apply limit to /api/v1/health"]}',
        ],
        "pith": [
            "#6 plan add rate limit to public api\n"
            " 1 add redis token bucket middleware at src/middleware/rateLimit.ts\n"
            " 2 apply to /api/v1/*, default 100 req/min per api key\n"
            " 3 add limit, window options to config/default.json\n"
            " 4 write integration tests: limit exceeded, limit reset\n"
            "think risk = redis becomes hard dep; redis down -> requests fail\n"
            "ask ok #6?",
            "ok #6\n"
            " must fail open if redis down: pass requests, no error\n"
            " not limit /api/v1/health",
        ],
    },
    {
        "name": "failure report",
        "english": [
            "I wasn't able to complete the deployment to staging. The build step succeeded, but the deploy step failed with the error `Error: ECONNREFUSED 10.0.4.12:443` when the script tried to reach the staging cluster. I retried three times over about five minutes and got the same error each time. I suspect the VPN connection isn't active on this machine, since 10.0.4.12 is a private address, but I have no way to verify that from here. Nothing was changed on staging; the previous version is still running. If you can confirm the VPN is up, I can retry.",
        ],
        "terse": [
            "Staging deploy failed. Build OK. Deploy step error: `Error: ECONNREFUSED 10.0.4.12:443` reaching staging cluster. Retried 3 times over ~5 min, same error. Suspect VPN down on this machine (10.0.4.12 is private); can't verify from here. Staging unchanged, previous version still running. Confirm VPN up and I'll retry.",
        ],
        "json": [
            '{"type":"failure","re":7,"task":"deploy to staging","steps":{"build":"ok","deploy":"failed"},"error":"Error: ECONNREFUSED 10.0.4.12:443","retries":{"count":3,"duration":"about 5 minutes","result":"same error"},"hypothesis":{"claim":"VPN down on this machine","basis":"10.0.4.12 is a private address","verified":false},"side_effects":"none; staging unchanged, previous version still running","next":"confirm VPN is up, then retry"}',
        ],
        "pith": [
            "err #7 deploy staging\n"
            " did build pass\n"
            " did retry deploy 3x over ~5 min -> same error\n"
            " next confirm vpn up -> retry\n"
            "fact deploy step -> \"Error: ECONNREFUSED 10.0.4.12:443\" <- deploy log\n"
            "guess vpn down at agent host <- 10.0.4.12 = private address\n"
            "think staging unchanged, old version still running <- deploy never connected",
        ],
    },
    {
        "name": "four-turn investigation",
        "english": [
            "I'm investigating why the nightly payments reconciliation job (jobs/reconcile_payments.py) has been running slowly. Could you check how long its main query takes against the staging replica database at pg-staging-replica-02.internal:5432/payments? Please only run read-only queries against that database.",
            "I ran the main query from jobs/reconcile_payments.py against pg-staging-replica-02.internal:5432/payments using EXPLAIN ANALYZE, and it took 48.2 seconds. The plan shows a sequential scan on the ledger_entries table, which has about 310 million rows. I think the slowness is caused by a missing index on ledger_entries.settled_at, since the query filters on that column.",
            "Thanks. Can you check whether an index on ledger_entries.settled_at exists in production, and also confirm whether it is missing from pg-staging-replica-02.internal:5432/payments? Please don't create the index yourself; I want to add it through a migration.",
            "I can't check production because I don't have credentials for it. On pg-staging-replica-02.internal:5432/payments I confirmed there is no index on ledger_entries.settled_at; I looked at the output of `\\d ledger_entries`. I only ran read-only commands and haven't created anything.",
        ],
        "terse": [
            "Investigating slow nightly payments reconciliation job (jobs/reconcile_payments.py). Time its main query on staging replica pg-staging-replica-02.internal:5432/payments. Read-only queries only.",
            "Main query of jobs/reconcile_payments.py on pg-staging-replica-02.internal:5432/payments: 48.2s (EXPLAIN ANALYZE). Plan: sequential scan on ledger_entries, ~310M rows. Likely cause: missing index on ledger_entries.settled_at; query filters on it.",
            "Check: does index on ledger_entries.settled_at exist in prod? Confirm missing on pg-staging-replica-02.internal:5432/payments? Don't create index; will add via migration.",
            "Can't check prod: no credentials. pg-staging-replica-02.internal:5432/payments: no index on ledger_entries.settled_at (from `\\d ledger_entries`). Read-only commands only; created nothing.",
        ],
        "json": [
            '{"type":"query","id":1,"question":"how long does the main query take","job":"jobs/reconcile_payments.py","database":"pg-staging-replica-02.internal:5432/payments","purpose":"investigating slow nightly payments reconciliation job","constraints":["read-only queries only"]}',
            '{"type":"answer","re":1,"job":"jobs/reconcile_payments.py","database":"pg-staging-replica-02.internal:5432/payments","value":"48.2s","verified":true,"source":"EXPLAIN ANALYZE","observations":["plan shows sequential scan on ledger_entries, about 310M rows"],"hypothesis":{"claim":"slow because of missing index on ledger_entries.settled_at","basis":"query filters on that column","verified":false}}',
            '{"type":"query","questions":[{"id":2,"question":"does index on ledger_entries.settled_at exist","database":"production"},{"id":3,"question":"does index on ledger_entries.settled_at exist","database":"pg-staging-replica-02.internal:5432/payments"}],"constraints":["do not create the index; will be added via migration"]}',
            '{"type":"answer","answers":[{"re":2,"status":"refused","reason":"no production credentials"},{"re":3,"database":"pg-staging-replica-02.internal:5432/payments","value":"no index on ledger_entries.settled_at","verified":true,"source":"\\\\d ledger_entries"}],"actions":"read-only commands only; created nothing"}',
        ],
        "pith": [
            "pith 1\n"
            "$job = jobs/reconcile_payments.py\n"
            "$db = pg-staging-replica-02.internal:5432/payments\n"
            "#1 ask $job main query time at $db = ?\n"
            " why $job nightly run slow\n"
            " not write to $db",
            "fact #1 = 48.2s <- `EXPLAIN ANALYZE` at $db\n"
            "fact seq scan on ledger_entries, ~310M rows <- query plan\n"
            "think slow <- missing index on ledger_entries.settled_at; query filters on settled_at",
            "$col = ledger_entries.settled_at\n"
            "#2 ask index on $col exists at prod = ?\n"
            "#3 ask index on $col exists at $db = ?\n"
            " not create index; migration will add",
            "no #2 <- no prod credentials\n"
            "fact #3 = no index on $col <- `\\d ledger_entries` at $db\n"
            " did read only, created nothing",
        ],
    },
]
