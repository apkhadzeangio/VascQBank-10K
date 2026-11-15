# VascQBank-10K — Monitoring stage 1 (non-invasive)

The existing 12 independent question-producing chats and their schedules remain unchanged.
The repository's existing hourly README progress updater (approximately :35 Asia/Tbilisi)
is not replaced. Smart Watchdog uses GitHub Actions at :50 each hour and updates ONLY
the separately marked VASCQBANK_MONITORING block, skipping the README push if main
changed during observation. It never overwrites AUTOMATION_CONTEXT.json or topic TXT.

## 1. What counts as evidence?

- Validated new Git commit touching a topic proves production, not that a ChatGPT task is live.
- STARTED / WRITING / QA / COMMITTING means IN_PROGRESS only with a fresh (<90 min)
  actual heartbeat signal. COMMITTED only proves success if its SHA is a reachable commit.
- A topic with no genuine heartbeat is INTEGRATION_PENDING and its agent state is UNKNOWN.
- 2 hours without a new commit is an OBSERVATION, not failure.
- PRODUCTION_DELAY requires >=3 hours of stale *explicit active-phase heartbeat* and
  two independent watchdog snapshots with unchanged topic counts.
- Only actual FAILED or BLOCKED heartbeats create corresponding agent alerts.
- INDEX_MISMATCH is alerted only if the same count mismatch persists across two cycles.
- The Quality Gate is syntactic/structural, NOT an independent clinical peer review.

## 2. Integrate one producing agent (future, optional)

Do not change currently running producer prompts in this stage. When authorized to
integrate an agent, append the following **minimal** side-channel instructions to
its prompt without changing generation, numbering, writes, or scheduling:

1. Assign one stable safe agent_id to that producer (e.g. ALI-CHAT-01).
2. For each two-question production cycle generate one unique safe run_id (e.g.
   ALI-20261116T0345-r1); reuse it in stage updates for that same cycle.
3. Dispatch a GitHub Actions event to workflow qbank-heartbeat.yml on branch main
   once at STARTED, optionally at WRITING/QA/COMMITTING, and after verified commit
   at COMMITTED. For a genuine error send FAILED or BLOCKED plus error_code.
4. Include topic, agent_id, run_id, planned_questions, uploaded_questions and verified
   full commit_sha for COMMITTED. Never send a guessed SHA or claim success before readback.
5. Heartbeat dispatch is best-effort: failure to dispatch must never mutate question
   files/index or retry a possibly committed production batch.
6. Do not use GitHub workflow artifacts as a shared counter/lock. Preserve the
   existing atomic three-file producer commit and race-safe main checks.

REST example (use authenticated repo-scoped GitHub API; do not put the token in prompts):

POST https://api.github.com/repos/apkhadzeangio/VascQBank-10K/actions/workflows/qbank-heartbeat.yml/dispatches

Body:

    {
      "ref": "main",
      "inputs": {
        "topic": "ALI",
        "agent_id": "ALI-CHAT-01",
        "run_id": "ALI-20261116T0345-r1",
        "state": "STARTED",
        "planned_questions": "2",
        "uploaded_questions": "0",
        "commit_sha": "",
        "error_code": ""
      }
    }

GitHub Actions upload-artifact stores a new immutable per-dispatch JSON signal
as qbank-hb-<GitHub run id>. No shared repository file or shared index is rewritten.
The watchdog samples recent artifacts. Historical absence is UNKNOWN, not BLOCKED.

## 3. Automatic controls

- qbank-quality.yml: post-commit check for topic TXT/index/source changes; 12-topic
  validation and Python synthetic fixtures; JSON/Markdown report artifact.
  This is informative CI, not branch protection and never rolls back a commit.
- qbank-watchdog.yml: independent hourly observer; verifies git history, 24-hour
  increase, index synchronization, last Quality Gate run, and available heartbeat.
  Uploads a report artifact, manages one GitHub Issue per confirmed problem,
  and attempts a fast-forward-only README monitoring block commit.
- qbank-heartbeat.yml: manual/API dispatch receiver; no cron; no production agent
  is automatically considered connected merely because the receiver exists.

Alert codes: PRODUCTION_DELAY, AGENT_BLOCKED, AGENT_FAILED, QA_FAILED,
INDEX_MISMATCH, COMMIT_CONFLICT, SOURCE_UNAVAILABLE, and RECOVERED (closing an
existing issue). An existing issue is updated/closed, not duplicated hourly.

## 4. Limitations and next stage

- This control does not inspect ChatGPT Scheduled Tasks belonging to another account.
- At stage 1 all unintegrated agents remain UNKNOWN, even if their content has grown.
- Heartbeat only starts providing authoritative stage signals AFTER producers explicitly
  dispatch successfully and artifacts are observed.
- GitHub Actions might be disabled or require account/repo-level permissions.
- To verify installation: open GitHub Actions, inspect the first Structural Quality
  Gate run; use Run workflow for the Watchdog and inspect its JSON artifact/README.
- Do not turn on mandatory branch protection, scheduled retries, automated rollback,
  or automatic question rewriting as a result of these reports.

Priority: production continuity > data integrity > validation > monitoring >
automated recovery.
