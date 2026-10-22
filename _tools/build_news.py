#!/usr/bin/env python3
"""Write the news stories into sports-news.html as static HTML.

    python3 _tools/build_news.py

Stories live in data/news/*.json (one object per story, same fields as before:
sport, category, publishedDate, title, summary, go2cupAngle, fanTravelImpact,
sourceName, sourceUrl, imageUrl, imageAlt, tags). The page shows them grouped by
sport, newest first. JavaScript only filters by sport; every story is in the HTML,
so search engines and AI crawlers can read it.
"""
import glob
import json
import os
import re
from datetime import date
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "sports-news.html")

# order on the page, label, emoji, accent color
SPORTS = [
    ("nfl", "NFL", "&#127944;", "#21c25a"),
    ("nba", "NBA", "&#127936;", "#ff7a1a"),
    ("soccer", "Soccer", "&#9917;", "#2fe0c8"),
    ("ufc", "UFC", "&#129354;", "#ff3b3b"),
    ("boxing", "Boxing", "&#129354;", "#f5b041"),
    ("tennis", "Tennis", "&#127934;", "#d7f53a"),
    ("f1", "Formula 1", "&#127950;&#65039;", "#ffb020"),
    ("worldcup", "World Cup 2026", "&#127942;", "#4ecf95"),
]
HUB = {"nfl": "/nfl.html", "nba": "/nba.html", "soccer": "/soccer.html", "ufc": "/ufc.html",
       "boxing": "/boxing.html", "tennis": "/tennis.html", "f1": "/racing.html", "worldcup": "/scoreboard.html"}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def e(s):
    return escape(str(s if s is not None else ""), quote=True)


def todo(v):
    return (not v) or str(v).upper().startswith("TODO")


def fmt(d):
    y, m, dd = (int(x) for x in d.split("-"))
    return "%s %d, %d" % (MONTHS[m - 1], dd, y)


stories = []
for p in sorted(glob.glob(os.path.join(ROOT, "data", "news", "*.json"))):
    stories.extend(json.load(open(p, encoding="utf-8")))


def card(it, emoji):
    parts = []
    if not todo(it.get("imageUrl")):
        parts.append('<div class="g2pub__card-img"><img src="%s" alt="%s" loading="lazy"></div>' % (e(it["imageUrl"]), e(it.get("imageAlt", ""))))
    else:
        parts.append('<div class="g2pub__card-imgfb" aria-hidden="true">%s</div>' % emoji)
    parts.append('<div class="g2pub__card-body">')
    parts.append('<div class="g2pub__card-meta"><span class="g2pub__badge">%s</span>%s<time class="g2pub__date" datetime="%s">%s</time></div>' % (
        e(label_of[it["sport"]]), ('<span class="g2pub__cat">%s</span>' % e(it["category"])) if it.get("category") else "",
        e(it["publishedDate"]), fmt(it["publishedDate"])))
    parts.append('<h3 class="g2pub__title">%s</h3>' % e(it["title"]))
    if it.get("summary"):
        parts.append('<p class="g2pub__summary">%s</p>' % e(it["summary"]))
    if (it.get("go2cupAngle") or "").strip():
        parts.append('<div class="g2pub__angle"><div class="g2pub__angle-label">&#9889; SportDGX Angle</div><div class="g2pub__angle-text">%s</div></div>' % e(it["go2cupAngle"]))
    if (it.get("fanTravelImpact") or "").strip():
        parts.append('<div class="g2pub__impact"><span class="g2pub__impact-lbl">&#129523; Fan Travel:</span><span>%s</span></div>' % e(it["fanTravelImpact"]))
    parts.append('<div class="g2pub__source"><span class="g2pub__source-via">Via <strong>%s</strong></span><a class="g2pub__read-link" href="%s" target="_blank" rel="noopener noreferrer">Read original &#8594;</a></div>' % (
        e(it.get("sourceName", "")), e(it["sourceUrl"])))
    if it.get("tags"):
        parts.append('<div class="g2pub__tags">%s</div>' % "".join('<span class="g2pub__tag">%s</span>' % e(t) for t in it["tags"]))
    parts.append("</div>")
    return "".join(parts)


label_of = {k: lbl for k, lbl, _, _ in SPORTS}
sections, nav = [], []
for key, label, emoji, color in SPORTS:
    items = sorted([s for s in stories if s["sport"] == key], key=lambda s: s["publishedDate"], reverse=True)
    if not items:
        continue
    cards = "".join('<article class="g2pub__card">%s</article>' % card(it, emoji) for it in items)
    sections.append(
        '<section class="g2pub__col col-%s" id="news-%s" data-sport="%s" style="--sc:%s" aria-labelledby="news-%s-h">'
        '<div class="g2pub__col-header"><span class="g2pub__col-emoji" aria-hidden="true">%s</span><h2 class="g2pub__col-title" id="news-%s-h">%s</h2>'
        '<span class="g2pub__col-count">%d %s</span><a class="g2pub__col-hub" href="%s">%s hub &#8594;</a></div>%s</section>'
        % (key, key, key, color, key, emoji, key, label, len(items), "story" if len(items) == 1 else "stories", HUB[key], label, cards))
    nav.append('<a class="nav-sport" href="#news-%s" data-sport="%s" style="--sc:%s">%s %s</a>' % (key, key, color, emoji, label))

grid = '<div class="g2pub__grid" id="g2pub-grid">%s</div>' % "".join(sections)
subnav = ('<nav class="g2pub__subnav" aria-label="Sport sections"><a class="nav-sport is-on" href="#g2pub-grid" data-sport="all">All sports</a>%s</nav>' % "".join(nav))

ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "SportDGX News", "url": "https://sportdgx.com/sports-news",
      "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {
          "@type": "NewsArticle", "headline": s["title"], "datePublished": s["publishedDate"], "description": s.get("summary", ""),
          "url": s["sourceUrl"]}} for i, s in enumerate(sorted(stories, key=lambda s: s["publishedDate"], reverse=True))]}

extra_css = """
<style id="g2pub-sports-css">
.g2pub__col-header{border-color:var(--sc)!important}
.g2pub__col-hub{margin-left:auto;font-size:.78rem;letter-spacing:.04em;color:var(--sc);text-decoration:none;font-weight:700}
.g2pub__col-hub:hover{text-decoration:underline}
.g2pub__subnav{display:flex;gap:6px;flex-wrap:wrap}
.g2pub__subnav a.nav-sport{border-bottom:2px solid transparent}
.g2pub__subnav a.nav-sport:hover,.g2pub__subnav a.nav-sport.is-on{color:#fff;border-color:var(--sc,#4ecf95)}
.g2pub__card .g2pub__title{font-size:1.15rem}
.g2pub__col[hidden]{display:none}
</style>
"""

script = """<script>
(function () {
  var d = document.getElementById('g2pub-date');
  if (d) d.textContent = new Date().toLocaleDateString('en-US', { weekday:'long', month:'long', day:'numeric', year:'numeric' });
  // Progressive enhancement: every story is already in the HTML. This only filters by sport.
  var links = [].slice.call(document.querySelectorAll('.g2pub__subnav a.nav-sport'));
  var cols = [].slice.call(document.querySelectorAll('.g2pub__col'));
  function show(sport) {
    links.forEach(function (a) { a.classList.toggle('is-on', a.dataset.sport === sport); });
    cols.forEach(function (c) { c.hidden = sport !== 'all' && c.dataset.sport !== sport; });
  }
  links.forEach(function (a) {
    a.addEventListener('click', function (ev) {
      ev.preventDefault(); show(a.dataset.sport);
      try { history.replaceState(null, '', a.dataset.sport === 'all' ? location.pathname : '#news-' + a.dataset.sport); } catch (e) {}
      document.getElementById('g2pub-grid').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
  var m = /^#news-(\\w+)$/.exec(location.hash); if (m) show(m[1]);
}());
</script>"""

s = open(PAGE, encoding="utf-8").read()

# 1) grid: replace the (empty or generated) grid div
s = re.sub(r'<div class="g2pub__grid" id="g2pub-grid">.*?</div>\s*(?=</main>)', lambda m: grid + "\n", s, count=1, flags=re.S)
# 2) sport sub-navigation
s = re.sub(r'<nav class="g2pub__subnav" aria-label="Sport sections">.*?</nav>', lambda m: subnav, s, count=1, flags=re.S)
# 3) replace the old client-side renderer (or a previously generated script) with the small filter script
start = s.find("<script>\n(function () {")
if start == -1:
    start = s.find("<script> (function () {")
assert start != -1, "renderer script not found"
end = s.find("</script>", start) + len("</script>")
s = s[:start] + script + s[end:]
# 4) static JSON-LD + sport colors in <head>
s = re.sub(r'\n<script type="application/ld\+json" id="g2pub-ld">.*?</script>', "", s, flags=re.S)
s = re.sub(r'\n<style id="g2pub-sports-css">.*?</style>\n', "\n", s, flags=re.S)
s = s.replace("</head>", extra_css + '<script type="application/ld+json" id="g2pub-ld">%s</script>\n</head>' % json.dumps(ld, ensure_ascii=False), 1)
open(PAGE, "w", encoding="utf-8").write(s)
print("news page: %d stories in %d sections" % (len(stories), len(sections)))
