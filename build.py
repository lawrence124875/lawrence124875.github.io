#!/usr/bin/env python3
"""Build the static site into _site/.

- Copies existing hand-written pages (index.html, tarot-cards/, terms/, app-ads.txt ...) as-is.
- Renders src/content/<lang>/<app>/<slug>.md into /<lang>/<app>/<slug>/index.html.
- Renders a home page per language at /<lang>/.
- Writes sitemap.xml and robots.txt.

Add a language: add src/langs/<lang>.json ("order" sets its place in the language list) and write articles under src/content/<lang>/.
Articles in different languages are paired by the same <app>/<slug> path (used for hreflang).
"""
import html
import json
import shutil
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "_site"
BASE = "https://lawrence124875.github.io"
DEFAULT_LANG = "en"
APP_ORDER = ["iching", "tarot", "english"]
PLAY = {
    "iching": "https://play.google.com/store/apps/details?id=com.lclab.qiangua",
    "tarot": "https://play.google.com/store/apps/details?id=com.lclab.tarot",
    "english": "https://play.google.com/store/apps/details?id=tw.bcc.englishapp",
}
REFLECTION_APPS = {"iching", "tarot"}
# Paths at the repo root that are not part of the published site.
SKIP = {".git", ".github", "_site", "src", "build.py", "HANDOFF.md", "README.md", ".gitignore"}

LANGS = dict(sorted(
    ((p.stem, json.loads(p.read_text(encoding="utf-8"))) for p in (SRC / "langs").glob("*.json")),
    key=lambda kv: kv[1].get("order", 999)))
CSS = (SRC / "style.css").read_text(encoding="utf-8")
esc = html.escape


def parse(path):
    """Front matter (key: value lines between ---) + Markdown body."""
    text = path.read_text(encoding="utf-8")
    meta = {}
    if text.startswith("---"):
        head, body = text[3:].split("\n---", 1)
        for line in head.strip().splitlines():
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip("\"")
        text = body
    for key in ("title", "description"):
        if not meta.get(key):
            sys.exit(f"{path}: missing '{key}' in front matter")
    meta["order"] = int(meta.get("order", 99))
    meta["body"] = text.strip()
    return meta


def load_articles():
    arts = {}  # (lang, app, slug) -> meta
    for lang in LANGS:
        for p in sorted((SRC / "content" / lang).glob("*/*.md")):
            app, slug = p.parent.name, p.stem
            if app not in PLAY:
                sys.exit(f"{p}: unknown app folder '{app}'")
            arts[(lang, app, slug)] = parse(p)
    return arts


def url(lang, app=None, slug=None):
    return f"{BASE}/{lang}/" + (f"{app}/{slug}/" if slug else "")


def alternates(variants):
    """variants: {lang: absolute url}"""
    tags = [f'<link rel="alternate" hreflang="{l}" href="{u}">' for l, u in variants.items()]
    if DEFAULT_LANG in variants:
        tags.append(f'<link rel="alternate" hreflang="x-default" href="{variants[DEFAULT_LANG]}">')
    return "\n".join(tags)


def lang_switch(lang, variants):
    links = [f'<a href="{u}" hreflang="{l}" lang="{LANGS[l]["html_lang"]}">{esc(LANGS[l]["lang_name"])}</a>'
             for l, u in variants.items() if l != lang]
    return f'<nav class="langs" aria-label="{esc(LANGS[lang]["other_langs"])}">{" · ".join(links)}</nav>' if links else ""


def page(lang, title, description, canonical, variants, body):
    t = LANGS[lang]
    return f"""<!DOCTYPE html>
<html lang="{t['html_lang']}" dir="{t.get('dir', 'ltr')}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
{alternates(variants)}
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<style>{CSS}</style>
</head>
<body>
<header class="top"><a class="brand" href="/{lang}/">{esc(t['site_name'])}</a>{lang_switch(lang, variants)}</header>
<main>
{body}
</main>
<footer>LC Lab © 2026 · <a href="/">lawrence124875.github.io</a></footer>
</body>
</html>
"""


def cta(lang, app):
    t = LANGS[lang]
    a = t["apps"][app]
    return f"""<aside class="cta">
<p class="cta-title">{esc(t['download_cta'].format(app=a['name']))}</p>
<p>{esc(a['pitch'])}</p>
<a class="btn" href="{PLAY[app]}" rel="noopener">{esc(t['download'])}</a>
</aside>"""


def article_list(lang, items):
    return "<ul class=\"list\">" + "".join(
        f'<li><a href="/{lang}/{app}/{slug}/">{esc(m["title"])}</a></li>' for app, slug, m in items) + "</ul>"


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for p in ROOT.iterdir():
        if p.name in SKIP or p.name in LANGS:
            continue
        (shutil.copytree if p.is_dir() else shutil.copy2)(p, OUT / p.name)

    arts = load_articles()
    md = markdown.Markdown(extensions=["tables", "sane_lists"])
    sitemap = []  # (loc, {lang: url})
    by_lang_app = {}
    for (lang, app, slug), m in arts.items():
        by_lang_app.setdefault((lang, app), []).append((app, slug, m))
    for items in by_lang_app.values():
        items.sort(key=lambda x: (x[2]["order"], x[1]))

    for (lang, app, slug), m in arts.items():
        t = LANGS[lang]
        variants = {l: url(l, app, slug) for l in LANGS if (l, app, slug) in arts}
        md.reset()
        content = md.convert(m["body"])
        top_note = f'<p class="note">{esc(t["reflection_note"])}</p>' if app in REFLECTION_APPS else ""
        source_note = f'<p class="note">{esc(t["ngsl_note"])}</p>' if "NGSL" in m["body"] else ""
        related = [x for x in by_lang_app[(lang, app)] if x[1] != slug]
        body = f"""<article>
<p class="crumb"><a href="/{lang}/">{esc(t['back_home'])}</a> {'‹' if t.get('dir') == 'rtl' else '›'} {esc(t['apps'][app]['name'])}</p>
<h1>{esc(m['title'])}</h1>
{top_note}
{content}
{source_note}
{cta(lang, app)}
</article>
""" + (f"<section><h2>{esc(t['related'])}</h2>{article_list(lang, related)}</section>" if related else "")
        out = OUT / lang / app / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(lang, m["title"], m["description"], variants[lang], variants, body), encoding="utf-8")
        sitemap.append((variants[lang], variants))

    for lang, t in LANGS.items():
        cards = []
        for app in APP_ORDER:
            a = t["apps"][app]
            items = by_lang_app.get((lang, app), [])
            cards.append(f"""<section class="card" id="{app}">
<h2>{esc(a['name'])} <span class="sub">{esc(a['sub'])}</span></h2>
<p>{esc(a['pitch'])}</p>
{article_list(lang, items) if items else ''}
<a class="btn" href="{PLAY[app]}" rel="noopener">{esc(t['download'])}</a>
</section>""")
        body = f"<h1>{esc(t['site_name'])}</h1>\n<p class=\"lead\">{esc(t['home_lead'])}</p>\n" + "\n".join(cards)
        variants = {l: url(l) for l in LANGS}
        out = OUT / lang / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(lang, t["home_title"], t["home_description"], variants[lang], variants, body), encoding="utf-8")
        sitemap.append((variants[lang], variants))

    static = sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob("*.html")
                    if p.relative_to(OUT).parts[0] not in LANGS)
    sitemap[:0] = [(f"{BASE}/" + s.removesuffix("index.html"), {}) for s in static]
    entries = []
    for loc, variants in sitemap:
        alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{u}"/>' for l, u in variants.items())
        if DEFAULT_LANG in variants:
            alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{variants[DEFAULT_LANG]}"/>'
        entries.append(f"  <url>\n    <loc>{loc}</loc>{alts}\n  </url>")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(entries) + "\n</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("")

    counts = {l: sum(1 for k in arts if k[0] == l) for l in LANGS}
    print(f"Built {len(arts)} articles {counts}, {len(LANGS)} home pages, sitemap with {len(sitemap)} URLs")


if __name__ == "__main__":
    build()
