#!/usr/bin/env python3
"""SEO acceptance checks for the generated VitePress site."""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / ".vitepress" / "dist"
errors = []

sitemap = DIST / "sitemap.xml"
if not sitemap.exists():
    errors.append("generated sitemap.xml is missing")
else:
    try:
        tree = ET.parse(sitemap)
        urls = {node.text for node in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
        expected = {
            "https://docs.termark.app/",
            "https://docs.termark.app/blog/termark-ssh-terminal-workbench.html",
            "https://docs.termark.app/zh/blog/termark-ssh-terminal-workbench.html",
            "https://docs.termark.app/usage/sftp-cwd-tracking.html",
        }
        missing = expected - urls
        if missing:
            errors.append(f"sitemap is missing URLs: {sorted(missing)}")
    except ET.ParseError as exc:
        errors.append(f"invalid sitemap XML: {exc}")

samples = [
    (DIST / "blog" / "termark-ssh-terminal-workbench.html", "en-US", "/blog/termark-ssh-terminal-workbench.html"),
    (DIST / "zh" / "blog" / "termark-ssh-terminal-workbench.html", "zh-CN", "/zh/blog/termark-ssh-terminal-workbench.html"),
]
for page, lang, route in samples:
    if not page.exists():
        errors.append(f"generated page is missing: {page.relative_to(ROOT)}")
        continue
    body = page.read_text(encoding="utf-8")
    canonical = f'<link rel="canonical" href="https://docs.termark.app{route}">'
    if canonical not in body:
        errors.append(f"canonical missing from {route}")
    if 'hreflang="en"' not in body or 'hreflang="zh-CN"' not in body or 'hreflang="x-default"' not in body:
        errors.append(f"hreflang cluster missing from {route}")
    if f'<html lang="{lang}"' not in body:
        errors.append(f"wrong HTML language for {route}")

robots = DIST / "robots.txt"
if not robots.exists() or "Sitemap: https://docs.termark.app/sitemap.xml" not in robots.read_text(encoding="utf-8"):
    errors.append("robots.txt is missing the documentation sitemap directive")

if errors:
    print("SEO checks failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)
print("SEO checks passed")
