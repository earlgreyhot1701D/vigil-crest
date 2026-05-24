# vigil-triage Cron Job — Setup Reference

Created: 2026-05-24

## Job Record

Job ID:     c9cdffb982a6
Name:       vigil-triage
Schedule:   0 8 * * 1,4  (Monday + Thursday, 08:00 UTC)
Script:     devto_challenge_check.py
Skills:     triage-challenge
Toolsets:   browser, web
Deliver:    telegram (home channel)
State:      scheduled, enabled

## Pre-Check Script

Location: /home/ubuntu/.hermes/scripts/devto_challenge_check.py
State file: /home/ubuntu/.hermes/vigil/devto_seen_challenges.json

What it does:

- Launches headless Chromium via playwright
- Navigates to https://dev.to/challenges
- Runs JS extractor to collect dated challenge slugs from the Active Challenges
  section only (slug pattern: challenges/<name>-YYYY-MM-DD)
- Diffs against the state file (seen slugs from previous runs)
- If new slugs found: emits wakeAgent=true with context payload
- If nothing new or fetch failed: emits wakeAgent=false

Context payload fields when wakeAgent=true:

    new_challenge_slugs   list of new slug strings
    new_challenge_urls    list of https://dev.to/<slug> URLs
    new_challenge_count   integer
    all_known_slugs       full current list
    detected_at           ISO timestamp
    instruction           human-readable task summary string

Safety: state is updated BEFORE emitting wakeAgent=true, so an agent crash
does not cause re-triage of the same challenges on the next tick.

## First Test Run — 2026-05-24

Ran via cronjob(action='run', job_id='c9cdffb982a6').

Result: wakeAgent=false (all current challenges already in state file from
prior manual triage session).

Log evidence:

    17:10:52 INFO cron.scheduler: Job 'vigil-triage' (ID: c9cdffb982a6): wakeAgent=false, skipping agent run
    17:10:52 INFO cron.scheduler: Job 'c9cdffb982a6': agent returned [SILENT] — skipping delivery

Agent stayed asleep. No tokens consumed. No Telegram message sent.

last_status: ok

## Second Test Run — 2026-05-24 (state file deleted before run)

State file was manually deleted: ~/.hermes/vigil/devto_seen_challenges.json removed.

Ran via cronjob(action='run', job_id='c9cdffb982a6').

Result: wakeAgent=false AGAIN.

Log evidence:

    17:13:52 INFO cron.scheduler: Job 'vigil-triage' (ID: c9cdffb982a6): wakeAgent=false, skipping agent run
    17:13:52 INFO cron.scheduler: Job 'c9cdffb982a6': agent returned [SILENT] — skipping delivery

Output file (~/.hermes/cron/output/c9cdffb982a6/2026-05-24_17-13-52.md):
"Script gate returned `wakeAgent=false` — agent skipped."

State file after run: STILL ABSENT (nothing written to vigil/).

Root cause investigation: The scheduler's _run_job_script() discards stderr on
success. The [devto_challenge_check] diagnostic lines are NOT available in any
log file. The script ran, exited 0, emitted {"wakeAgent": false} — but why is
unknown from log evidence alone. User confirmed the script finds 4 slugs when
run manually from shell. Most likely: the page JS extractor failed to locate the
"Active Challenges" heading in the headless browser context (possibly a
dynamic-rendering or timing issue), causing fetch_slugs() to return None,
which short-circuits to wakeAgent=false with no state file write.

Key lesson: pre-check script stderr is permanently discarded on success.
To debug "why false?", run the script manually:
    python3 ~/.hermes/scripts/devto_challenge_check.py

## Cron Prompt (stored)

The pre-check script has detected new DEV Community challenges. A context
payload is injected above this prompt containing:

- new_challenge_urls: direct URLs to the new challenges
- new_challenge_slugs: their slugs
- instruction: a short summary of the task

Follow the instruction from the context payload. Use the triage-challenge
skill to evaluate each new challenge. Deliver the resulting verdict digest
to the Telegram home channel.

If after visiting the challenge URLs you find nothing genuinely worth
reporting (challenge already closed, page unreadable, no actionable
information), start your response with [SILENT] and nothing will be sent.
Otherwise produce the full triage digest.
