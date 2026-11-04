#!/usr/bin/env python3
"""Update the Recent Contributions section of README.md from GitHub API."""
import os
import re
import urllib.request
import json

USERNAME = "indraoverflow"
README = "README.md"
START = "<!-- RECENT_CONTRIBUTIONS:START -->"
END = "<!-- RECENT_CONTRIBUTIONS:END -->"

token = os.environ.get("GITHUB_TOKEN")
headers = {"Accept": "application/vnd.github+json"}
if token:
    headers["Authorization"] = f"Bearer {token}"

url = (
    "https://api.github.com/search/issues"
    f"?q=author:{USERNAME}+type:pr&sort=updated&order=desc&per_page=8"
)
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.load(resp)

items = data.get("items", [])
lines = ["## 🔄 Recent Contributions", "", f"_Last updated: auto-generated_ ", ""]
if not items:
    lines.append("_No recent pull requests found._")
else:
    for it in items:
        title = it.get("title", "").strip()
        html_url = it.get("html_url", "")
        repo = it.get("repository_url", "").split("/repos/")[-1]
        state = it.get("state", "")
        merged = " (merged)" if it.get("pull_request", {}).get("merged_at") else ""
        lines.append(f"- [{title}]({html_url}) — `{repo}` ({state}{merged})")

block = "\n".join(lines) + "\n"

with open(README, "r", encoding="utf-8") as f:
    content = f.read()

pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
replacement = START + "\n" + block + END
if pattern.search(content):
    content = pattern.sub(replacement, content, count=1)
else:
    content = content.rstrip() + "\n\n" + START + "\n" + block + END + "\n"

with open(README, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Updated {len(items)} contributions.")
