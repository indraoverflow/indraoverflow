#!/usr/bin/env python3
"""Health check for the profile README.

Three things are verified:

  links     every external URL answers with a success or a redirect
  assets    every local file referenced by the README exists, and the SVGs
            declare the dimensions so the render cannot collapse
  blocks    each generated marker pair exists and holds content

Exit status is 0 when everything is healthy, 1 otherwise. The workflow turns a
failure into an issue instead of a silently red run.
"""
import concurrent.futures
import pathlib
import re
import sys
import urllib.error
import urllib.request

README = pathlib.Path("README.md")
ROOT = README.parent
BLOCKS = ("CONTRIBUTIONS", "STATS", "PROJECTS")
TIMEOUT = 20
UA = "Mozilla/5.0 (compatible; profile-health-check)"

# LinkedIn answers 405 to HEAD and 999 to some automated clients while the page
# itself is public. Treat those as reachable instead of paging on a false alarm.
TOLERATED = {
    "www.linkedin.com": {405, 999},
}

OK_STATUS = {200, 203, 204, 301, 302, 303, 307, 308}


def links(text):
    found = set(re.findall(r"\]\((https?://[^)\s]+)\)", text))
    found |= set(re.findall(r'href="(https?://[^"]+)"', text))
    found |= set(re.findall(r'src="(https?://[^"]+)"', text))
    found |= set(re.findall(r'srcset="(https?://[^"\s]+)', text))
    return sorted(found)


def probe(url):
    host = url.split("/")[2] if "://" in url else ""
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                if response.status in OK_STATUS:
                    return url, "ok", response.status
        except urllib.error.HTTPError as error:
            code = error.code
            if code in TOLERATED.get(host, set()):
                return url, "ok", code
            if method == "HEAD" and code in (403, 405, 501):
                continue
            return url, "fail", code
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            if method == "HEAD":
                continue
            return url, "fail", type(error).__name__
    return url, "fail", "unreachable"


def assets(text):
    problems = []
    checked = []
    refs = set(re.findall(r'(?:src|srcset)="(assets/[^"?#]+)', text))
    for ref in sorted(refs):
        path = ROOT / ref
        if not path.exists():
            problems.append(f"{ref} is referenced but missing")
            continue
        if path.suffix == ".svg":
            body = path.read_text(encoding="utf-8")
            match = re.search(r'width="(\d+)"\s+height="(\d+)"', body)
            if not match:
                problems.append(f"{ref} has no width and height attributes")
                continue
            width, height = int(match.group(1)), int(match.group(2))
            if width < 200 or height < 40:
                problems.append(f"{ref} is {width}x{height}, too small to render as a banner")
            if "viewBox" not in body:
                problems.append(f"{ref} has no viewBox and cannot scale")
            checked.append(f"{ref} {width}x{height}")
    return checked, problems


def blocks(text):
    problems = []
    held = []
    for name in BLOCKS:
        start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
        if start not in text or end not in text:
            problems.append(f"missing markers for {name}")
            continue
        body = text.split(start, 1)[1].split(end, 1)[0].strip()
        if not body:
            problems.append(f"{name} block is empty")
            continue
        held.append(f"{name} {len(body.splitlines())} lines")
    return held, problems


def main():
    text = README.read_text(encoding="utf-8")
    failures = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(probe, links(text)))

    for url, state, detail in results:
        if state != "ok":
            failures.append(f"link {url} answered {detail}")

    checked_assets, asset_problems = assets(text)
    checked_blocks, block_problems = blocks(text)
    failures.extend(asset_problems)
    failures.extend(block_problems)

    print(f"links checked: {len(results)}")
    print(f"assets checked: {', '.join(checked_assets) or 'none'}")
    print(f"blocks checked: {', '.join(checked_blocks) or 'none'}")
    if failures:
        print("\nFAILURES")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
