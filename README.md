<p align="center">
  <img src="logo.png" alt="Vigil Crest logo" width="200">
</p>

# Vigil Crest

## The problem

If you enter hackathons, every new challenge is a small decision with a real cost. Enter the wrong one and you burn days you cannot get back. But you cannot tell from a challenge page alone whether it fits your stack, whether there is enough runway left, or whether the learning is worth it.

The DEV Community challenge feed does not sort itself by *worth your time*. So you either check it obsessively, miss things, or enter on a hunch and regret it.

## What Vigil Crest does about it

Vigil Crest is a dev.to challenge triage agent you talk to on Telegram. You message it, it browses the live challenge feed, and it sends back an honest verdict on each active challenge: *is this worth entering?*

It grades every challenge against the stack you actually build with and the way you actually pick work. And it is honest about its own confidence. Early on it calls its verdicts *first impressions* and invites correction. It gets better at reading your judgment the more you check in. A verdict that knows how sure it is beats a confident guess.

Built on Hermes Agent and AWS Bedrock for the DEV Hermes Agent Challenge.

## What it does

Vigil Crest looks at the DEV Community challenge feed and answers one question for each active challenge: *is this worth entering?*

For every challenge it produces four short, honest fit lines and a verdict:

- **Time** — days remaining versus the effort the challenge needs
- **Learning** — what new ground it opens, or whether it is familiar
- **Stack fit** — how well it maps to the stack you actually build with
- **Timing** — where it sits relative to whatever else is going on

Then a short reasoning paragraph, and a verdict: **enter**, **skip**, or **maybe**.

It does not pretend to know you better than it does. Until it has watched you make several real decisions, it labels its verdicts as first impressions and says what it is unsure about. That hedging is the point, not a limitation.

## How you use it

Vigil Crest is a check-in correspondent, not a broadcast bot. You message it, it triages, and every check-in is a chance for it to learn your taste.

A browser-free nudge runs on a schedule (twice a week) and sends a short reminder to Telegram: *time to check the board*. The triage itself happens when you reply. The nudge prompts the ritual; the conversation does the work.

## How it works

- **Hermes Agent** runs the agent, the persona, the skills, and the schedule.
- **AWS Bedrock** provides the model (Claude Sonnet), via an EC2 instance role so there are no credentials stored on the box.
- **Telegram** is the interface. You talk to Vigil Crest like any contact.
- **The triage skill** browses dev.to/challenges live and reads the active challenges section directly. It never relies on cached search results.
- **A stack file** is the single source of truth for stack-fit grading. Its Languages section refreshes automatically from public GitHub repos; the framework, cloud, and tooling sections are hand-curated, because GitHub language tags cannot verify those. The file is marked by provenance so it is always clear which is which.

## Architecture

```
You --message--> Telegram --> Hermes gateway (on EC2)
                                    |
                                    v
                           triage-challenge skill
                                    |
                   browses dev.to/challenges (live)
                                    |
                           grades against stack.md
                                    |
                                    v
                      hedged verdict --> Telegram --> You
```

A scheduled nudge runs separately and only sends a reminder message. It does not browse or triage.

## Setup

Vigil Crest is not a clone-and-run app. It is a configured Hermes instance. Running your own means supplying your own Hermes install, model connection, and Telegram bot. What this repo gives you is the recipe and the portable parts.

1. Install Hermes Agent and run the setup wizard. Choose a model provider (this build uses AWS Bedrock with an IAM instance role).
2. Connect a Telegram bot and set your home channel.
3. Drop the skills from `skills/` into your Hermes skills directory.
4. Copy `SOUL.md` and `stack.md` as templates and edit them to be *you*. The tool grades against one specific person, so the persona and stack must be yours, not the author's.
5. Schedule the nudge cron job.

See the build guide for the full walkthrough.

## What is shareable

The portable layer is the skills, the persona and stack templates, and the build guide. The skills are just files and drop into any Hermes install. `SOUL.md` and `stack.md` are templates: every user supplies their own, because Vigil Crest grades against one person's judgment and stack.

## Known limitations

- **The autonomous triage cron is not shipped.** A scheduled job that browses the feed unattended hit a real wall: a headless browser is environment-sensitive and does not launch reliably inside a background scheduler. The shipped design is the check-in correspondent plus a browser-free nudge, which is arguably the better fit for an agent whose value is learning your judgment. A fully autonomous version is a v2 item.
- **Stack detection is partial.** The Languages section is verified from GitHub; frameworks, cloud, and tooling are hand-curated. Verifying those automatically needs deeper repo data and is a v2 item.

## Roadmap (v2)

- API-based pre-check to replace the browser scrape, so an autonomous scheduled triage becomes reliable.
- Deeper stack detection from repo dependency files.
- A brief "working on it" acknowledgement during interactive triage.

## License

Apache 2.0.

---

*AI assisted. Human approved. Powered by NLP.*
