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
PRINTABLE_FILES = [
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
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag not in self.void:
            self.tag_stack.append(tag)
        if tag == "a":
            for k, v in attrs:
                if k == "href":
                    self.links.append(v)

    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
        elif tag in self.void:
            pass
        else:
            self.errors.append(f"unexpected close </{tag}> (open: {self.tag_stack[-5:]})")


def check(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    chk = HTMLChecker(os.path.basename(path), text)
    return chk.errors, text, chk.links


ok = True

style_css = open(os.path.join(ROOT, "style.css"), encoding="utf-8").read()

for html_file in HTML_FILES:
    path = os.path.join(ROOT, html_file)
    errs, text, links = check(path)
    if errs:
        ok = False
        errors.append(f"{html_file}: " + "; ".join(errs))

    # Internal links must resolve to existing files
    for link in links:
        if link.startswith("http://") or link.startswith("https://") or link.startswith("mailto:"):
            continue
        target = os.path.join(ROOT, link.lstrip("/"))
        if not os.path.exists(target):
            ok = False
            errors.append(f"{html_file}: broken link -> {link}")

    # Every page credits Asdale Dynamics, LLC in the footer area
    if "Asdale Dynamics, LLC" not in text:
        ok = False
        errors.append(f"{html_file}: missing credit")

    # Shared stylesheet linked
    if 'href="style.css"' not in text:
        ok = False
        errors.append(f"{html_file}: missing shared stylesheet")

    # Printable pages must be fillable and have a print trigger
    if html_file in PRINTABLE_FILES:
        if "window.print()" not in text:
            ok = False
            errors.append(f"{html_file}: missing print trigger")
        if '<input' not in text:
            ok = False
            errors.append(f"{html_file}: no fillable inputs")
        if '<footer' not in text:
            ok = False
            errors.append(f"{html_file}: missing footer")

if '@media print' not in style_css:
    ok = False
    errors.append("style.css: missing @media print")
if '@page' not in style_css:
    ok = False
    errors.append("style.css: missing @page rule")

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
if "MIT" not in readme_text:
    ok = False
    errors.append("README: missing license reference")

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
        fpath = os.path.join(root, fn)
        try:
            with open(fpath, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except OSError:
            continue
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
print(f"  HTML pages checked: {len(HTML_FILES)} (well-formed, links resolve, credit present)")
print(f"  Printable pages ({len(PRINTABLE_FILES)}): fillable inputs, print trigger, footer")
print("  style.css: @media print and @page present")
print("  LICENSE: exact copyright line present")
print("  README: Asdale Dynamics, LLC credited, MIT license referenced")
print("  No .github/workflows, no secrets detected")
