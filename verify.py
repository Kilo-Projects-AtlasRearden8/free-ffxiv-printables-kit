#!/usr/bin/env python3
"""Verify the FFXIV Freebies Kit builds correctly."""
import html.parser
import os
import re
import sys

ROOT = "/workspace/kilo-lab/free-ffxiv-printables-kit"
HTML_FILES = [
    "index.html",
    "duty-rotator.html",
    "gil-tracker.html",
    "leve-planner.html",
    "mount-checklist.html",
]
errors = []


class HTMLChecker(html.parser.HTMLParser):
    def __init__(self, name, text):
        super().__init__()
        self.name = name
        self.errors = []
        self.tag_stack = []
        self.void = {
            "area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr",
        }
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag not in self.void:
            self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        elif tag in self.void:
            pass
        else:
            self.errors.append(f"unexpected close </{tag}> (open: {self.tag_stack[-5:]})")

    def handle_data(self, data):
        pass


def check(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    chk = HTMLChecker(os.path.basename(path), text)
    return chk.errors, text


ok = True

for html_file in HTML_FILES:
    path = os.path.join(ROOT, html_file)
    errs, text = check(path)
    if errs:
        ok = False
        errors.append(f"{html_file}: " + "; ".join(errs))
    # Required features (landing page excluded from print-form checks)
    required = html_file != "index.html"
    if required and "window.print()" not in text:
        ok = False
        errors.append(f"{html_file}: missing print trigger")
    if required and '<input' not in text:
        ok = False
        errors.append(f"{html_file}: no fillable inputs")
    if '@media print' not in open(os.path.join(ROOT, "style.css")).read():
        ok = False
        errors.append(f"{html_file}: style.css lacks print media query")
    if "Asdale Dynamics, LLC" not in text:
        ok = False
        errors.append(f"{html_file}: missing credit")
    if 'href="style.css"' not in text:
        ok = False
        errors.append(f"{html_file}: missing shared stylesheet")

# LICENSE exact copyright line
with open(os.path.join(ROOT, "LICENSE"), encoding="utf-8") as f:
    license_text = f.read()
if "Copyright (c) 2026 Asdale Dynamics, LLC" not in license_text:
    ok = False
    errors.append("LICENSE: missing exact copyright line")

# README credit
with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
    readme_text = f.read()
if "Asdale Dynamics, LLC" not in readme_text:
    ok = False
    errors.append("README: missing credit")

# Forbidden files
if os.path.exists(os.path.join(ROOT, ".github", "workflows")):
    ok = False
    errors.append(".github/workflows exists (forbidden)")

# Secrets scan (naive)
for root, _dirs, files in os.walk(ROOT):
    if ".git" in root:
        continue
    for fn in files:
        if fn == ".gitkeep":
            continue
        with open(os.path.join(root, fn), encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for pat in (r"sk-[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"):
            if re.search(pat, content):
                ok = False
                errors.append(f"{fn}: possible secret ({pat})")

if errors:
    print("VERIFICATION FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print("VERIFICATION PASSED")
print(f"  HTML pages checked: {len(HTML_FILES)} (well-formed, fillable inputs, print trigger, credit)")
print("  style.css: @media print present")
print("  LICENSE: exact copyright line present")
print("  README: Asdale Dynamics, LLC credited")
print("  No .github/workflows, no secrets detected")
