#!/usr/bin/env python3
"""SEO acceptance checks for the generated VitePress site."""
from pathlib import Path
import html
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / ".vitepress" / "dist"
errors = []
urls: set[str] = set()
UMAMI_WEBSITE_ID = "dd1a2266-3b28-4646-b8b4-107f0fb640dd"

blog_index = ROOT / "zh" / "blog" / "index.md"
if not blog_index.exists():
    errors.append("Chinese blog index is missing")
else:
    index_body = blog_index.read_text(encoding="utf-8")
    for required in (
        "/zh/blog/windows-ssh-client-guide",
        "/zh/blog/sftp-client-guide",
        "/zh/blog/ssh-client-recommendation",
        "/zh/blog/can-you-ssh-on-a-phone",
        "/zh/blog/termark-ai-design",
        "/zh/blog/ssh-credential-security",
    ):
        if required not in index_body:
            errors.append(f"Chinese blog index is missing priority article: {required}")

priority_articles = {
    "windows-ssh-client-guide.md": "/zh-cn/windows-ssh-client/",
    "ssh-client-recommendation.md": "/zh-cn/ssh-client/",
    "can-you-ssh-on-a-phone.md": "/zh-cn/ssh-client/",
    "termark-ai-design.md": "/zh-cn/ai-ssh-client/",
    "ssh-credential-security.md": "/zh-cn/ssh-client/",
    "sftp-client-guide.md": "/zh-cn/sftp-client/",
}
required_article_images = {
    "windows-ssh-client-guide.md": "./images6/termark-new-ssh-host.png",
    "sftp-client-guide.md": "./images6/fstp-file-actions.png",
}
for filename, product_link in priority_articles.items():
    source = ROOT / "zh" / "blog" / filename
    if not source.exists():
        errors.append(f"priority Chinese article is missing: {filename}")
        continue
    body = source.read_text(encoding="utf-8")
    if not body.startswith("---\n") or "description:" not in body.split("---", 2)[1]:
        errors.append(f"priority article needs title and description frontmatter: {filename}")
    frontmatter = body.split("---", 2)[1] if body.startswith("---\n") else ""
    for required_field in ("date:", "updated:", "author:"):
        if required_field not in frontmatter:
            errors.append(f"priority article is missing {required_field[:-1]} frontmatter: {filename}")
    if product_link not in body:
        errors.append(f"priority article is missing contextual product link: {filename}")
    image_link = required_article_images.get(filename)
    if image_link and image_link not in body:
        errors.append(f"priority article is missing required product screenshot: {filename}")
    if image_link and not (source.parent / image_link.removeprefix("./")).exists():
        errors.append(f"priority article screenshot file is missing: {filename}: {image_link}")

redirects_source = ROOT / "public" / "_redirects"
required_redirects = {
    "/zh/blog/go": "/zh/blog/termark-ssh-terminal-workbench",
    "/zh/blog/wechat-promo-article": "/zh/blog/termark-ssh-terminal-workbench",
    "/zh/blog/the-curse-of-knowledge-in-ai": "/zh/blog/termark-ai-design",
    "/zh/blog/soft-articles/03-ssh-client-selection-details": "/zh/blog/ssh-client-recommendation",
    "/zh/blog/soft-articles/04-ssh-credential-security-boundary": "/zh/blog/ssh-credential-security",
}
if not redirects_source.exists():
    errors.append("Cloudflare Pages redirects file is missing")
else:
    redirect_lines = redirects_source.read_text(encoding="utf-8")
    for source, target in required_redirects.items():
        if f"{source} {target} 301" not in redirect_lines:
            errors.append(f"permanent redirect is missing: {source} -> {target}")

stale_markers = (
    "【抽奖链接待补充】",
    "TODO: 以下 3 条为占位文案",
    "活动截止 **2026 年 5 月 22 日**",
    "移动端计划下个月开始开发",
    "已有 100+ 位付费用户",
    "¥149",
    "抽奖送授权",
    "最近更新到了 v1.1.0",
    "移动端也在开发中",
    "SFTP Sudo 提权",
    "SFTP 在线编辑器**                           | — | ✅",
)
blog_sources = [source for source in (ROOT / "zh" / "blog").glob("*.md") if source.name != "index.md"]
for source in blog_sources:
    body = source.read_text(encoding="utf-8")
    frontmatter = body.split("---", 2)[1] if body.startswith("---\n") else ""
    for required_field in ("title:", "description:", "date:", "updated:", "author:"):
        if required_field not in frontmatter:
            errors.append(f"published article is missing {required_field[:-1]} frontmatter: {source.name}")
    for marker in stale_markers:
        if marker in body:
            errors.append(f"published article contains stale campaign content: {source.name}: {marker}")

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
    if f'data-website-id="{UMAMI_WEBSITE_ID}"' not in body or 'src="https://umami.typesafe.cn/script.js"' not in body:
        errors.append(f"Umami tracker is missing from {route}")

for filename in (source.name for source in blog_sources):
    page = DIST / "zh" / "blog" / filename.replace(".md", ".html")
    if not page.exists():
        errors.append(f"generated priority blog page is missing: {filename}")
        continue
    body = page.read_text(encoding="utf-8")
    scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S)
    parsed = []
    for script in scripts:
        try:
            parsed.append(json.loads(script))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON-LD in {filename}: {exc}")
    types = {item.get("@type") for item in parsed if isinstance(item, dict)}
    if not {"BlogPosting", "BreadcrumbList"}.issubset(types):
        errors.append(f"blog schema is incomplete in {filename}: {sorted(str(value) for value in types)}")
        continue
    article = next(item for item in parsed if isinstance(item, dict) and item.get("@type") == "BlogPosting")
    breadcrumbs = next(item for item in parsed if isinstance(item, dict) and item.get("@type") == "BreadcrumbList")
    expected_url = f"https://docs.termark.app/zh/blog/{filename.removesuffix('.md')}"
    if article.get("mainEntityOfPage", {}).get("@id") != expected_url:
        errors.append(f"BlogPosting mainEntityOfPage is wrong in {filename}")
    for required_field in ("headline", "description", "datePublished", "dateModified", "author", "publisher"):
        if not article.get(required_field):
            errors.append(f"BlogPosting is missing {required_field} in {filename}")
    elements = breadcrumbs.get("itemListElement", [])
    if [item.get("position") for item in elements] != [1, 2, 3] or not elements or elements[-1].get("item") != expected_url:
        errors.append(f"BreadcrumbList is malformed in {filename}")

tracked_blog_links = {
    "windows-ssh-client-guide.md": "utm_campaign=windows_ssh_guide",
    "sftp-client-guide.md": "utm_campaign=sftp_client_guide",
    "termark-ai-design.md": "utm_campaign=ai_ssh_safety",
    "ssh-credential-security.md": "utm_campaign=ssh_credential_security",
    "can-you-ssh-on-a-phone.md": "utm_campaign=mobile_ssh_guide",
}
for filename, campaign in tracked_blog_links.items():
    source = ROOT / "zh" / "blog" / filename
    body = source.read_text(encoding="utf-8")
    if "utm_source=docs&utm_medium=blog&" + campaign not in body:
        errors.append(f"tracked product CTA is missing from {filename}")
    campaign_name = campaign.removeprefix("utm_campaign=")
    if 'data-umami-event="blog-cta-click"' not in body or f'data-umami-event-campaign="{campaign_name}"' not in body:
        errors.append(f"Umami CTA event is missing from {filename}")

usage_routes = [
    "data-storage-path",
    "local-encryption",
    "powershell-light-theme",
    "sftp-cwd-tracking",
    "terminal-keyword-highlight",
    "windows-virus-warning",
]
usage_sources = [ROOT / f"{locale}usage/{route}.md" for locale in ("", "zh/") for route in usage_routes]
for source in usage_sources:
    body = source.read_text(encoding="utf-8")
    frontmatter = body.split("---", 2)[1] if body.startswith("---\n") else ""
    for required_field in ("title:", "description:"):
        if required_field not in frontmatter:
            errors.append(f"usage source is missing explicit {required_field[:-1]} frontmatter: {source.relative_to(ROOT)}")

usage_metadata: dict[str, tuple[str, str]] = {}
for locale in ("", "zh/"):
    for route in usage_routes:
        rel = f"{locale}usage/{route}"
        page = DIST / f"{rel}.html"
        if not page.exists():
            errors.append(f"generated usage page is missing: {rel}")
            continue
        body = page.read_text(encoding="utf-8")
        title_match = re.search(r"<title>(.*?)</title>", body, re.S)
        description_match = re.search(r'<meta name="description" content="([^"]*)">', body)
        title = html.unescape(title_match.group(1).strip()) if title_match else ""
        description = html.unescape(description_match.group(1).strip()) if description_match else ""
        usage_metadata[rel] = (title, description)
        if not title or not description:
            errors.append(f"usage page is missing title or description: {rel}")
        if description in {"Termark Documentation", "Termark 使用文档"}:
            errors.append(f"usage page uses the generic site description: {rel}")

for index, value in enumerate(usage_metadata.items()):
    rel, (title, description) = value
    for other_rel, (other_title, other_description) in list(usage_metadata.items())[index + 1:]:
        if title == other_title:
            errors.append(f"usage pages have duplicate titles: {rel}, {other_rel}")
        if description == other_description:
            errors.append(f"usage pages have duplicate descriptions: {rel}, {other_rel}")

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
