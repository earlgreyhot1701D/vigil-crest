---
name: refresh-stack
description: "Refresh the [GitHub-refreshed] Languages section of stack.md by reading earlgreyhot1701D's public GitHub repos. Updates only that section and the Last refreshed line. Never touches [hand-curated] sections."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vigil, stack, github, refresh]
    related_skills: [triage-challenge]
---

# refresh-stack

Keep the Languages [GitHub-refreshed] section of stack.md current
by reading earlgreyhot1701D's public GitHub repositories directly.

## Trigger

Run this skill on demand or on a schedule (e.g. weekly) to keep the stack
picture fresh. It is safe to run at any time — if anything goes wrong the
file is left completely intact.

## Stack file path

    ~/.hermes/skills/research/triage-challenge/stack.md

## Step 1 — Browse GitHub repositories directly

Navigate to:

    https://github.com/earlgreyhot1701D?tab=repositories

Do NOT use web_search. Search indexes cache stale states.

Let the page render fully. Then extract the primary language tag for every
repository visible on that page using:

    Array.from(document.querySelectorAll('[itemprop="programmingLanguage"]')).map(el => el.textContent.trim()).filter(Boolean)

Collect the distinct set of languages. Order them by frequency (most repos
first), then alphabetically for ties.

## Honesty guardrail — abort conditions

If ANY of the following is true, stop immediately. Do NOT write anything to
stack.md. Report the failure plainly.

- The GitHub page fails to load or returns an error.
- The page loads but shows zero repositories.
- The JS query returns an empty array (no language tags found at all).
- The network is unavailable.

Never overwrite stack.md with empty or partial data. The file must only be
updated when a real, non-empty language list is successfully collected.

## Step 2 — Read the current stack.md

Read the file at the path above. Locate the line that begins:

    Languages [GitHub-refreshed]:

This is the only line (plus any continuation lines) you are allowed to change.

The sections you must NEVER touch:

- Frameworks [hand-curated]
- Cloud and infra [hand-curated]
- Common pieces [hand-curated]
- Build tools [hand-curated]
- Ecosystem range [hand-curated]
- The comment block at the top of the file
- All section headers and their markers

## Step 3 — Update the file

Make exactly two changes and nothing else:

1. Replace the "Languages [GitHub-refreshed]:" line (and any
   continuation lines that belong to it) with the freshly collected language
   list. Format as a single line if it fits; wrap to a second line only if
   the list is long. End at the blank line before the next section — do not
   bleed into adjacent sections.

   Example output line:

       Languages [GitHub-refreshed]: Python, TypeScript, JavaScript, HTML.

   Note: GitHub language tags show primary languages only. They do not
   confirm frameworks (React, Next.js, etc.). Do not add or remove
   framework names based on GitHub data — those belong in the hand-curated
   sections. List only the raw language names GitHub reported.

2. Replace the "Last refreshed:" line with today's date in this format:

       Last refreshed: <Month D YYYY> — auto-refreshed from GitHub.

   Example:

       Last refreshed: May 24 2026 — auto-refreshed from GitHub.

Use the patch tool (targeted find-and-replace) rather than rewriting the
whole file, to minimise the risk of accidentally disturbing other sections.

## Step 4 — Confirm

After writing, read the file back and confirm:

- The [GitHub-refreshed] line contains the new language list.
- All four [hand-curated] sections are byte-for-byte unchanged.
- The Last refreshed line shows today's date.
- The comment block at the top is intact.

Report what changed and what was left untouched.

---

## Worked Example — May 24 2026

GitHub page loaded successfully.

Repos visible on first page: vigil-crest (no tag), Clew-Labs (HTML),
themis-lex (TypeScript), petit-mot (JavaScript), vidi-clew (no tag),
Clew-Directive (Python), readme-clew (TypeScript), steep (JavaScript),
and more.

Raw language tags collected (via JS query):

    ["HTML", "TypeScript", "JavaScript", "Python", "TypeScript",
    "JavaScript", "Python", "TypeScript", "TypeScript", "TypeScript",
    "TypeScript", "JavaScript", "TypeScript", "JavaScript", "TypeScript",
    "Python", "Python", "Python", "Python", "Python", "Python", "Python",
    "Python", "Python"]

Distinct set, frequency order: Python (10), TypeScript (8),
JavaScript (4), HTML (1).

Updated line:

    Languages [GitHub-refreshed]: Python, TypeScript, JavaScript, HTML.

Updated footer:

    Last refreshed: May 24 2026 — auto-refreshed from GitHub.
