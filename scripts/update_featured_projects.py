#!/usr/bin/env python3
"""Update the Recent Contributions section of README.md from GitHub API."""
import os
import re
import urllib.request
import json
from datetime import date, datetime, timezone, timedelta

USERNAME = "indraoverflow"
README = "README.md"
START_YEAR = 2014  # reconciled to 12+ years (AGENTS.md / IND-1 onboarding plan)
RECENT_START = "<!-- RECENT_CONTRIBUTIONS:START -->"
RECENT_END = "<!-- RECENT_CONTRIBUTIONS:END -->"
FEATURED_START = "<!-- FEATURED_PROJECTS:START -->"
FEATURED_END = "<!-- FEATURED_PROJECTS:END -->"
TECH_START = "<!-- TECH_STACK:START -->"
TECH_END = "<!-- TECH_STACK:END -->"


def fetch(url):
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def update_section(content, start, end, body):
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    replacement = start + "\n" + body + "\n" + end
    if pattern.search(content):
        return pattern.sub(replacement, content, count=1)
    return content.rstrip() + "\n\n" + replacement + "\n"


# Recent contributions (all PRs)
recent_data = fetch(
    "https://api.github.com/search/issues"
    f"?q=author:{USERNAME}+type:pr&sort=updated&order=desc&per_page=30"
)
recent_items = recent_data.get("items", [])
wib_now = datetime.now(timezone(timedelta(hours=7)))
updated_label = wib_now.strftime("%d %B %Y, %H:%M GMT+7")
recent_lines = ["## 🔄 Recent Contributions", "", f"_Last updated: {updated_label}_", ""]
if not recent_items:
    recent_lines.append("_No recent pull requests found._")
else:
    for it in recent_items:
        repo = it.get("repository_url", "").split("/repos/")[-1]
        if repo.startswith(f"{USERNAME}/"):
            continue
        merged_at = it.get("pull_request", {}).get("merged_at")
        state = it.get("state", "")
        # Closed (non-merged) PRs are no longer shown in recent contributions.
        if state == "closed" and not merged_at:
            continue
        repo_owner = repo.split("/", 1)[0]
        # Merged PRs in repositories owned by the user are already covered by
        # Featured Projects; do not duplicate them in recent contributions.
        if merged_at and repo_owner in {USERNAME, "qansaid"}:
            continue
        title = it.get("title", "").strip()
        html_url = it.get("html_url", "")
        # GitHub reports a merged pull request as state "closed"; showing both
        # produced "(closed (merged))" on every line.
        status = "merged" if merged_at else state
        recent_lines.append(f"- [{title}]({html_url}) : `{repo}` ({status})")
recent_body = "\n".join(recent_lines)

# Featured projects (merged PRs, deduped by repo)
merged_data = fetch(
    "https://api.github.com/search/issues"
    f"?q=author:{USERNAME}+type:pr+is:merged&sort=updated&order=desc&per_page=30"
)
merged_items = merged_data.get("items", [])

# Two things the author query cannot express, both kept explicit.
#
# PINNED: a repository where the newest merged PR is not the one worth showing,
# because a one-line chore landed on top of the real work. The repository still
# has to appear in the merged list, so a pin can never invent a contribution.
PINNED = {
    "qansaid/agentdiet": ("feat(website): add the AgentDiet product site", 1),
}

# CREDITED: work merged by someone else that credits this account. A pull
# request can carry a Co-authored-by trailer without being yours, and the search
# query only matches authors. Each entry carries the form the credit takes, so
# the section never implies authorship it does not have.
CREDITED = [
    (
        "garrytan/gstack",
        4085,
        "free-ci-health: a split shard's overrun compares wall time with its prediction over jobs (GST-1653)",
        "co-author on 5e2964d",
    ),
]

featured_lines = ["## 📌 Featured Projects", "", "_Repositories where my work was merged._", ""]

generated = {}
order = []
for it in merged_items:
    repo = it.get("repository_url", "").split("/repos/")[-1]
    if repo.startswith(f"{USERNAME}/") or repo in generated:
        continue
    generated[repo] = (it.get("title", "").strip(), it.get("html_url", ""))
    order.append(repo)

rows = []
for repo, (pr_title, number) in PINNED.items():
    if repo in generated:
        rows.append((repo, pr_title, f"https://github.com/{repo}/pull/{number}", None))
        order.remove(repo)
for repo, number, pr_title, note in CREDITED:
    rows.append((repo, pr_title, f"https://github.com/{repo}/pull/{number}", note))
    if repo in order:
        order.remove(repo)
for repo in order:
    pr_title, pr_url = generated[repo]
    rows.append((repo, pr_title, pr_url, None))

if not rows:
    featured_lines.append("_No merged contributions yet._")
for repo, pr_title, pr_url, note in rows:
    entry = f"- **[{repo}](https://github.com/{repo})**: {pr_title}"
    entry += f" ({note}, [PR]({pr_url}))" if note else f" ([PR]({pr_url}))"
    featured_lines.append(entry)

featured_body = "\n".join(featured_lines)

# Tech stack (recommended curated format)
tech_lines = [
    "## 🛠 Tech Stack",
    "",
    "| Category | Technologies |",
    "|---|---|",
    "| **Programming Languages** | Go, TypeScript, JavaScript, Python, Java |",
    "| **Backend Engineering** | Node.js, Spring Boot, REST API, gRPC |",
    "| **Databases & Caching** | PostgreSQL, MongoDB, Redis |",
    "| **DevOps & CI/CD** | Docker, Kubernetes, GitHub Actions |",
    "| **Cloud & Infrastructure** | Linux, Nginx, Networking |",
    "| **Monitoring & Observability** | Prometheus, Grafana, Logging |",
    "| **Version Control** | Git, GitHub |",
    "| **Software Architecture** | Microservices, Distributed Systems, System Design |",
]
tech_body = "\n".join(tech_lines)

with open(README, "r", encoding="utf-8") as f:
    content = f.read()

content = update_section(content, RECENT_START, RECENT_END, recent_body)
content = update_section(content, FEATURED_START, FEATURED_END, featured_body)
content = update_section(content, TECH_START, TECH_END, tech_body)

# Update years of experience dynamically
years = date.today().year - START_YEAR
content = re.sub(r"\d+\+ years of experience", f"{years}+ years of experience", content)

with open(README, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Updated {len(recent_items)} recent contributions and {len(rows)} featured projects.")
