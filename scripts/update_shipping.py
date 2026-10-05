"""Rewrite the README block between SHIPPING markers with recently pushed public repos."""
import json
import re
import subprocess
from datetime import datetime, timezone

USER = "Samurai33"
SKIP = {USER}           # repos never listed (e.g. the profile repo itself)
LIMIT = 5

raw = subprocess.check_output(
    ["gh", "api", f"users/{USER}/repos?per_page=100&sort=pushed&type=owner"], text=True
)
repos = [
    r for r in json.loads(raw)
    if not r["fork"] and not r["archived"] and r["name"] not in SKIP and r["description"]
][:LIMIT]


def ago(iso: str) -> str:
    days = (datetime.now(timezone.utc) - datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    return "today" if days == 0 else f"{days}d ago" if days < 30 else f"{days // 30}mo ago"


rows = ["| Repository | What it is | Stack | Last push |", "|---|---|---|---|"]
for r in repos:
    desc = r["description"].replace("|", "\\|")
    rows.append(
        f"| [{r['name']}]({r['html_url']}) | {desc} | "
        f"{r['language'] or '—'} | {ago(r['pushed_at'])} |"
    )

block = "<!-- SHIPPING:START -->\n" + "\n".join(rows) + "\n<!-- SHIPPING:END -->"
with open("README.md", encoding="utf-8") as f:
    readme = f.read()
readme = re.sub(r"<!-- SHIPPING:START -->.*?<!-- SHIPPING:END -->", lambda _: block, readme, flags=re.S)
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
print(f"Updated with {len(repos)} repos")
