#!/usr/bin/env python3
"""devto_challenge_check.py — Pre-check script for the vigil-triage cron job.

Launches a headless Chromium browser, navigates to https://dev.to/challenges,
and extracts dated challenge slugs from the "Active Challenges" section only.

Compares against a local state file of previously seen slugs:
- If new slugs are found: emits {"wakeAgent": true, "context": {...}} to stdout
- If nothing new or fetch failed: emits {"wakeAgent": false} to stdout

Safety:
- Never overwrites state with empty/partial data (honesty guardrail).
- After a successful run the state file is updated to include all currently
  known slugs, so the next run compares against an up-to-date baseline.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CHALLENGES_URL = "https://dev.to/challenges"
STATE_FILE = Path.home() / ".hermes" / "vigil" / "devto_seen_challenges.json"
BROWSER_TIMEOUT_MS = 30_000  # milliseconds for playwright page.goto / wait_until

# Slug pattern: challenges/<name>-YYYY-MM-DD
# Only dated slugs are tracked; undated landing pages (e.g. /challenges/cloudflare)
# are excluded because they have no stable identity across time.
# (Pattern is embedded in the JS extractor below; defined here for reference.)
SLUG_PATTERN = r"challenges/[a-z0-9][a-z0-9\-]+-\d{4}-\d{2}-\d{2}"

# ---------------------------------------------------------------------------
# JS extractor
# ---------------------------------------------------------------------------

# Injected into the fully-rendered page via page.evaluate().
# Returns {"found_active": bool, "slugs": [...]} so we can distinguish
# "Active Challenges section absent" from "section found but empty".
#
# Strategy:
#   1. Find the first heading whose text contains "active" — that is the
#      start of the Active Challenges section.
#   2. Find the next heading after it whose text contains "previous",
#      "archived", or "past" — that is the boundary where we stop.
#   3. Walk all <a href*="/challenges/"> links on the page and keep only
#      those that follow activeH and precede boundaryH in document order,
#      using compareDocumentPosition (no layout/scroll assumptions).
#   4. Apply the dated-slug filter; return deduped results.

_EXTRACT_JS = r"""
(function() {
  var slugRe = /challenges\/[a-z0-9][a-z0-9-]+-\d{4}-\d{2}-\d{2}/;
  var FOLLOWING = 4; /* Node.DOCUMENT_POSITION_FOLLOWING */

  /* Locate the Active Challenges heading and the first boundary heading
     that follows it (Previous / Archived / Past Challenges). */
  var headings = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6'));
  var activeH   = null;
  var boundaryH = null;

  for (var i = 0; i < headings.length; i++) {
    var text = headings[i].textContent.trim().toLowerCase();
    if (!activeH && text.includes('active')) {
      activeH = headings[i];
    } else if (activeH && !boundaryH &&
               (text.includes('previous') ||
                text.includes('archived') ||
                text.includes('past'))) {
      boundaryH = headings[i];
      break;
    }
  }

  if (!activeH) {
    return {found_active: false, slugs: []};
  }

  /* Collect dated challenge slugs strictly within the Active section. */
  var seen  = {};
  var slugs = [];
  var links = Array.from(document.querySelectorAll('a[href*="/challenges/"]'));

  for (var j = 0; j < links.length; j++) {
    var a = links[j];
    var m = a.href.match(slugRe);
    if (!m) continue;

    /* Link must follow the Active heading in document order. */
    if (!(activeH.compareDocumentPosition(a) & FOLLOWING)) continue;

    /* Link must precede the boundary heading (skip if it follows it). */
    if (boundaryH && (boundaryH.compareDocumentPosition(a) & FOLLOWING)) continue;

    var slug = m[0];
    if (!seen[slug]) {
      seen[slug] = true;
      slugs.push(slug);
    }
  }

  return {found_active: true, slugs: slugs};
})()
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def log(msg: str) -> None:
    """Write a diagnostic line to stderr (never contaminates stdout JSON)."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[devto_challenge_check] {timestamp} {msg}", file=sys.stderr)


def fetch_slugs() -> list[str] | None:
    """Launch a headless Chromium browser, fully render the challenges page,
    and extract dated slugs ONLY from the "Active Challenges" section.

    Returns a sorted list of unique slugs (possibly empty when no active
    challenges are listed), or None on any failure:
    - playwright not installed
    - network / navigation error
    - "Active Challenges" section not found in the rendered page

    None always triggers the honesty guardrail in main(): wakeAgent=false,
    state file untouched.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log("playwright not available; cannot perform browser-rendered fetch")
        return None

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(
                    CHALLENGES_URL,
                    timeout=BROWSER_TIMEOUT_MS,
                    wait_until="networkidle",
                )
                result = page.evaluate(_EXTRACT_JS)
            finally:
                browser.close()
    except Exception as exc:
        log(f"browser fetch failed: {exc}")
        return None

    if not result.get("found_active"):
        log("Active Challenges section not found on rendered page")
        return None

    slugs = sorted(set(result.get("slugs", [])))
    log(f"fetched {len(slugs)} active dated slug(s) from {CHALLENGES_URL}")
    return slugs


def load_seen() -> set[str]:
    """Load the set of already-seen slugs from the state file.
    Returns an empty set if the file does not exist (first run)."""
    if not STATE_FILE.exists():
        log(f"state file not found at {STATE_FILE} — treating as first run")
        return set()
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        seen = set(data.get("seen", []))
        log(f"loaded {len(seen)} previously seen slug(s) from state file")
        return seen
    except Exception as exc:
        log(f"could not read state file ({exc}) — treating as first run")
        return set()


def save_seen(slugs: list[str]) -> None:
    """Persist the full current slug list to the state file.
    Creates parent directories as needed."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "seen": sorted(slugs),
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    STATE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    log(f"state file updated with {len(slugs)} slug(s) at {STATE_FILE}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    # 1. Fetch current active challenges via browser-rendered page
    current_slugs = fetch_slugs()

    if current_slugs is None:
        # Fetch failed or Active section unreadable — safe no-op:
        # do not touch state, do not wake agent.
        log("aborting: fetch failed or Active Challenges section unreadable; wakeAgent=false")
        print(json.dumps({"wakeAgent": False}))
        return

    # 2. Load what we have already seen
    seen = load_seen()

    # 3. Diff: new = in current but not yet in seen
    new_slugs = [s for s in current_slugs if s not in seen]

    if not new_slugs:
        log("no new challenges detected; wakeAgent=false")
        # Still update the state so it stays tidy (catches any slug removals
        # on the page, though we don't act on removals).
        save_seen(current_slugs)
        print(json.dumps({"wakeAgent": False}))
        return

    # 4. New challenges found — build context for the agent
    log(f"found {len(new_slugs)} new challenge(s): {new_slugs}")

    # Update state BEFORE waking agent so a crash/timeout on the agent side
    # doesn't cause the same challenges to be re-triaged on the next tick.
    save_seen(current_slugs)

    context = {
        "new_challenge_slugs": new_slugs,
        "new_challenge_urls": [f"https://dev.to/{slug}" for slug in new_slugs],
        "new_challenge_count": len(new_slugs),
        "all_known_slugs": current_slugs,
        "detected_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "instruction": (
            "New DEV Community challenges have been detected. "
            "Use the triage-challenge skill to evaluate each one. "
            "The new_challenge_urls list contains the direct URLs to visit."
        ),
    }

    print(json.dumps({"wakeAgent": True, "context": context}))


if __name__ == "__main__":
    main()
