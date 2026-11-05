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
        title = it.get("title", "").strip()
        html_url = it.get("html_url", "")
        state = it.get("state", "")
        merged = " (merged)" if it.get("pull_request", {}).get("merged_at") else ""
        recent_lines.append(f"- [{title}]({html_url}) : `{repo}` ({state}{merged})")
recent_body = "\n".join(recent_lines)

# Featured projects (merged PRs, deduped by repo)
merged_data = fetch(
    "https://api.github.com/search/issues"
    f"?q=author:{USERNAME}+type:pr+is:merged&sort=updated&order=desc&per_page=30"
)
merged_items = merged_data.get("items", [])
seen = set()
featured_lines = ["## 📌 Featured Projects", "", "_External repositories where my pull requests were merged._", ""]
if not merged_items:
    featured_lines.append("_No merged contributions yet._")
else:
    for it in merged_items:
        repo = it.get("repository_url", "").split("/repos/")[-1]
        if repo.startswith(f"{USERNAME}/"):
            continue
        if repo in seen:
            continue
        seen.add(repo)
        html_url = "https://github.com/" + repo
        pr_title = it.get("title", "").strip()
        pr_url = it.get("html_url", "")
        featured_lines.append(f"- **[{repo}]({html_url})** — {pr_title} ([PR]({pr_url}))")
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

print(f"Updated {len(recent_items)} recent contributions and {len(seen)} featured projects.")
