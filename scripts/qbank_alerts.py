#!/usr/bin/env python3
"""Idempotent GitHub Issues alerts: one thread per problem; close on recovery."""
import json
import os
from pathlib import Path
import sys
from urllib.request import Request, urlopen
from urllib.parse import quote

PREFIX = "[VascQBank monitor]"
API = "https://api.github.com"

def request(repo, path, method="GET", body=None):
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GitHub token not available")
    headers = {"Authorization": "Bearer " + token,
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "VascQBank-alerts"}
    raw = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    if raw is not None:
        headers["Content-Type"] = "application/json"
    with urlopen(Request(f"{API}/repos/{repo}/{path}", data=raw,
                         headers=headers, method=method), timeout=20) as r:
        result = r.read()
    return json.loads(result) if result else {}

def existing_issues(repo):
    found = []
    for page in range(1, 6):
        batch = request(repo, f"issues?state=all&per_page=100&page={page}")
        found.extend(i for i in batch if "pull_request" not in i and
                     i.get("title", "").startswith(PREFIX))
        if len(batch) < 100:
            break
    return found

def synchronize(report):
    repo = report["repository"]
    wanted = {}
    for alert in report.get("alerts", []):
        code, topic = alert["code"], alert["topic"]
        key = f"{code}:{topic}"
        wanted[key] = dict(
            title=f"{PREFIX} {code} / {topic}",
            body=f"<!-- QBM:{key} -->\n**Code:** {code}\n**Topic:** {topic}\n\n"
                 f"{alert['detail']}\n\nThis report is observational. "
                 "No producer or shared automation index has been modified.")
    present = {}
    for item in existing_issues(repo):
        body = item.get("body") or ""
        if "<!-- QBM:" in body:
            key = body.split("<!-- QBM:", 1)[1].split(" -->", 1)[0]
            present[key] = item
    for key, issue in wanted.items():
        old = present.get(key)
        if old:
            changes = {}
            if old.get("state") != "open":
                changes["state"] = "open"
            if old.get("body", "") != issue["body"]:
                changes["body"] = issue["body"]
            if changes:
                request(repo, f"issues/{old['number']}", method="PATCH", body=changes)
                print("Updated", key)
        else:
            created = request(repo, "issues", method="POST", body=issue)
            print("Opened", key, created.get("html_url"))
    for key, old in present.items():
        if key not in wanted and old.get("state") == "open":
            request(repo, f"issues/{old['number']}/comments", method="POST",
                    body={"body": "RECOVERED — the previously reported condition "
                                  "is absent from the latest confirmed monitor snapshot."})
            request(repo, f"issues/{old['number']}", method="PATCH",
                    body={"state": "closed", "state_reason": "completed"})
            print("Recovered", key)

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/qbank_alerts.py snapshot.json")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    try:
        synchronize(data)
    except Exception as exc:
        print(f"Alert synchronization unavailable: {exc}", file=sys.stderr)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
