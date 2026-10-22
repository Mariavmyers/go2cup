#!/usr/bin/env python3
"""Build the sport hub pages (nba, soccer, ufc, boxing, tennis, racing) as static HTML.

    python3 _tools/build_sports.py

Each page comes from data/sports/<slug>.json. Every date in those files was copied
from the source listed in that file; nothing is estimated. Commit the emitted HTML.
"""
import glob
import json
import os
import sys
from datetime import date
from html import escape
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sports_nav import SWITCH_CSS, sport_bar  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLIGHTS = "https://aviasales.tpk.lu/gsLDMhOV?marker=736515.worldcup26"
ADVERTISE = "https://docs.google.com/forms/d/e/1FAIpQLSd3_Nd1UgH81RW4oYpZX6zMwCj9ZWApRaVUzShIc4UISRw2hQ/viewform?usp=header"
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

PATTERNS = {
    "court": "radial-gradient(circle at 78% 50%, transparent 0 88px, rgba(255,255,255,.07) 89px 91px, transparent 92px), linear-gradient(90deg, transparent calc(78% - 1px), rgba(255,255,255,.07) calc(78% - 1px) 78%, transparent 78%)",
    "pitch": "radial-gradient(circle at 50% 50%, transparent 0 92px, rgba(255,255,255,.07) 93px 95px, transparent 96px), linear-gradient(90deg, transparent calc(50% - 1px), rgba(255,255,255,.07) calc(50% - 1px) 50%, transparent 50%)",
    "octagon": "repeating-conic-gradient(from 22.5deg at 82% 55%, rgba(255,255,255,.05) 0 1deg, transparent 1deg 45deg)",
    "ring": "repeating-linear-gradient(180deg, transparent 0 46px, rgba(255,255,255,.06) 46px 48px)",
    "tcourt": "linear-gradient(90deg, transparent 15%, rgba(255,255,255,.07) 15% calc(15% + 2px), transparent calc(15% + 2px) 85%, rgba(255,255,255,.07) 85% calc(85% + 2px), transparent calc(85% + 2px)), linear-gradient(180deg, transparent 50%, rgba(255,255,255,.07) 50% calc(50% + 2px), transparent calc(50% + 2px))",
    "checker": "repeating-conic-gradient(rgba(255,255,255,.06) 0 25%, transparent 0 50%) 0 100% / 28px 28px",
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Oswald:wght@500;600&family=Inter:wght@400;500;600;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:#eef1f0;font-family:'Inter',sans-serif;line-height:1.55}
a{color:inherit}
.wrap{max-width:1100px;margin:0 auto;padding:0 18px}
:focus-visible{outline:2px solid var(--ac);outline-offset:2px;border-radius:4px}
header{border-bottom:1px solid var(--line);background:var(--bg2)}
.nav{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 18px;max-width:1100px;margin:0 auto;flex-wrap:wrap}
.logo{font-family:'Bebas Neue',sans-serif;font-size:30px;letter-spacing:1px;line-height:1;text-decoration:none}
.logo .b{color:#2f80ff}.logo .w{color:#fff}.logo .r{color:#ff4338}
.menu{display:flex;gap:18px;flex-wrap:wrap;font-family:'Oswald',sans-serif;font-size:14px;letter-spacing:.5px;text-transform:uppercase}
.menu a{color:#a9b5b0;text-decoration:none}.menu a:hover{color:var(--ac)}
.hero{position:relative;border-bottom:1px solid var(--line);background:var(--pat),linear-gradient(180deg,var(--bg2),var(--bg))}
.hero .wrap{padding-top:46px;padding-bottom:34px}
.hero .kicker{font-family:'Oswald',sans-serif;font-size:15px;letter-spacing:1.5px;color:var(--ac)}
.hero h1{font-family:'Bebas Neue',sans-serif;font-size:clamp(46px,9vw,90px);line-height:.92;letter-spacing:1px;margin-top:4px}
.hero p{color:#b8c2be;max-width:620px;margin-top:12px;font-size:16px}
.next{margin-top:22px;display:inline-flex;gap:14px;align-items:center;background:rgba(0,0,0,.35);border:1px solid var(--line);border-left:5px solid var(--ac);border-radius:12px;padding:12px 16px}
.next b{font-family:'Bebas Neue',sans-serif;font-size:26px;letter-spacing:.5px;line-height:1.05;display:block}
.next span{font-size:13px;color:#b8c2be}
.next .lbl{font-family:'Oswald',sans-serif;font-size:13px;color:var(--ac)}
.block{padding:34px 0;border-bottom:1px solid var(--line)}
h2{font-family:'Bebas Neue',sans-serif;font-size:38px;letter-spacing:1px;line-height:1}
.lead{color:#a9b5b0;margin:6px 0 16px;max-width:680px;font-size:15px}
.kc{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-top:26px;font-size:15px}
.kc b{color:var(--ac);font-family:'Oswald',sans-serif;font-weight:600;letter-spacing:.4px}
.events{list-style:none;display:grid;gap:10px}
.ev{display:grid;grid-template-columns:86px 1fr;gap:14px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 14px;align-items:start}
.ev.big{border-color:var(--ac)}
.when{text-align:center;border-right:1px solid var(--line);padding-right:12px}
.when .m{font-family:'Oswald',sans-serif;font-size:13px;letter-spacing:1px;color:var(--ac);text-transform:uppercase}
.when .d{font-family:'Bebas Neue',sans-serif;font-size:32px;line-height:1}
.when .y{font-size:11px;color:#8b9792}
.ev h3{font-family:'Oswald',sans-serif;font-size:18px;line-height:1.25}
.ev .sub{font-size:14px;color:#c9d1ce;margin-top:2px}
.ev .pl{font-size:13px;color:#8f9b96;margin-top:3px}
.ev .acts{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.tag{font-family:'Oswald',sans-serif;font-size:11.5px;color:var(--ac);border:1px solid var(--ac);border-radius:5px;padding:0 6px;margin-left:6px;vertical-align:2px}
.btn{display:inline-block;font-family:'Oswald',sans-serif;font-size:13.5px;letter-spacing:.3px;text-decoration:none;border-radius:8px;padding:7px 12px;border:1px solid var(--line);color:var(--soft)}
.btn:hover{border-color:var(--ac);color:var(--ac)}
.btn.solid{background:var(--ac);border-color:var(--ac);color:#0b0b0b;font-weight:600}
.btn.solid:hover{filter:brightness(1.1);color:#0b0b0b}
.two{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.box{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}
.box h3{font-family:'Oswald',sans-serif;font-size:18px;margin-bottom:6px}
.box p{font-size:14.5px;color:#c9d1ce;margin-bottom:10px}
.cta{display:flex;gap:8px;flex-wrap:wrap}
.advertise{text-align:center}
.advertise p{color:#c9d1ce;margin:8px auto 14px;max-width:560px}
.fine{font-size:12.5px;color:#8f9b96;margin-top:14px}
.fine a{color:var(--soft)}
footer{border-top:1px solid var(--line);background:var(--bg2);padding:22px 0;font-size:12.5px;color:#8f9b96;line-height:1.7;margin-top:20px}
footer a{color:var(--soft)}
@media(max-width:700px){.two{grid-template-columns:1fr}.ev{grid-template-columns:66px 1fr;gap:10px}.when .d{font-size:26px}h2{font-size:32px}}
""" + SWITCH_CSS


def e(s):
    return escape(str(s if s is not None else ""), quote=True)


def stay22(address):
    return "https://www.stay22.com/allez/roam?aid=1607597&address=" + quote(address, safe="")


def d(iso):
    y, m, dd = (int(x) for x in iso.split("-"))
    return date(y, m, dd)


def when_block(it):
    a = d(it["date"])
    if it.get("end"):
        b = d(it["end"])
        day = "%d–%d" % (a.day, b.day)
        mon = MON[a.month - 1] if a.month == b.month else "%s–%s" % (MON[a.month - 1], MON[b.month - 1])
    else:
        day, mon = str(a.day), MON[a.month - 1]
    return '<div class="when"><div class="m">%s</div><div class="d">%s</div><div class="y">%d</div></div>' % (e(mon), e(day), a.year)


def date_text(it):
    a = d(it["date"])
    s = "%s %d" % (MON[a.month - 1], a.day)
    if it.get("end"):
        b = d(it["end"])
        s += "–" + ("%d" % b.day if a.month == b.month else "%s %d" % (MON[b.month - 1], b.day))
    return s + ", %d" % a.year


def build(path):
    D = json.load(open(path, encoding="utf-8"))
    th = D["theme"]
    slug = D["slug"]
    today = date(2026, 10, 22)
    all_items = [it for s in D["sections"] for it in s["items"]]
    upcoming = sorted([it for it in all_items if d(it.get("end", it["date"])) >= today], key=lambda it: it["date"])
    nxt = upcoming[0]

    secs = []
    for s in D["sections"]:
        lis = []
        for it in s["items"]:
            acts = ""
            if it.get("hotels"):
                acts += '<a class="btn" href="%s" target="_blank" rel="sponsored noopener">Hotels nearby</a>' % e(stay22(it["hotels"]))
            if it.get("link"):
                acts += '<a class="btn" href="%s">%s</a>' % (e(it["link"]), e(it["linktext"]))
            tags = ""
            if it.get("time"):
                tags += '<span class="tag">%s</span>' % e(it["time"])
            lis.append('<li class="ev%s">%s<div><h3>%s%s</h3>%s%s%s</div></li>' % (
                " big" if it.get("big") else "", when_block(it), e(it["title"]), tags,
                ('<p class="sub">%s</p>' % e(it["sub"])) if it.get("sub") else "",
                ('<p class="pl">%s</p>' % e(it["place"])) if it.get("place") else "",
                ('<div class="acts">%s</div>' % acts) if acts else ""))
        secs.append('<section class="block"><h2>%s</h2>%s<ol class="events">%s</ol></section>' % (
            e(s["h"]), ('<p class="lead">%s</p>' % e(s["intro"])) if s.get("intro") else "", "".join(lis)))

    travel = "".join('<a class="btn%s" href="%s" target="_blank" rel="sponsored noopener">%s</a>' % (
        " solid" if i == 0 else "", e(stay22(addr)), e(lbl)) for i, (lbl, addr) in enumerate(D["travel"]))
    travel += '<a class="btn" href="%s" target="_blank" rel="sponsored noopener">Find flights</a>' % e(FLIGHTS)

    sources = "; ".join('<a href="%s" rel="noopener">%s</a>' % (e(u), e(t)) for t, u in D["sources"])

    events_ld = []
    for it in all_items:
        if not it.get("venue"):
            continue
        ev = {"@type": "SportsEvent", "name": it["title"], "startDate": it.get("start", it["date"]),
              "location": {"@type": "Place", "name": it["venue"],
                           "address": {"@type": "PostalAddress", "addressLocality": it.get("city", ""), "addressCountry": it.get("country", "")}}}
        if it.get("end"):
            ev["endDate"] = it["end"]
        events_ld.append(ev)
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": "https://sportdgx.com/%s#webpage" % slug, "url": "https://sportdgx.com/%s" % slug,
         "name": D["title"], "description": D["tagline"], "dateModified": D["accessed"][:10],
         "isPartOf": {"@type": "WebSite", "name": "GO2CUP", "url": "https://sportdgx.com/"}},
        {"@type": "ItemList", "name": D["title"] + " — upcoming events",
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": ev} for i, ev in enumerate(events_ld)]}]}

    theme_vars = "--bg:%s;--bg2:%s;--panel:%s;--line:%s;--ac:%s;--soft:%s;--pat:%s" % (
        th["bg"], th["bg2"], th["panel"], th["line"], th["accent"], th["soft"], PATTERNS[th["pattern"]])

    page = """<!doctype html>
<html lang="en">
<head>
<script nowprocket data-noptimize="1" data-cfasync="false" data-wpfc-render="false" seraph-accel-crit="1" data-no-defer="1">
  (function () {
      var script = document.createElement("script");
      script.async = 1;
      script.src = 'https://tp-em.com/NTM2NzI2.js?t=536726';
      document.head.appendChild(script);
  })();
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-Q4WSZ56TCX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-Q4WSZ56TCX');
</script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s — Schedule & Travel | GO2CUP</title>
<meta name="description" content="%(tagline)s">
<link rel="canonical" href="https://sportdgx.com/%(slug)s">
<meta property="og:type" content="website">
<meta property="og:site_name" content="GO2CUP">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(tagline)s">
<meta property="og:url" content="https://sportdgx.com/%(slug)s">
<meta property="og:image" content="https://sportdgx.com/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="%(bg)s">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<!-- Generated by _tools/build_sports.py from data/sports/%(slug)s.json. Edit those, not this file. -->
<script type="application/ld+json">
%(ld)s
</script>
<style>
%(css)s
:root{%(vars)s}
</style>
</head>
<body>
<header>
  <nav class="nav" aria-label="Site">
    <a href="/" class="logo"><span class="b">GO</span><span class="w">2</span><span class="r">CUP</span></a>
    <div class="menu">
      <a href="/">Home</a>
      <a href="/brazil-2027.html">Brazil 2027</a>
      <a href="/nfl.html">NFL</a>
      <a href="/scoreboard.html">Scoreboard</a>
      <a href="/where-to-stay.html">Where to Stay</a>
      <a href="/sports-news.html">News</a>
    </div>
  </nav>
</header>
%(bar)s
<section class="hero" aria-labelledby="hero-h">
  <div class="wrap">
    <p class="kicker">%(sport)s · 2026</p>
    <h1 id="hero-h">%(title)s</h1>
    <p>%(tagline)s</p>
    <div class="next"><div><span class="lbl">Next up · %(nextdate)s</span><b>%(nexttitle)s</b><span>%(nextplace)s</span></div></div>
  </div>
</section>
<main class="wrap">
%(kc)s
%(sections)s
<section class="block">
  <h2>Plan the trip</h2>
  <div class="two" style="margin-top:14px">
    <div class="box"><h3>Hotels and flights</h3><p>Book refundable rooms early for the big events; they sell out first.</p><div class="cta">%(travel)s</div></div>
    <div class="box"><h3>More from GO2CUP</h3><p>Kansas City guide, where to stay and the latest sports news.</p><div class="cta"><a class="btn" href="/host-cities/kansas-city.html">Kansas City guide</a><a class="btn" href="/where-to-stay.html">Where to stay</a><a class="btn" href="/sports-news.html">Sports news</a></div>
      <!-- AFFILIATE: tickets -->
    </div>
  </div>
</section>
<section class="block advertise" aria-labelledby="adv-h">
  <h2 id="adv-h">Advertise on our %(sport)s page</h2>
  <p>Reach fans planning game days and trips, with Kansas City fans first.</p>
  <a class="btn solid" href="%(adv)s" target="_blank" rel="noopener">Book your spot</a>
</section>
<p class="fine">Dates checked %(acc)s. Sources: %(sources)s. Events can move; confirm with the organizer before you travel.</p>
</main>
<footer>
  <div class="wrap">
    GO2CUP is an independent fan and travel guide by MainEntry LLC. We are not affiliated with, endorsed by or sponsored by any league, team, promoter, venue or ticket seller named on this page. Names are used only to identify events.<br>
    GO2CUP may earn a commission from affiliate links. <a href="/disclosure.html">Disclosure</a> · <a href="/privacy.html">Privacy</a> · <a href="/terms.html">Terms</a> · <a href="/">Home</a>
  </div>
</footer>
</body>
</html>
""" % {
        "title": e(D["title"]), "tagline": e(D["tagline"]), "slug": slug, "bg": th["bg"],
        "ld": json.dumps(ld, indent=1, ensure_ascii=False), "vars": theme_vars, "css": CSS,
        "bar": sport_bar(slug + ".html"), "sport": e(D["sport"]),
        "nextdate": e(date_text(nxt)), "nexttitle": e(nxt["title"]), "nextplace": e(nxt.get("place", nxt.get("sub", ""))),
        "kc": ('<div class="kc"><b>From Kansas City:</b> %s</div>' % e(D["kc"])) if D.get("kc") else "",
        "sections": "".join(secs), "travel": travel, "adv": e(ADVERTISE),
        "acc": "October 22, 2026", "sources": sources,
    }
    out = os.path.join(ROOT, slug + ".html")
    open(out, "w", encoding="utf-8").write(page)
    print("wrote %s.html (%d events, next: %s)" % (slug, len(all_items), nxt["title"]))


for p in sorted(glob.glob(os.path.join(ROOT, "data", "sports", "*.json"))):
    build(p)
