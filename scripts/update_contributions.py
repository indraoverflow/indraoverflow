#!/usr/bin/env python3
"""Refresh the Open Source Contributions section from merged pull requests.

Only merged pull requests into repositories owned by someone else are listed.
Work in the profile owner's own repositories is described by hand in the
Flagship projects section, and credited work that lives in another author's
commit is described by hand as well, because the search API cannot see a
Co-authored-by trailer.
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timedelta, timezone

USERNAME = "indraoverflow"
OWNED_BY = {USERNAME, "qansaid"}
README = "README.md"
START = "<!-- CONTRIBUTIONS:START -->"
END = "<!-- CONTRIBUTIONS:END -->"
MAX_ROWS = 5


def fetch(url):
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def merged_rows():
    data = fetch(
        "https://api.github.com/search/issues"
        f"?q=author:{USERNAME}+type:pr+is:merged&sort=updated&order=desc&per_page=100"
    )
    rows = []
    seen = set()
    for item in data.get("items", []):
        repo = item.get("repository_url", "").split("/repos/")[-1]
        if not repo or repo.split("/")[0] in OWNED_BY:
            continue
        merged_at = item.get("pull_request", {}).get("merged_at")
        if not merged_at:
            continue
        key = (repo, item.get("number"))
        if key in seen:
            continue
        seen.add(key)
        rows.append((merged_at, repo, item.get("number"), item.get("title", "").strip()))
    rows.sort(reverse=True)
    return rows[:MAX_ROWS]


def render(rows):
    if not rows:
        return ["_No merged upstream contributions yet._"]
    lines = []
    for merged_at, repo, number, title in rows:
        day = datetime.fromisoformat(merged_at.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        lines.append(
            f"- **[{repo}](https://github.com/{repo})**: {title} "
            f"([#{number}](https://github.com/{repo}/pull/{number}), merged {day})"
        )
    return lines


def main():
    rows = merged_rows()
    body = "\n".join(render(rows))

    with open(README, "r", encoding="utf-8") as handle:
        content = handle.read()

    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(content):
        raise SystemExit(f"missing markers {START} / {END} in {README}")

    content = pattern.sub(lambda _: f"{START}\n{body}\n{END}", content, count=1)
    with open(README, "w", encoding="utf-8") as handle:
        handle.write(content)

    stamp = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M GMT+7")
    print(f"Updated {len(rows)} merged upstream contributions ({stamp}).")


if __name__ == "__main__":
    main()
