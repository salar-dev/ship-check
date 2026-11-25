#!/usr/bin/env python3
"""Ship Check report checker: catches mistakes in a finished report before the owner reads it.

It checks that
  1. every `file:line` the report cites exists in the project,
  2. no secret from the project appears unmasked in the report,
  3. the counts in the Result line match the findings, and every check appears exactly once,
  4. no line promises that the site is secure, safe or ready.

It only reads. Usage:  python3 check_report.py <project_dir> <report.md>
"""

import os
import re
import sys

MARKS = ["\U0001F534", "\U0001F7E1", "\U0001F7E2", "⚪"]  # red, yellow, green, white
NAMES = dict(zip(MARKS, ["red", "yellow", "green", "not checked"]))
TOKEN = re.compile(
    r"sk-[A-Za-z0-9_\-]{16,}|sk_(?:live|test)_[A-Za-z0-9]{10,}|rk_(?:live|test)_[A-Za-z0-9]{10,}"
    r"|whsec_[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9\-]{10,}"
    r"|sb_secret_[A-Za-z0-9_\-]{10,}|eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}")
SECRET_NAME = re.compile(r"KEY|SECRET|TOKEN|PASSWORD|PASSWD|PRIVATE|CREDENTIAL|DSN|DATABASE_URL", re.I)
CITATION = re.compile(r"`([^`\s:]+(?:/[^`\s:]+)*\.[A-Za-z0-9]+|\.[A-Za-z0-9_.\-]+|[A-Za-z0-9_.\-]+):(\d+)(?:-(\d+))?`")
PROMISE = re.compile(r"100\s?%|\bguaranteed\b|\b(is|are|now|fully|completely) (secure|safe)\b|\bready to (launch|ship|go live)\b", re.I)
PROMISE_OK = re.compile(r"\bnot\b|\bcannot\b|\bcan't\b|\bnever\b|\bno\b|\bbefore\b|\bisn't\b|\bsays?\b|\bpromises?\b|\bclaims?\b", re.I)


def line_count(path, cache={}):
    if path not in cache:
        try:
            with open(path, "rb") as f:
                cache[path] = f.read().count(b"\n") + 1
        except OSError:
            cache[path] = None
    return cache[path]


def env_secrets(root):
    found = {}
    for name in sorted(os.listdir(root)):
        if not name.startswith(".env") or re.search(r"example|sample|template|dist", name):
            continue
        try:
            text = open(os.path.join(root, name), encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in re.finditer(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", text, re.M):
            value = m.group(2).strip().strip("\"'")
            if SECRET_NAME.search(m.group(1)) and len(value) >= 6:
                found[value] = f"{m.group(1)} (from {name})"
    return found


def check_ids(skill_dir):
    path = os.path.join(skill_dir, "references", "checks.md")
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return []
    return re.findall(r"^### ([A-Z]\d+)\.", text, re.M)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    root, report_path = os.path.abspath(sys.argv[1]), sys.argv[2]
    report = open(report_path, encoding="utf-8").read()
    lines = report.splitlines()
    problems = []

    # 1. citations
    cited = 0
    for n, line in enumerate(lines, 1):
        for m in CITATION.finditer(line):
            rel, first, last = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
            cited += 1
            total = line_count(os.path.join(root, rel))
            if total is None:
                problems.append(f"report line {n}: `{rel}` does not exist in the project")
            elif last > total or first < 1:
                problems.append(f"report line {n}: `{rel}:{m.group(2)}` is past the end of the file ({total} lines)")

    # 2. secrets
    for value, name in env_secrets(root).items():
        if value in report:
            problems.append(f"the full value of {name} appears in the report: mask it")
    for n, line in enumerate(lines, 1):
        if TOKEN.search(line):
            problems.append(f"report line {n}: an unmasked key-like value: mask it")

    # 3. counts and check IDs
    result = next((l for l in lines if all(mark in l for mark in MARKS[:2]) and re.search(r"\d", l)), "")
    stated = {}
    for mark in MARKS:
        m = re.search(re.escape(mark) + r"\s*(\d+)", result)
        if m:
            stated[mark] = int(m.group(1))
    sections, current = {mark: [] for mark in MARKS}, None
    for line in lines:
        if line.startswith("## "):
            current = next((mark for mark in MARKS if mark in line), None)
            continue
        if current:
            sections[current].append(line)
    ids = []
    for mark in MARKS:
        body = sections[mark]
        if mark in MARKS[:2]:
            count = sum(1 for l in body if l.startswith("### "))
            ids += [m.group(1) for l in body for m in [re.match(r"\s*-\s+\*\*[^*]+\*\*\s*([A-Z]\d+)\s*$", l)] if m]
        else:
            entries = [l for l in body if re.match(r"-\s+\S", l) and not re.match(r"-\s+none\b", l, re.I)]
            count = len(entries)
            ids += [m.group(1) for l in entries for m in [re.match(r"-\s+\**([A-Z]\d+)\b", l)] if m]
        if mark not in stated:
            problems.append(f"the Result line has no count for {NAMES[mark]}")
        elif stated[mark] != count:
            problems.append(f"Result line says {stated[mark]} {NAMES[mark]}, but the report lists {count}")

    expected = check_ids(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if expected:
        for cid in expected:
            if ids.count(cid) == 0:
                problems.append(f"check {cid} has no mark in the report")
            elif ids.count(cid) > 1:
                problems.append(f"check {cid} appears {ids.count(cid)} times; each check gets one mark")
        for cid in sorted(set(ids) - set(expected)):
            problems.append(f"check {cid} is not in the check list")
        if sum(stated.values()) != len(expected):
            problems.append(f"the four counts add up to {sum(stated.values())}, but there are {len(expected)} checks")

    # 4. promises
    for n, line in enumerate(lines, 1):
        if PROMISE.search(line) and not PROMISE_OK.search(line):
            problems.append(f"report line {n}: reads like a promise that the site is secure, safe or ready: reword it")

    print(f"Checked {cited} file:line citations, {len(ids)} check marks, {len(lines)} lines.")
    if problems:
        print(f"{len(problems)} thing(s) to fix before delivering the report:")
        for p in problems:
            print("- " + p)
        sys.exit(1)
    print("No problems found in the report's citations, masking, counts or wording.")


if __name__ == "__main__":
    main()
