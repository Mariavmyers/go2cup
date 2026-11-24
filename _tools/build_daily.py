#!/usr/bin/env python3
"""Build the SportDGX Daily blog.

    python3 _tools/build_daily.py

Posts live in data/daily/*.json (one file per post). Each post becomes
articles/<slug>.html, and the hub page daily.html lists every post, newest
first. New post URLs are added to sitemap.xml. Existing pages are never edited.

Post JSON fields:
  slug, date (YYYY-MM-DD), sport (label shown on the card, e.g. "NFL"),
  lang ("en" or "es"; main language of the page), title, description,
  kicker, dek, body (HTML string: <h2>, <p>, <ul>, <table class="t"> ...),
  faq ([{"q": "...", "a": "..."}], optional), sources ([{"name": "...", "url": "..."}])
"""
import glob
import json
import os
import re
import sys
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_tools"))
from sports_nav import sport_bar, SWITCH_CSS  # noqa: E402
from form_markup import static_form  # noqa: E402

SITE = "https://sportdgx.com"


def hook():
    t = open(os.path.join(ROOT, "insider.html"), encoding="utf-8").read()
    m = re.search(r'action="(https://hook\.[^"]+)"', t)
    if not m:
        sys.exit("Could not find the newsletter webhook in insider.html")
    return m.group(1)


HEAD_SCRIPTS = """<script nowprocket data-noptimize="1" data-cfasync="false" data-wpfc-render="false" seraph-accel-crit="1" data-no-defer="1">
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
</script>"""

CSS = """*{box-sizing:border-box}
body{margin:0;background:#07180e;color:#e8f2ec;font-family:Inter,system-ui,sans-serif;line-height:1.65}
a{color:#21c25a}
.nav{max-width:1100px;margin:0 auto;padding:14px 18px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
.logo{font-family:'Bebas Neue',sans-serif;font-size:30px;letter-spacing:1px;text-decoration:none;color:#fff}
.logo .g{color:#21c25a}
.menu{display:flex;gap:16px;flex-wrap:wrap}
.menu a{font-family:Oswald,sans-serif;font-size:14px;letter-spacing:.06em;text-transform:uppercase;color:#b9c7c0;text-decoration:none}
.menu a:hover,.menu a[aria-current=page]{color:#fff}
""" + SWITCH_CSS + """
.hero{background:radial-gradient(90% 120% at 0% 0%,rgba(33,194,90,.22),transparent 60%),#0a2413;border-bottom:1px solid rgba(33,194,90,.25)}
.wrap{max-width:860px;margin:0 auto;padding:0 18px}
.hero .wrap{padding-top:44px;padding-bottom:40px}
.kicker{font-family:Oswald,sans-serif;font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:#f5c518;margin:0 0 8px}
h1{font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:clamp(2.6rem,6.4vw,4.4rem);line-height:.95;margin:0 0 14px;color:#fff;letter-spacing:.5px}
.lead{font-size:17px;color:rgba(232,242,236,.85);margin:0 0 10px}
.meta{font-family:Oswald,sans-serif;font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#9fb3a6}
main.wrap{padding-top:30px;padding-bottom:30px}
main h2{font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:2.1rem;margin:30px 0 10px;color:#fff;letter-spacing:.5px}
main h3{font-family:Oswald,sans-serif;font-weight:600;font-size:18px;margin:20px 0 6px;color:#fff}
main p,main li{font-size:16.5px;color:#dbe6dd}
main ul,main ol{padding-left:22px}
.answer{background:#0a2413;border:1px solid rgba(33,194,90,.35);border-left:4px solid #21c25a;border-radius:14px;padding:16px 20px;margin:8px 0 18px}
.note{background:#0c1f14;border-left:4px solid #f5c518;border-radius:12px;padding:14px 18px;margin:16px 0}
table.t{width:100%;border-collapse:collapse;margin:10px 0 18px;font-size:15px}
table.t th{background:#0a2413;color:#f5c518;font-family:Oswald,sans-serif;letter-spacing:.06em;text-transform:uppercase;font-size:13px;text-align:left;padding:10px}
table.t td{border-top:1px solid rgba(255,255,255,.08);padding:10px;vertical-align:top;color:#dbe6dd}
.lang-split{border:0;border-top:2px solid rgba(245,197,24,.5);margin:40px 0 10px}
.join{margin:34px 0}
.faq details{background:#0a2413;border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:12px 16px;margin:8px 0}
.faq summary{cursor:pointer;font-weight:600;color:#fff}
.sources{font-size:14px;color:#9fb3a6;border-top:1px solid rgba(255,255,255,.08);margin-top:30px;padding-top:14px}
.sources a{color:#b9c7c0}
.grid{display:grid;gap:14px;margin:10px 0 30px}
.card{display:block;background:#0a2413;border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:18px;text-decoration:none}
.card:hover{border-color:rgba(33,194,90,.5)}
.card .tag{display:inline-block;font-family:Oswald,sans-serif;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:#f5c518;margin-bottom:6px}
.card h3{font-family:Oswald,sans-serif;font-weight:600;font-size:19px;margin:0 0 6px;color:#fff}
.card p{margin:0;font-size:14.5px;color:rgba(232,242,236,.75)}
footer{border-top:1px solid rgba(255,255,255,.08);padding:26px 0 40px;font-size:13px;color:rgba(232,242,236,.55)}
footer a{color:rgba(232,242,236,.75)}
"""

MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def nice_date(iso):
    y, m, d = iso.split("-")
    return "%s %d, %s" % (MONTHS_EN[int(m) - 1], int(d), y)


def header(current):
    links = [("/", "Home"), ("/daily", "Daily"), ("/sports-news.html", "News"), ("/brazil-2027.html", "Brazil 2027"),
             ("/insider.html", "Insider"), ("/advertise.html", "Advertise")]
    menu = "".join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == current else "", t) for h, t in links)
    return ('<header><nav class="nav" aria-label="Site"><a href="/" class="logo">Sport<span class="g">DGX</span></a>'
            '<div class="menu">%s</div></nav></header>%s' % (menu, sport_bar("")))


FOOTER = ('<footer><div class="wrap"><p><a href="/daily">SportDGX Daily</a> · <a href="/insider.html">Insider newsletter</a> · '
          '<a href="/advertise.html">Advertise / partner</a> · <a href="/privacy.html">Privacy</a> · <a href="/disclaimers.html">Disclaimer &amp; Disclosure</a></p>'
          '<p>SportDGX is an independent sports and fan-travel site operated by MainEntry LLC. Not affiliated with any league, team, venue, broadcaster or ticket seller. '
          'Some links may be affiliate links.</p><p>&copy; 2026 SportDGX · MainEntry LLC</p></div></footer>')


def page(lang, title, desc, canonical, body_html, extra_head="", og_type="article"):
    return """<!doctype html>
<html lang="%s">
<head>
%s
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="%s">
<meta property="og:site_name" content="SportDGX">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<meta property="og:image" content="%s/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#07180e">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Oswald:wght@500;600&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>%s</style>
%s
</head>
<body>
%s
</body>
</html>
""" % (lang, HEAD_SCRIPTS, escape(title), escape(desc), canonical, og_type, escape(title), escape(desc), canonical, SITE,
       CSS, extra_head, body_html)


def build_post(p, hk):
    url = "%s/articles/%s" % (SITE, p["slug"])
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": p["title"], "description": p["description"],
           "datePublished": p["date"], "dateModified": p.get("updated", p["date"]), "inLanguage": p["lang"],
           "mainEntityOfPage": url, "image": SITE + "/og-image.png",
           "author": {"@type": "Organization", "name": "SportDGX"},
           "publisher": {"@type": "Organization", "name": "MainEntry LLC", "logo": {"@type": "ImageObject", "url": SITE + "/favicon-512x512.png"}}}]
    faq_html = ""
    if p.get("faq"):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", f["a"])}} for f in p["faq"]]})
        faq_html = '<section class="faq"><h2>%s</h2>%s</section>' % (
            "Preguntas frecuentes" if p["lang"] == "es" else "FAQ",
            "".join("<details><summary>%s</summary><p>%s</p></details>" % (escape(f["q"]), f["a"]) for f in p["faq"]))
    src = ""
    if p.get("sources"):
        src = '<div class="sources"><b>Sources:</b> %s</div>' % " · ".join(
            '<a href="%s" rel="nofollow noopener" target="_blank">%s</a>' % (escape(s["url"]), escape(s["name"])) for s in p["sources"])
    join = '<div class="join" data-sdgx-inline="newsletter" data-source="daily %s">%s</div>' % (
        escape(p["slug"]), static_form("newsletter", "", "daily " + p["slug"], hk))
    extra = '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False)
    body = ('%s<section class="hero"><div class="wrap"><p class="kicker">%s</p><h1>%s</h1><p class="lead">%s</p>'
            '<p class="meta">SportDGX Daily · %s</p></div></section>'
            '<main class="wrap">%s%s%s%s</main>%s<script src="/assets/sdgx-forms.js" defer></script>') % (
        header("/daily"), escape(p["kicker"]), escape(p["title"]), escape(p["dek"]), nice_date(p["date"]),
        p["body"], join, faq_html, src, FOOTER)
    out = os.path.join(ROOT, "articles", p["slug"] + ".html")
    open(out, "w", encoding="utf-8").write(page(p["lang"], p["title"] + " | SportDGX", p["description"], url, body, extra))
    return url


def build_hub(posts, hk):
    cards = "".join('<a class="card" href="/articles/%s"><span class="tag">%s · %s</span><h3>%s</h3><p>%s</p></a>' % (
        p["slug"], escape(p["sport"]), nice_date(p["date"]), escape(p["title"]), escape(p["description"])) for p in posts)
    body = ('%s<section class="hero"><div class="wrap"><p class="kicker">New every day · English &amp; Español</p>'
            '<h1>SportDGX <span style="color:#21c25a">Daily</span></h1><p class="lead">The games of the moment, explained simply: '
            'where to watch, when they play, how to get there. NFL, soccer, Liga MX and the road to the FIFA Women\'s World Cup Brazil 2027.</p>'
            '</div></section><main class="wrap"><div class="grid">%s</div><div class="join" data-sdgx-inline="newsletter" data-source="daily hub">%s</div></main>%s'
            '<script src="/assets/sdgx-forms.js" defer></script>') % (header("/daily"), cards, static_form("newsletter", "", "daily hub", hk), FOOTER)
    open(os.path.join(ROOT, "daily.html"), "w", encoding="utf-8").write(
        page("en", "SportDGX Daily: Where to Watch, Schedules & Fan Guides | SportDGX",
             "A new sports guide every day: NFL, Liga MX, soccer and the 2027 Women's World Cup in Brazil. Where to watch, dates and fan travel, in English and Spanish.",
             SITE + "/daily", body, og_type="website"))


def build_redirect(old_slug, new_slug):
    url = "%s/articles/%s" % (SITE, new_slug)
    html_ = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved | SportDGX</title>'
             '<link rel="canonical" href="%s"><meta name="robots" content="noindex, follow">'
             '<meta http-equiv="refresh" content="0; url=/articles/%s"></head><body>'
             '<p>This article moved: <a href="/articles/%s">%s</a></p></body></html>') % (url, new_slug, new_slug, url)
    open(os.path.join(ROOT, "articles", old_slug + ".html"), "w", encoding="utf-8").write(html_)


HOME_START = "<!-- SPORTDGX DAILY:START (generated by _tools/build_daily.py) -->"
HOME_END = "<!-- SPORTDGX DAILY:END -->"


def build_home_block(posts, hk):
    """Latest posts + Insider signup on the homepage, between the SPORTDGX DAILY markers."""
    path = os.path.join(ROOT, "index.html")
    t = open(path, encoding="utf-8").read()
    if HOME_START not in t:
        return
    cards = "".join(
        '<a class="sd-card" href="/articles/%s"><span class="sd-tag">%s · %s</span><span class="sd-t">%s</span></a>' % (
            p["slug"], escape(p["sport"]), nice_date(p["date"]), escape(p["title"])) for p in posts[:3])
    block = """%s
<section class="sd" aria-labelledby="sd-h">
  <style>
    .sd{background:#07180e;border-bottom:1px solid rgba(33,194,90,.25);padding:34px 18px;color:#e8f2ec;font-family:Inter,system-ui,sans-serif}
    .sd-in{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:1.25fr 1fr;gap:26px;align-items:start}
    .sd h2{font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:clamp(2rem,4.5vw,3.2rem);line-height:1;margin:0;color:#fff;letter-spacing:1px}
    .sd h2 span{color:#21c25a}
    .sd-lead{color:#9fb0ab;font-size:15px;margin:6px 0 14px}
    .sd-list{display:grid;gap:10px}
    .sd-card{display:block;background:#0a2413;border:1px solid rgba(255,255,255,.08);border-left:4px solid #21c25a;border-radius:12px;padding:14px 16px;text-decoration:none}
    .sd-card:hover{border-color:#21c25a}
    .sd-tag{display:block;font-family:'Oswald',sans-serif;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:#f5c518;margin-bottom:4px}
    .sd-t{display:block;font-family:'Oswald',sans-serif;font-weight:600;font-size:18px;color:#fff;line-height:1.25}
    .sd-all{display:inline-block;margin-top:12px;font-family:'Oswald',sans-serif;font-size:15px;letter-spacing:.06em;text-transform:uppercase;color:#07180e;background:#21c25a;border-radius:10px;padding:10px 16px;text-decoration:none}
    @media(max-width:860px){.sd-in{grid-template-columns:1fr}}
  </style>
  <div class="sd-in">
    <div>
      <h2 id="sd-h">SportDGX <span>Daily</span> Blog</h2>
      <p class="sd-lead">A new guide every day: where to watch, dates, tickets and fan travel. English &amp; Español.</p>
      <div class="sd-list">%s</div>
      <a class="sd-all" href="/daily">See all posts &rarr;</a>
    </div>
    <div data-sdgx-inline="newsletter" data-source="homepage daily block">%s</div>
  </div>
</section>
%s""" % (HOME_START, cards, static_form("newsletter", "", "homepage daily block", hk), HOME_END)
    s, e = t.index(HOME_START), t.index(HOME_END) + len(HOME_END)
    open(path, "w", encoding="utf-8").write(t[:s] + block + t[e:])


def update_sitemap(urls, remove=()):
    path = os.path.join(ROOT, "sitemap.xml")
    t = open(path, encoding="utf-8").read()
    for u in remove:
        t = re.sub(r"\s*<url>\s*<loc>%s</loc>.*?</url>" % re.escape(u), "", t, flags=re.S)
    add = ""
    for u, lastmod in urls:
        if "<loc>%s</loc>" % u not in t:
            add += "  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>\n" % (u, lastmod)
    if add:
        t = t.replace("</urlset>", add + "</urlset>")
    open(path, "w", encoding="utf-8").write(t)


def main():
    hk = hook()
    posts = [json.load(open(f, encoding="utf-8")) for f in glob.glob(os.path.join(ROOT, "data", "daily", "*.json"))]
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    urls, old = [], []
    for p in posts:
        urls.append((build_post(p, hk), p["date"]))
        for o in p.get("redirect_from", []):
            build_redirect(o, p["slug"])
            old.append("%s/articles/%s" % (SITE, o))
    build_hub(posts, hk)
    build_home_block(posts, hk)
    urls.insert(0, (SITE + "/daily", posts[0]["date"] if posts else "2026-11-24"))
    update_sitemap(urls, old)
    print("Built %d posts + daily.html" % len(posts))


if __name__ == "__main__":
    main()
