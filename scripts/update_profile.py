#!/usr/bin/env python3
"""Refresh the generated blocks in the profile README.

Two blocks are maintained here and nowhere else in the file:

  CONTRIBUTIONS  merged pull requests into repositories the owner does not own
  STATS          contribution counts and merged totals from the GitHub API
  PROJECTS       release, last commit and licence for each flagship repository

Everything else in the README is written by hand. Sections are located by
their HTML comment markers, so a run can never touch prose outside them.
"""
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

USERNAME = "indraoverflow"
OWNED_BY = {USERNAME, "qansaid"}
README = "README.md"
MAX_ROWS = 5
UPDATED_AT = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d")

BLOCKS = {
    "contributions": ("<!-- CONTRIBUTIONS:START -->", "<!-- CONTRIBUTIONS:END -->"),
    "stats": ("<!-- STATS:START -->", "<!-- STATS:END -->"),
    "projects": ("<!-- PROJECTS:START -->", "<!-- PROJECTS:END -->"),
}

# The flagship repositories, in the order the README presents them.
PROJECTS = [
    ("agentdiet", "qansaid/agentdiet"),
    ("gha-bill", "indraoverflow/gha-bill"),
    ("consistency-nginx", "indraoverflow/consistency-nginx"),
]


def token():
    return os.environ.get("GITHUB_TOKEN", "")


def rest(path):
    headers = {"Accept": "application/vnd.github+json"}
    if token():
        headers["Authorization"] = f"Bearer {token()}"
    request = urllib.request.Request("https://api.github.com" + path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def graphql(query, variables):
    payload = json.dumps({"query": query, "variables": variables}).encode()
    headers = {"Content-Type": "application/json", "Accept": "application/vnd.github+json"}
    if token():
        headers["Authorization"] = f"Bearer {token()}"
    request = urllib.request.Request("https://api.github.com/graphql", data=payload, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.load(response)
        return body.get("data") or {}
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError):
        return {}


_visibility = {}


def is_public(repo):
    """Private repositories are excluded: a visitor cannot verify work they cannot see."""
    if repo not in _visibility:
        try:
            _visibility[repo] = not rest(f"/repos/{repo}").get("private", False)
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError):
            _visibility[repo] = False
    return _visibility[repo]


def merged_pull_requests():
    """Merged pull requests authored by USERNAME in public repositories, newest first."""
    items = []
    for page in (1, 2):
        data = rest(
            "/search/issues?q=author:%s+type:pr+is:merged&sort=updated&order=desc&per_page=100&page=%d"
            % (USERNAME, page)
        )
        items.extend(data.get("items", []))
        if len(data.get("items", [])) < 100:
            break
    rows = []
    for item in items:
        repo = item.get("repository_url", "").split("/repos/")[-1]
        merged_at = item.get("pull_request", {}).get("merged_at")
        if not repo or not merged_at or not item.get("number"):
            continue
        if not is_public(repo):
            continue
        rows.append(
            {
                "repo": repo,
                "number": item["number"],
                "title": (item.get("title") or "").strip(),
                "merged_at": merged_at,
                "external": repo.split("/")[0] not in OWNED_BY,
            }
        )
    rows.sort(key=lambda row: row["merged_at"], reverse=True)
    return rows


def render_contributions(rows):
    external = [row for row in rows if row["external"]][:MAX_ROWS]
    if not external:
        return ["_No merged upstream contributions yet._"]
    lines = []
    for row in external:
        day = row["merged_at"][:10]
        repo = row["repo"]
        lines.append(
            f"- **[{repo}](https://github.com/{repo})**: {row['title']} "
            f"([#{row['number']}](https://github.com/{repo}/pull/{row['number']}), merged {day})"
        )
    return lines


def render_stats(rows):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=365)
    data = graphql(
        'query($from:DateTime!,$to:DateTime!){user(login:"%s"){contributionsCollection(from:$from,to:$to){'
        "totalCommitContributions totalPullRequestContributions totalIssueContributions "
        "restrictedContributionsCount contributionCalendar{totalContributions}}}}"
        % USERNAME,
        {"from": start.strftime("%Y-%m-%dT%H:%M:%SZ"), "to": now.strftime("%Y-%m-%dT%H:%M:%SZ")},
    )
    collection = (data.get("user") or {}).get("contributionsCollection") or {}

    external = [row for row in rows if row["external"]]
    repos_all = {row["repo"] for row in rows}
    repos_external = {row["repo"] for row in external}
    def plural(count):
        return "repository" if count == 1 else "repositories"

    lines = ["| Metric | Value |", "| --- | --- |"]
    if collection:
        lines += [
            f"| Contributions, last 12 months | {collection.get('contributionCalendar', {}).get('totalContributions', 0):,} |",
            f"| Commits, last 12 months | {collection.get('totalCommitContributions', 0):,} |",
            f"| Pull requests opened, last 12 months | {collection.get('totalPullRequestContributions', 0):,} |",
            f"| Private contributions, last 12 months | {collection.get('restrictedContributionsCount', 0):,} |",
        ]
    lines.append(
        f"| Merged pull requests authored, all time | {len(rows):,} in {len(repos_all)} {plural(len(repos_all))} |"
    )
    lines.append(
        f"| Merged upstream, all time | {len(external):,} in {len(repos_external)} {plural(len(repos_external))} |"
    )
    lines.append(f"\n_Refreshed {UPDATED_AT} from the GitHub API._")
    return lines


def age(iso_date):
    days = (datetime.now(timezone.utc) - datetime.fromisoformat(iso_date.replace("Z", "+00:00"))).days
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 60:
        return f"{days} days ago"
    if days < 730:
        return f"{days // 30} months ago"
    return f"{days // 365} years ago"


def render_projects():
    lines = ["| Project | Release | Commit | License |", "| --- | --- | --- | --- |"]
    for label, repo in PROJECTS:
        meta = rest(f"/repos/{repo}")
        try:
            release = rest(f"/repos/{repo}/releases/latest")
            version = release.get("tag_name") or "none"
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError):
            version = "none"
        commits = rest(f"/repos/{repo}/commits?per_page=1")
        last = commits[0]["commit"]["committer"]["date"] if commits else None
        license_id = (meta.get("license") or {}).get("spdx_id") or "not set"
        if license_id == "NOASSERTION":
            license_id = "not set"
        when = age(last) if last else "unknown"
        lines.append(f"| [{label}](https://github.com/{repo}) | {version} | {when} | {license_id} |")
    return lines


def replace_block(content, start, end, body):
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if not pattern.search(content):
        raise SystemExit(f"missing markers {start} / {end} in {README}")
    return pattern.sub(lambda _: f"{start}\n{body}\n{end}", content, count=1)


def main():
    rows = merged_pull_requests()

    with open(README, "r", encoding="utf-8") as handle:
        content = handle.read()

    contributions = "\n".join(render_contributions(rows))
    stats = "\n".join(render_stats(rows))
    projects = "\n".join(render_projects())

    content = replace_block(content, *BLOCKS["contributions"], contributions)
    content = replace_block(content, *BLOCKS["stats"], stats)
    content = replace_block(content, *BLOCKS["projects"], projects)

    with open(README, "w", encoding="utf-8") as handle:
        handle.write(content)

    print(f"Merged pull requests: {len(rows)}. Blocks refreshed for {UPDATED_AT}.")


if __name__ == "__main__":
    main()
