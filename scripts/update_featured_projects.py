#!/usr/bin/env python3
"""Update the Recent Contributions section of README.md from GitHub API."""
import os
import re
import urllib.request
import json
from datetime import date, datetime, timezone, timedelta

USERNAME = "indraoverflow"
README = "README.md"
START_YEAR = 2012  # adjust to actual career start year
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

# Tech stack (aggregated from contributed repositories, grouped by category)
contrib_repos = []
for it in recent_items + merged_items:
    repo = it.get("repository_url", "").split("/repos/")[-1]
    if not repo or repo.startswith(f"{USERNAME}/"):
        continue
    if repo in contrib_repos:
        continue
    contrib_repos.append(repo)

def categorize(topics, repo):
    t = set(topics or [])
    name = repo.lower()
    if t & {"security", "appsec", "bug-bounty", "penetration-testing", "ethical-hacking", "vulnerability-scanner"} or "security" in name:
        return "Security"
    if t & {"ai", "ai-agents", "llm", "mcp", "agent-orchestration", "agentic-ai", "claude", "codex", "hermes"} or "llm" in name or "paperclip" in name or "freellmapi" in name:
        return "AI & Agents"
    if t & {"spring-boot", "erp", "accounting", "postgresql", "backend", "java", "inventory", "payroll"} or "balaka" in name:
        return "Backend & Enterprise"
    if "gstack" in name:
        return "Developer Tools"
    if t & {"devops", "docker", "shell", "infrastructure", "cli", "automation"}:
        return "DevOps & Infrastructure"
    return "Other"

color_map = {
    "TypeScript": "3178C6", "JavaScript": "F7DF1E", "Python": "3776AB",
    "Go": "00ADD8", "Java": "007396", "C": "A8B9CC", "C++": "00599C",
    "Shell": "4EAA25", "HTML": "E34F26", "CSS": "1572B6", "Rust": "000000",
    "Ruby": "CC342D", "PHP": "777BB4", "Kotlin": "7F52FF", "Swift": "F05138",
    "Dockerfile": "2496ED",
}

category_langs = {}
for repo in contrib_repos:
    try:
        r = fetch(f"https://api.github.com/repos/{repo}")
        topics = r.get("topics", [])
        cat = categorize(topics, repo)
        lang = r.get("language")
    except Exception:
        continue
    if not lang:
        continue
    category_langs.setdefault(cat, set())
    category_langs[cat].add(lang)

tech_lines = ["## 🛠 Tech Stack", "", "_Categorized by contributions._", "", "| Category | Technologies |", "|---|---|"]
if not category_langs:
    tech_lines.append("_No contribution data available._")
else:
    for cat in sorted(category_langs):
        langs = sorted(category_langs[cat])
        tech_lines.append(f"| **{cat}** | {', '.join(langs)} |")
tech_body = "\n".join(tech_lines).rstrip()

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
