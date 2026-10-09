#!/usr/bin/env python3
"""Update the GitHub ASCII card's uptime from the GitHub account creation date."""
import datetime as dt
import json
import os
import re
import urllib.request
from pathlib import Path

USERNAME = os.environ.get("GITHUB_USERNAME", "akashbondada1234")
SVG_PATH = Path("dark_mode.svg")
API_URL = f"https://api.github.com/users/{USERNAME}"

def calendar_age(start: dt.date, end: dt.date) -> tuple[int, int, int]:
    years = end.year - start.year
    months = end.month - start.month
    days = end.day - start.day
    if days < 0:
        previous_month = end.month - 1 or 12
        previous_year = end.year if end.month > 1 else end.year - 1
        next_month = previous_month % 12 + 1
        next_year = previous_year + (1 if previous_month == 12 else 0)
        days += (dt.date(next_year, next_month, 1) -
                 dt.date(previous_year, previous_month, 1)).days
        months -= 1
    if months < 0:
        months += 12
        years -= 1
    return years, months, days

request = urllib.request.Request(
    API_URL,
    headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-ascii-card-uptime-updater",
    },
)
with urllib.request.urlopen(request, timeout=20) as response:
    profile = json.load(response)

created_at = profile.get("created_at")
if not created_at:
    raise RuntimeError(f"GitHub API response did not contain created_at for {USERNAME}")

created_date = dt.datetime.fromisoformat(created_at.replace("Z", "+00:00")).date()
today_utc = dt.datetime.now(dt.timezone.utc).date()
years, months, days = calendar_age(created_date, today_utc)
uptime = f"{years} years, {months} months, {days} days"

svg = SVG_PATH.read_text(encoding="utf-8")
pattern = r'(<tspan id="uptime-value" fill="#c9d1d9">).*?(</tspan>)'
updated_svg, replacements = re.subn(
    pattern, lambda m: m.group(1) + uptime + m.group(2), svg, count=1
)
if replacements != 1:
    raise RuntimeError("Could not find the uptime-value marker in dark_mode.svg")

if updated_svg != svg:
    SVG_PATH.write_text(updated_svg, encoding="utf-8")
    print(f"Updated uptime for @{USERNAME}: {uptime}")
else:
    print(f"Uptime is already current: {uptime}")
