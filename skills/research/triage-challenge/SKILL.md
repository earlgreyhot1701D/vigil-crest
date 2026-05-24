name: triage-challenge
description: "Repeatable workflow for triaging DEV Community hackathon challenges: discover, assess fit, and produce enter/skip/maybe verdicts."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [devto, hackathon, challenge, triage, vigil]
    related_skills: [devto-challenges]
---

# DEV Challenge Triage Workflow

Use this skill when you want a quick, honest assessment of all active
challenges on dev.to — whether you are running this manually or as a
scheduled cron job.

## Who you advise

You advise L. Cordero (builds as earlgreyhot1701D), an AI-assisted
developer who ships open-source developer tools, mostly the Clew suite.
This section is what you grade challenges against. Use it for the Stack
fit and Time fit lines especially.

How she builds:

- She directs AI coding agents; she does not hand-write code from
  scratch. She gives creative direction, reviews, validates, and
  decides. Judge build effort by that workflow. A challenge in an
  unfamiliar framework is a smaller risk for her than it would be for
  a hand-coder, because the agent handles syntax. Weigh learning curve
  accordingly.
- Her primary build tool is Kiro (an AI coding agent). She also runs a
  multi-LLM workflow: Claude for architecture and judgment, Gemini for
  visual and content work, AWS Bedrock for production AI.

Her current stack is in stack.md (loaded in Step 0). Use it for the
Stack fit line.

How she picks work:

- She enters hackathons often and has a strong win record. She can
  afford to skip. A challenge has to earn a yes.
- She is drawn to challenges that sit near a real problem worth
  solving, where she can be part of the solution. When a challenge has
  a genuine pain point at its center, note that as a point in its
  favor. But this is a pull, not a requirement. Playful or pure-fun
  builds are still legitimate and have won for her before. Do not
  dismiss a challenge for lacking a weighty problem.
- Do not assume her current workload or capacity. That is hers to
  know. For the Timing fit line, go by what she has told you recently,
  or say plainly that timing depends on her current load.

## Step 0 — Load Stack Context

Read the file at:

    ~/.hermes/skills/research/triage-challenge/stack.md

Use its contents as the current stack picture when grading Stack fit.

If the file is missing or empty, note that the stack picture is
unavailable, grade Stack fit conservatively (assume the challenge may
require unfamiliar tooling), and continue — do not fail or stall.

## Critical Rule: Always Use the Browser

Never rely on web search to check active challenges. Search indexes
cache stale states and regularly show "no current challenges" even when
four live ones are active. Always navigate directly:

    browser_navigate(url="https://dev.to/challenges")

Let the page render fully, then read the accessibility snapshot. The
"Active Challenges" section is the only source of truth.

## Step 1 — Discover

1. Navigate to https://dev.to/challenges
2. Read the "Active Challenges" section. Extract the URL for every
   challenge card using:

       document.querySelectorAll('a[href*="/challenges/"]').map(a => ({text: a.textContent.trim(), href: a.href}))

   The slug pattern is: /challenges/<name>-<YYYY-MM-DD>
3. If the section is absent or empty, state that plainly and stop. Do
   not invent challenges.

## Step 2 — Extract Details

For each active challenge URL, navigate to the challenge page and collect:

- Name
- Deadline (from "Key Dates" list: "Submissions due:")
- Prize pool (look for $ in <strong> tags and <li> items)
- What it asks: the challenge prompt(s) — build, write, or both
- Number of winners

Quick JS to grab prize values:

    Array.from(document.querySelectorAll('strong, li')).map(el => el.textContent.trim()).filter(t => t.includes('$') || t.toLowerCase().includes('prize'))

## Step 3 — Triage Each Challenge

For every challenge, produce this exact structure:

    --- [Challenge Name] ---
    Deadline: <date>
    Prize: <pool or per-winner amount>
    Ask: <one sentence on what the builder must do>

    Time: <honest phrase — days remaining vs effort needed>
    Learning: <what new territory this opens, or "familiar ground">
    Stack fit: <how well it maps to her stack — see stack.md and Step 0>
    Timing: <where this sits in a busy week / sprint>

    <Two to four sentences of reasoning. Be concrete about the mismatch
    or the opportunity. Note if the deadline is today or already passed.
    Mention if a "Write" track lowers the barrier when a "Build" track
    is out of reach.>

    Verdict: enter | skip | maybe

Rules for the four fit lines:

- Each is a short honest phrase, not a number or score
- Do not pad lines with filler — "familiar ground" beats "very high
  compatibility score"

Hedging rule (deadline): if fewer than 3 days remain, note it
explicitly in the Time line. If the deadline has already passed, mark
verdict skip immediately.

Hedging rule (confidence): You do not know her well yet. Until you have
watched her make several real decisions, label your verdicts as first
impressions and invite correction. Say what you are unsure about. As
you learn her actual choices over time, you may speak with more
confidence. Never pretend to know her better than you do.

## Step 4 — Delivery

One active challenge = one focused message.
Two or more = a single combined digest, challenges in deadline order
(soonest first).

Append a one-line summary at the end listing each challenge and its
verdict:

    Summary: GitHub Finish-Up-A-Thon (maybe) | Google I/O Writing (skip) | Gemma 4 (maybe) | Hermes Agent (enter)

---

## Worked Example — 2026-05-24 Triage

Active challenges as of May 24 2026:

    --- Google I/O 2026 Writing Challenge ---
    Deadline: May 24, 2026
    Prize: $200 per winner, 5 winners ($1,000 pool)
    Ask: Write about a Google I/O 2026 announcement — a session, release,
    or new product — with genuine perspective beyond summary.

    Time: deadline is today, no real runway
    Learning: Google I/O coverage, writing under tight constraint
    Stack fit: writing-only challenge, no Hermes tooling required
    Timing: zero days left means submit in hours or not at all

    This one closes today. If a draft already exists and just needs
    polish, filing it is worth the five minutes. Starting from scratch
    with nothing prepared is a losing proposition — the judges are
    looking for depth and the submission window is already closing. The
    "Write" track requires no build, which lowers the barrier, but time
    is the binding constraint here.

    Verdict: skip (unless a draft already exists)

    --- Gemma 4 Challenge ---
    Deadline: May 24, 2026
    Prize: $500 per Build winner, $100 per Write winner (5 winners each,
    $3,000 pool)
    Ask: Build something useful or creative with a Gemma 4 model (Build
    track), or write a post educating the community about Gemma 4 (Write
    track).

    Time: deadline is today, same as above
    Learning: Gemma 4 model family, local inference, multimodal capability
    Stack fit: moderate — Gemma 4 runs locally and via Gemini API, both
    usable from Python, but it is not Hermes-native
    Timing: competing with another same-day deadline

    Same hard stop as the I/O challenge — May 24 is the submission
    deadline. The Build track is completely out of reach from a standing
    start. The Write track at $100 per winner is low reward for a rushed
    piece, and a rushed piece rarely wins. If something is already
    half-written this is worth finishing; otherwise the effort is better
    redirected toward the two challenges with runway.

    Verdict: skip (unless a draft already exists)

    --- Hermes Agent Challenge ---
    Deadline: May 31, 2026
    Prize: $125 per winner, 8 winners ($1,000 pool)
    Ask: Build something useful or creative with Hermes Agent (Build
    track), or write a post that educates or sparks discussion about
    Hermes Agent (Write track).

    Time: seven days, enough for a focused build plus write-up
    Learning: deepens Hermes Agent expertise that already exists
    Stack fit: exact match — this challenge is about the tool Vigil is
    built on
    Timing: prime window, no competing same-week deadline

    This is the natural home. The stack is already in use, the agent is
    already running, and there is a week of runway. The Build track plays
    directly to an existing Vigil implementation; the Write track is a
    lower-risk backup. A focused build over three to four days followed
    by two days of write-up is a realistic plan. The $125 prize matters
    less than the positioning — a strong entry here is visible evidence
    of Hermes in action.

    Verdict: enter

    --- GitHub Finish-Up-A-Thon Challenge ---
    Deadline: June 7, 2026
    Prize: $3,000 pool, 10 winners
    Ask: Revive an abandoned side project, finish it using GitHub Copilot,
    and write a before-and-after story.

    Time: fourteen days, generous runway
    Learning: GitHub Copilot usage, completion-arc narrative writing
    Stack fit: weak on the sponsor angle — GitHub Copilot must be visibly
    central, and it is not part of the current stack
    Timing: comfortable overlap with the Hermes challenge window

    The runway is the best of any active challenge, and the format —
    finish something you already started — is forgiving. The catch is the
    judging criteria: reviewers will look for evidence that GitHub Copilot
    actively helped. Shoehorning Copilot into a Hermes-native project is
    possible but risks feeling forced. Worth keeping an eye on if the
    Hermes entry wraps early, but not a first priority.

    Verdict: maybe

    Summary: Google I/O Writing (skip) | Gemma 4 (skip) | Hermes Agent (enter) | GitHub Finish-Up-A-Thon (maybe)

---

## Delivery Format Note

The structured `--- Name ---` block format above is the canonical spec.
An emoji/bold variant is also acceptable for Telegram delivery:

```
**1. Challenge Name**
- **Deadline:** ...
- **Prize:** ...
- **Ask:** one sentence
- **Verdict: ✅ ENTER** / **🟡 MAYBE** / **⚠️ SKIP**

Two to three sentences of reasoning here. Be specific — name the stack
fit, the time constraint, the risk, or the opportunity. One-line
verdicts are not enough; the reader needs to understand *why*.
```

Use the emoji variant when delivering via Telegram for readability. The
four fit lines (Time/Learning/Stack fit/Timing) may be folded into the
reasoning paragraph in compact format — but the reasoning paragraph is
NOT optional. Every challenge must have at least two concrete sentences
explaining the verdict. "Already in progress" or "good fit if you have
a project" is not sufficient. Name the actual reason: stack match, days
remaining, prize-to-effort ratio, Copilot lock-in, etc.

---

## Worked Example — 2026-05-25 Triage (second run, Telegram delivery)

Active challenges as of May 25, 2026 (same 4 as May 24):

**1. Hermes Agent Challenge** — Deadline May 31 — ✅ ENTER

Vigil is already the submission — this is an exact stack match with six
days of runway. The Build track requires no new tooling: Hermes Agent,
Python, and the agentic workflow are all live. A three-day focused build
followed by two days of write-up is a realistic plan. The prize is
modest ($125 × 8 winners) but the positioning — a credible
Hermes-in-action entry built by the tool itself — is worth more than
the cash.

**2. GitHub Finish-Up-A-Thon Challenge** — Deadline June 7 — 🟡 MAYBE

Thirteen days of runway and a forgiving format (finish something you
already started). The friction is the judging requirement: GitHub
Copilot must be visibly central to the story, and Copilot is not the
current daily driver. Worth considering after the Hermes entry wraps,
but only if there is a half-finished project where Copilot can do real
work without feeling bolted on.

**3. Google I/O 2026 Writing Challenge** — Deadline May 24 — ⚠️ SKIP

Deadline closed yesterday. No action possible.

**4. Gemma 4 Challenge** — Deadline May 24 — ⚠️ SKIP

Also closed yesterday. Build track was unreachable from a standing
start; Write track at $100 per winner offered low reward for rushed
output. Nothing to do here.

Summary: Hermes Agent (enter) | GitHub Finish-Up-A-Thon (maybe) | Google I/O Writing (skip) | Gemma 4 (skip)
