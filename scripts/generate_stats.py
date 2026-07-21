#!/usr/bin/env python3
"""Generate dependency-free SVG cards from GitHub's public user API."""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

USERNAME = os.environ.get("PROFILE_USERNAME", "r0b5k3f0")
OUT = Path(os.environ.get("OUTPUT_DIR", "dist"))
OUT.mkdir(parents=True, exist_ok=True)

request = urllib.request.Request(
    f"https://api.github.com/users/{USERNAME}",
    headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-readme-action"},
)
with urllib.request.urlopen(request, timeout=20) as response:
    user = json.load(response)

created = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
now = datetime.now(timezone.utc)
days = max(1, (now - created).days)
updated = now.strftime("%Y-%m-%d %H:%M UTC")

values = [
    ("PUBLIC REPOS", str(user.get("public_repos", 0)), "#ff6ec7"),
    ("FOLLOWERS", str(user.get("followers", 0)), "#8be9fd"),
    ("FOLLOWING", str(user.get("following", 0)), "#c4a7ff"),
    ("DAYS ONLINE", str(days), "#63f5aa"),
]

stats = f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="190" viewBox="0 0 480 190" role="img" aria-labelledby="title desc">
<title id="title">{escape(USERNAME)} GitHub player stats</title>
<desc id="desc">Public repositories, followers, following, and account age.</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0d1117"/><stop offset="1" stop-color="#20113d"/></linearGradient>
  <linearGradient id="line"><stop stop-color="#ff6ec7"/><stop offset=".5" stop-color="#c4a7ff"/><stop offset="1" stop-color="#8be9fd"/></linearGradient>
  <filter id="glow"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect x="1.5" y="1.5" width="477" height="187" rx="14" fill="url(#bg)" stroke="url(#line)" stroke-width="3"/>
<text x="24" y="36" fill="#8be9fd" font-family="ui-monospace,monospace" font-size="12" letter-spacing="2">PLAYER DATA // LIVE</text>
<text x="24" y="62" fill="#f2ecff" font-family="ui-monospace,monospace" font-size="20" font-weight="700">@{escape(USERNAME)}</text>
<circle cx="447" cy="31" r="5" fill="#63f5aa" filter="url(#glow)"/>
'''
for index, (label, value, color) in enumerate(values):
    x = 24 + index * 113
    stats += f'''<g transform="translate({x} 91)">
<text x="0" y="0" fill="{color}" font-family="ui-monospace,monospace" font-size="25" font-weight="800">{escape(value)}</text>
<text x="0" y="22" fill="#9da7b3" font-family="ui-monospace,monospace" font-size="9" letter-spacing=".6">{label}</text>
</g>\n'''
stats += f'''<path d="M24 142H456" stroke="#30364d"/>
<text x="24" y="169" fill="#7d8590" font-family="ui-monospace,monospace" font-size="10">AUTO-SYNC • {updated}</text>
<text x="456" y="169" text-anchor="end" fill="#ff6ec7" font-family="ui-monospace,monospace" font-size="10">STATUS: ONLINE</text>
</svg>'''
(OUT / "player-stats.svg").write_text(stats, encoding="utf-8")

# Native GitHub achievements are intentionally represented locally so the card
# remains visible even when third-party Vercel trophy services are unavailable.
achievements = f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="126" viewBox="0 0 760 126" role="img" aria-labelledby="title desc">
<title id="title">{escape(USERNAME)} achievement showcase</title>
<desc id="desc">Pull Shark unlocked; future achievement slots are ready.</desc>
<defs>
 <linearGradient id="bg" x1="0" x2="1"><stop stop-color="#0d1117"/><stop offset=".5" stop-color="#20113d"/><stop offset="1" stop-color="#0d1117"/></linearGradient>
 <linearGradient id="t" x1="0" x2="1"><stop stop-color="#ff6ec7"/><stop offset="1" stop-color="#8be9fd"/></linearGradient>
 <filter id="g"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect x="1.5" y="1.5" width="757" height="123" rx="14" fill="url(#bg)" stroke="#c4a7ff" stroke-width="3"/>
<text x="24" y="31" fill="#8be9fd" font-family="ui-monospace,monospace" font-size="11" letter-spacing="2">ACHIEVEMENT UNLOCKED</text>
<g transform="translate(29 48)">
 <path d="M25 0l8 15 17 2-12 12 3 18-16-8-16 8 3-18L0 17l17-2z" fill="url(#t)" filter="url(#g)"/>
 <circle cx="25" cy="25" r="10" fill="#0d1117"/><path d="M17 26c5-8 12-8 17 0-5 7-12 7-17 0z" fill="#8be9fd"/>
</g>
<text x="96" y="72" fill="#f2ecff" font-family="ui-monospace,monospace" font-size="20" font-weight="800">PULL SHARK</text>
<text x="96" y="94" fill="#9da7b3" font-family="ui-monospace,monospace" font-size="11">Opened a pull request that was merged.</text>
<g opacity=".45" font-family="ui-monospace,monospace">
 <rect x="430" y="39" width="132" height="56" rx="9" fill="#151a25" stroke="#3b4261"/>
 <text x="496" y="72" text-anchor="middle" fill="#7d8590" font-size="11">NEXT TROPHY</text>
 <rect x="578" y="39" width="156" height="56" rx="9" fill="#151a25" stroke="#3b4261"/>
 <text x="656" y="72" text-anchor="middle" fill="#7d8590" font-size="11">QUEST LOCKED</text>
</g>
</svg>'''
(OUT / "achievements.svg").write_text(achievements, encoding="utf-8")

print(f"Generated cards for @{USERNAME} in {OUT}")
