"""
Pulls contribution + language data from the GitHub GraphQL API and renders
stats.svg (hero total + weekly sparkline), streak.svg (current/longest
streak), and langs.svg (top languages by bytes).

Stdlib only -- no dependencies to break in CI. Run inside the refresh-stats
workflow, where GITHUB_TOKEN and GH_LOGIN are already in the environment.

Two determinism traps this script exists specifically to avoid:
  1. The contribution window is pinned to whole UTC days (from = today-364
     at 00:00:00Z, to = today at 23:59:59Z). Left to "the past year" from
     request time, two runs minutes apart bucket days into different weeks
     and the sparkline shifts by a fraction of a pixel every night.
  2. repositories(...) is filtered to privacy: PUBLIC. A personal token run
     locally sees private repos; the workflow's GITHUB_TOKEN doesn't --
     without the filter, language percentages disagree depending on who
     ran the script, and you get merge conflicts against the workflow's
     own commits.
"""
import datetime as dt
import json
import os
import sys
import urllib.request

from stats_common import font_face_block
from stats_render import render_hero, render_streak, render_langs

API_URL = "https://api.github.com/graphql"

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node { name color }
          }
        }
      }
    }
  }
}
"""


def graphql(token, login, from_iso, to_iso):
    body = json.dumps({
        "query": QUERY,
        "variables": {"login": login, "from": from_iso, "to": to_iso},
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": login,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    if "errors" in payload:
        print("GraphQL errors:", json.dumps(payload["errors"], indent=2), file=sys.stderr)
        sys.exit(1)

    return payload["data"]["user"]


def pinned_window():
    """Whole-UTC-day window: [today-364 00:00:00Z, today 23:59:59Z]."""
    today = dt.datetime.now(dt.timezone.utc).date()
    start = today - dt.timedelta(days=364)
    from_iso = f"{start.isoformat()}T00:00:00Z"
    to_iso = f"{today.isoformat()}T23:59:59Z"
    return from_iso, to_iso, today


def flatten_days(calendar):
    days = []
    for week in calendar["weeks"]:
        days.extend(week["contributionDays"])
    days.sort(key=lambda d: d["date"])
    return days


def weekly_totals(calendar):
    return [sum(d["contributionCount"] for d in w["contributionDays"])
            for w in calendar["weeks"]]


def compute_streaks(days, today):
    """Returns (current, current_range, longest, longest_range)."""
    longest, longest_start, longest_end = 0, None, None
    run, run_start = 0, None

    for d in days:
        if d["contributionCount"] > 0:
            if run == 0:
                run_start = d["date"]
            run += 1
            if run > longest:
                longest = run
                longest_start, longest_end = run_start, d["date"]
        else:
            run = 0

    # Current streak: walk backward from the end. If the very last day is
    # today and has zero contributions yet, that's expected (the day isn't
    # over) -- skip it rather than treating it as a break.
    idx = len(days) - 1
    if idx >= 0 and days[idx]["date"] == today.isoformat() and days[idx]["contributionCount"] == 0:
        idx -= 1

    current, current_end = 0, None
    while idx >= 0 and days[idx]["contributionCount"] > 0:
        if current_end is None:
            current_end = days[idx]["date"]
        current += 1
        idx -= 1
    current_start = days[idx + 1]["date"] if current > 0 else None

    def date_range(start, end):
        if not start:
            return ""
        if start == end:
            return dt.date.fromisoformat(start).strftime("%b %-d, %Y")
        s, e = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
        if s.year == e.year:
            return f'{s.strftime("%b %-d")} - {e.strftime("%b %-d, %Y")}'
        return f'{s.strftime("%b %-d, %Y")} - {e.strftime("%b %-d, %Y")}'

    return (current, date_range(current_start, current_end),
            longest, date_range(longest_start, longest_end))


def compute_top_languages(repositories, limit=6):
    totals = {}   # name -> {bytes, color, repos}
    for repo in repositories["nodes"]:
        seen_in_repo = set()
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            color = edge["node"]["color"]
            size = edge["size"]
            entry = totals.setdefault(name, {"bytes": 0, "color": color, "repos": 0})
            entry["bytes"] += size
            if name not in seen_in_repo:
                entry["repos"] += 1
                seen_in_repo.add(name)

    grand_total = sum(v["bytes"] for v in totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda kv: kv[1]["bytes"], reverse=True)[:limit]

    return [
        {
            "name": name,
            "color": v["color"],
            "pct": (v["bytes"] / grand_total) * 100,
            "repo_count": v["repos"],
        }
        for name, v in ranked
    ]


def main():
    token = os.environ["GITHUB_TOKEN"]
    login = os.environ["GH_LOGIN"]

    from_iso, to_iso, today = pinned_window()
    user = graphql(token, login, from_iso, to_iso)

    calendar = user["contributionsCollection"]["contributionCalendar"]
    total = calendar["totalContributions"]
    days = flatten_days(calendar)
    weeks = weekly_totals(calendar)
    current, current_range, longest, longest_range = compute_streaks(days, today)
    langs = compute_top_languages(user["repositories"])

    # --- NEW: Calculate the extra hero stats ---
    active_days = sum(1 for d in days if d["contributionCount"] > 0)
    best_week = max(weeks) if weeks else 0
    # -----------------------------------------

    font_css, fam_reg, fam_bold = font_face_block()

    themes = {
        "dark": {"bg": "#0d1117", "fg": "#e6edf3", "muted": "#7d8590", "rule": "#30363d", "accent": "#39d353"},
        "light": {"bg": "#ffffff", "fg": "#24292f", "muted": "#57606a", "rule": "#d0d7de", "accent": "#2da44e"}
    }

    outputs = {}
    for theme_name, theme_colors in themes.items():
        # Notice we are now passing active_days and best_week into render_hero
        outputs[f"stats-{theme_name}.svg"] = render_hero(total, active_days, best_week, weeks, font_css, fam_reg, fam_bold, theme_colors)
        outputs[f"streak-{theme_name}.svg"] = render_streak(current, current_range, longest, longest_range, font_css, fam_reg, fam_bold, theme_colors)
        outputs[f"langs-{theme_name}.svg"] = render_langs(langs, font_css, fam_reg, fam_bold, theme_colors)

    for filename, svg in outputs.items():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(svg)

    print(f"Wrote {', '.join(outputs.keys())} -- total={total}, "
          f"current_streak={current}, longest_streak={longest}, "
          f"top_language={langs[0]['name'] if langs else 'n/a'}")

if __name__ == "__main__":
    main()