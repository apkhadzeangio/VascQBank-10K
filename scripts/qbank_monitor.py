#!/usr/bin/env python3
"""Observational VascQBank monitor. Never edits questions, agents or index."""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
import io
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.request import Request, urlopen
import zipfile
from zoneinfo import ZoneInfo
from qbank_quality import validate_repository

UTC = timezone.utc
LOCAL = ZoneInfo("Asia/Tbilisi")
ACTIVE = {"STARTED", "WRITING", "QA", "COMMITTING"}
PHASES = ACTIVE | {"SCHEDULED", "COMMITTED", "FAILED", "BLOCKED", "UNKNOWN"}

def parse_time(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC) if value else None
    except (ValueError, AttributeError):
        return None

def git(*args, optional=False):
    p = subprocess.run(["git", *args], text=True, capture_output=True)
    if p.returncode and not optional:
        raise RuntimeError(p.stderr.strip())
    return p.stdout.strip() if not p.returncode else ""

def api(repo, path, binary=False):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        return None
    url = "https://api.github.com/repos/" + repo + "/" + path.lstrip("/")
    headers = {"Authorization": "Bearer " + token,
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "QBank-monitor"}
    with urlopen(Request(url, headers=headers), timeout=15) as response:
        raw = response.read()
    return raw if binary else json.loads(raw)

def artifacts(repo, prefix, limit):
    if not (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")):
        return [], "Missing Actions API token"
    try:
        data = api(repo, "actions/artifacts?per_page=100")
        found = [a for a in data.get("artifacts", [])
                 if a.get("name", "").startswith(prefix) and not a.get("expired")]
        output = []
        for item in found[:limit]:
            try:
                data = api(repo, f"actions/artifacts/{item['id']}/zip", binary=True)
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    names = [x for x in archive.namelist() if x.endswith(".json")]
                    if names:
                        output.append(json.loads(archive.read(names[0]).decode("utf-8")))
            except Exception:
                continue
        return output, None
    except Exception as exc:
        return [], f"Artifacts inaccessible: {type(exc).__name__}: {exc}"

def last_quality_run(repo):
    try:
        data = api(repo, "actions/workflows/qbank-quality.yml/runs?per_page=5")
        runs = data.get("workflow_runs", []) if data else []
        return (runs[0].get("conclusion") or runs[0].get("status") or "UNKNOWN").upper() if runs else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def count_before(topic, cutoff):
    path = topic + "_questions.txt"
    sha = git("rev-list", "-1", "--before=" + cutoff.isoformat(), "HEAD", "--", path)
    if not sha:
        return 0
    body = git("show", f"{sha}:{path}", optional=True)
    return len(re.findall(r"(?m)^\d+\.\s+", body))

def committed(sha):
    if not re.fullmatch(r"[0-9a-fA-F]{40}", str(sha or "")):
        return False
    p = subprocess.run(["git", "merge-base", "--is-ancestor", sha, "HEAD"], capture_output=True)
    return p.returncode == 0

def state_for(count, target, upload, signal, now):
    if count >= target:
        return "COMPLETE"
    if signal:
        age = (now - parse_time(signal["emitted_at"])).total_seconds() / 3600
        phase = signal.get("state")
        if phase in {"BLOCKED", "FAILED"} and age <= 24:
            return phase
        if phase in ACTIVE and age <= 1.5:
            return "IN_PROGRESS"
        if phase == "COMMITTED" and age <= 1.5 and committed(signal.get("commit_sha")):
            return "PRODUCING"
    if upload and (now - upload).total_seconds() <= 3600:
        return "PRODUCING"  # Git commit proves production, not active automation.
    return "UNKNOWN"

def build(root, repo):
    quality = validate_repository(root)
    now = datetime.now(UTC)
    signals, signal_error = artifacts(repo, "qbank-hb-", 45)
    snapshots, snapshot_error = artifacts(repo, "qbank-watchdog-snapshot-", 2)
    previous = next((s for s in snapshots if s.get("topics") and s.get("observed_at")), {})
    latest = {}
    for h in signals:
        topic, agent, run = h.get("topic"), h.get("agent_id"), h.get("run_id")
        t = parse_time(h.get("emitted_at"))
        if topic and agent and run and t and h.get("state") in PHASES:
            old = latest.get(topic)
            if old is None or t > parse_time(old["emitted_at"]):
                latest[topic] = h
    mismatch = {i["topic"] for i in quality["findings"] if i["code"] == "INDEX_MISMATCH"}
    errors = {i["topic"] for i in quality["findings"] if i["level"] == "error"}
    topics, alerts = {}, []
    qa_state = last_quality_run(repo)
    for topic, detail in quality["topics"].items():
        last = parse_time(git("log", "-1", "--format=%cI", "--", topic + "_questions.txt"))
        age = (now - last).total_seconds() / 3600 if last else float("inf")
        growth = max(0, detail["questions"] - count_before(topic, now - timedelta(hours=24)))
        hb = latest.get(topic)
        status = state_for(detail["questions"], detail["target"], last, hb, now)
        index_ok = topic not in mismatch
        prior = previous.get("topics", {}).get(topic, {})
        stale = bool(hb and hb.get("state") in ACTIVE and
                     (now - parse_time(hb["emitted_at"])).total_seconds() >= 10800 and age >= 3)
        if not index_ok and prior.get("index_ok") is False and prior.get("count") == detail["questions"]:
            alerts.append({"code": "INDEX_MISMATCH", "topic": topic,
                           "detail": "Index mismatch persisted across two monitor cycles."})
        if stale and prior.get("stale_active") and prior.get("count") == detail["questions"]:
            alerts.append({"code": "PRODUCTION_DELAY", "topic": topic,
                           "detail": "Instrumented active phase was stale in two independent cycles."})
        if status in ("FAILED", "BLOCKED"):
            alerts.append({"code": "AGENT_BLOCKED" if status == "BLOCKED" else "AGENT_FAILED",
                           "topic": topic, "detail": "Explicit recent agent heartbeat."})
        if hb and hb.get("error_code") == "COMMIT_CONFLICT":
            alerts.append({"code": "COMMIT_CONFLICT", "topic": topic,
                           "detail": "Producer reported rejected concurrent commit."})
        if topic in errors and qa_state == "FAILURE":
            alerts.append({"code": "QA_FAILED", "topic": topic,
                           "detail": "Post-commit quality gate failed; inspect JSON artifact."})
        topics[topic] = {
            "count": detail["questions"], "target": detail["target"], "delta24": growth,
            "last_upload": last.isoformat() if last else None,
            "state": status, "index_ok": index_ok,
            "observation": age >= 2 and status not in ("COMPLETE", "IN_PROGRESS", "FAILED", "BLOCKED"),
            "stale_active": stale, "qa": qa_state, "heartbeat": hb,
            "integration": "INTEGRATED" if hb else "INTEGRATION_PENDING",
            "structural_errors": topic in errors,
        }
    if signal_error:
        alerts.append({"code": "SOURCE_UNAVAILABLE", "topic": "SYSTEM", "detail": signal_error})
    return {
        "observed_at": now.isoformat(), "repository": repo,
        "topics": topics, "alerts": alerts, "qa_summary": quality["summary"],
        "previous_error": snapshot_error,
        "confirmed_in_progress": sum(x["state"] == "IN_PROGRESS" for x in topics.values()),
        "heartbeat_integrated": sum(bool(x["heartbeat"]) for x in topics.values()),
    }

def local_time(iso):
    t = parse_time(iso)
    return t.astimezone(LOCAL).strftime("%Y-%m-%d %H:%M") if t else "უცნობი"

def markdown(report):
    out = [
        "<!-- VASCQBANK_MONITORING_START -->",
        "### აგენტების მონიტორინგი და ხარისხის კონტროლი",
        "",
        f"**შემოწმებულია:** {local_time(report['observed_at'])} (თბილისი). "
        f"**Heartbeat-ით დადასტურებული მიმდინარე სამუშაო:** {report['confirmed_in_progress']}; "
        f"**Heartbeat-ინტეგრირებული თემები:** {report['heartbeat_integrated']}/12. "
        "სხვა ChatGPT ანგარიშების ავტომატიზაციების მდგომარეობა მიუწვდომელია.",
        "",
        "| თემა | კითხვები | ბოლო წარმატებული ატვირთვა | +24სთ | სტატუსი | Quality Gate | ინდექსი | შენიშვნა |",
        "|---|---:|---|---:|---|---|---|---|",
    ]
    for topic, x in report["topics"].items():
        notes = []
        if x["integration"] == "INTEGRATION_PENDING":
            notes.append("Heartbeat დასაკავშირებელია")
        if x["observation"]:
            notes.append("≥2სთ ახალი კითხვის გარეშე; დაკვირვება")
        if x["structural_errors"]:
            notes.append("სტრუქტურული შეცდომა")
        out.append(f"| {topic} | {x['count']}/{x['target']} | {local_time(x['last_upload'])} | "
                   f"+{x['delta24']} | {x['state']} | {x['qa']} | "
                   f"{'OK' if x['index_ok'] else 'MISMATCH'} | {'; '.join(notes) or '—'} |")
    out += ["", "PRODUCING ნიშნავს ახლახან დადასტურებულ ატვირთვას და არა აქტიურ ჩატს. "
            "UNKNOWN არ ნიშნავს მუშაობის შეწყვეტას. Quality Gate ამოწმებს მხოლოდ სტრუქტურას, "
            "არა დამოუკიდებელ კლინიკურ ხარისხს. მონიტორი არ ცვლის კითხვებს, განმარტებებს ან საერთო ინდექსს.",
            "<!-- VASCQBANK_MONITORING_END -->", ""]
    return "\n".join(out)

def replace_block(readme, replacement):
    start = "<!-- VASCQBANK_MONITORING_START -->"
    end = "<!-- VASCQBANK_MONITORING_END -->"
    if start in readme and end in readme:
        a, b = readme.index(start), readme.index(end) + len(end)
        return readme[:a] + replacement.strip() + readme[b:]
    return readme.rstrip() + "\n\n" + replacement

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "apkhadzeangio/VascQBank-10K"))
    p.add_argument("--json-out", type=Path, default=Path("qbank-watchdog.json"))
    p.add_argument("--markdown-out", type=Path, default=Path("qbank-monitoring.md"))
    p.add_argument("--update-readme", action="store_true")
    args = p.parse_args()
    report = build(args.root, args.repo)
    md = markdown(report)
    args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    args.markdown_out.write_text(md, encoding="utf-8")
    if args.update_readme:
        pth = args.root / "README.md"
        old = pth.read_text(encoding="utf-8")
        new = replace_block(old, md)
        if old != new:
            pth.write_text(new, encoding="utf-8")
    print(f"Monitored {len(report['topics'])} topics; active="
          f"{report['confirmed_in_progress']}; alerts={len(report['alerts'])}")
    for a in report["alerts"]:
        print(a["code"], a["topic"], a["detail"])

if __name__ == "__main__":
    main()
