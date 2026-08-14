#!/usr/bin/env python3
"""SEO acceptance checks for the generated VitePress site."""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / ".vitepress" / "dist"
errors = []
urls: set[str] = set()

blog_index = ROOT / "zh" / "blog" / "index.md"
if not blog_index.exists():
    errors.append("Chinese blog index is missing")
else:
    index_body = blog_index.read_text(encoding="utf-8")
    for required in (
        "/zh/blog/ssh-client-recommendation",
        "/zh/blog/can-you-ssh-on-a-phone",
        "/zh/blog/termark-ai-design",
        "/zh/blog/ssh-credential-security",
    ):
        if required not in index_body:
            errors.append(f"Chinese blog index is missing priority article: {required}")

priority_articles = {
    "ssh-client-recommendation.md": "/zh-cn/ssh-client/",
    "can-you-ssh-on-a-phone.md": "/zh-cn/ssh-client/",
    "termark-ai-design.md": "/zh-cn/ai-ssh-client/",
    "ssh-credential-security.md": "/zh-cn/ssh-client/",
}
for filename, product_link in priority_articles.items():
    source = ROOT / "zh" / "blog" / filename
    if not source.exists():
        errors.append(f"priority Chinese article is missing: {filename}")
        continue
    body = source.read_text(encoding="utf-8")
    if not body.startswith("---\n") or "description:" not in body.split("---", 2)[1]:
        errors.append(f"priority article needs title and description frontmatter: {filename}")
    if product_link not in body:
        errors.append(f"priority article is missing contextual product link: {filename}")

sitemap = DIST / "sitemap.xml"
if not sitemap.exists():
    errors.append("generated sitemap.xml is missing")
else:
    try:
        tree = ET.parse(sitemap)
        root = tree.getroot()
        raw = sitemap.read_text(encoding="utf-8")
        urls = {
            node.text
            for node in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            if node.text
        }
        if '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' not in raw:
            errors.append("sitemap must use only the standard sitemap namespace")
        if "xmlns:" in raw or tree.findall(".//{http://www.w3.org/1999/xhtml}link"):
            errors.append("sitemap must not contain extension namespaces or alternate links")
        expected = {
            "https://docs.termark.app/",
            "https://docs.termark.app/blog/termark-ssh-terminal-workbench",
            "https://docs.termark.app/zh/blog/termark-ssh-terminal-workbench",
            "https://docs.termark.app/usage/sftp-cwd-tracking",
        }
        missing = expected - urls
        if missing:
            errors.append(f"sitemap is missing URLs: {sorted(missing)}")
    except ET.ParseError as exc:
        errors.append(f"invalid sitemap XML: {exc}")

samples = [
    (DIST / "blog" / "termark-ssh-terminal-workbench.html", "en-US", "/blog/termark-ssh-terminal-workbench"),
    (DIST / "zh" / "blog" / "termark-ssh-terminal-workbench.html", "zh-CN", "/zh/blog/termark-ssh-terminal-workbench"),
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

zh_home = DIST / "zh" / "index.html"
if zh_home.exists():
    body = zh_home.read_text(encoding="utf-8")
    if '<link rel="canonical" href="https://docs.termark.app/zh/">' not in body:
        errors.append("Chinese index canonical must retain its trailing slash")
else:
    errors.append("generated Chinese index is missing")

untranslated = DIST / "zh" / "blog" / "can-you-ssh-on-a-phone.html"
if untranslated.exists():
    body = untranslated.read_text(encoding="utf-8")
    if re.search(r'<link[^>]+hreflang=', body):
        errors.append("untranslated pages must not emit nonexistent language alternates")
else:
    errors.append("untranslated-page SEO fixture is missing")

if sitemap.exists():
    for url in urls:
        if url and url.endswith(".html"):
            errors.append(f"sitemap URL must be extensionless: {url}")

robots = DIST / "robots.txt"
if not robots.exists() or "Sitemap: https://docs.termark.app/sitemap.xml" not in robots.read_text(encoding="utf-8"):
    errors.append("robots.txt is missing the documentation sitemap directive")

if errors:
    print("SEO checks failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)
print("SEO checks passed")
