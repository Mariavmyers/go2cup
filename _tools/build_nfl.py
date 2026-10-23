#!/usr/bin/env python3
"""Build nfl.html (NFL 2026 Season Hub) as static HTML from data/nfl-2026-schedule.json.

Run locally, then commit the emitted nfl.html:
    python3 _tools/build_nfl.py

Schedule data comes only from the official club schedule pages listed in the
data file's "sources". Dates the clubs list as TBD stay TBD. No logos are used.
"""
import json
import os
from collections import Counter
from datetime import datetime
from html import escape
from urllib.parse import quote
from zoneinfo import ZoneInfo
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sports_nav import SWITCH_CSS, sport_bar  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CT = ZoneInfo("America/Chicago")  # Kansas City is our home market, so times are Central

DATA = json.load(open(os.path.join(ROOT, "data", "nfl-2026-schedule.json"), encoding="utf-8"))
GAMES = DATA["games"]

TEAMS = {
    "ARI": ("Arizona Cardinals", "NFC West"), "ATL": ("Atlanta Falcons", "NFC South"),
    "BAL": ("Baltimore Ravens", "AFC North"), "BUF": ("Buffalo Bills", "AFC East"),
    "CAR": ("Carolina Panthers", "NFC South"), "CHI": ("Chicago Bears", "NFC North"),
    "CIN": ("Cincinnati Bengals", "AFC North"), "CLE": ("Cleveland Browns", "AFC North"),
    "DAL": ("Dallas Cowboys", "NFC East"), "DEN": ("Denver Broncos", "AFC West"),
    "DET": ("Detroit Lions", "NFC North"), "GB": ("Green Bay Packers", "NFC North"),
    "HOU": ("Houston Texans", "AFC South"), "IND": ("Indianapolis Colts", "AFC South"),
    "JAX": ("Jacksonville Jaguars", "AFC South"), "KC": ("Kansas City Chiefs", "AFC West"),
    "LV": ("Las Vegas Raiders", "AFC West"), "LAC": ("Los Angeles Chargers", "AFC West"),
    "LAR": ("Los Angeles Rams", "NFC West"), "MIA": ("Miami Dolphins", "AFC East"),
    "MIN": ("Minnesota Vikings", "NFC North"), "NE": ("New England Patriots", "AFC East"),
    "NO": ("New Orleans Saints", "NFC South"), "NYG": ("New York Giants", "NFC East"),
    "NYJ": ("New York Jets", "AFC East"), "PHI": ("Philadelphia Eagles", "NFC East"),
    "PIT": ("Pittsburgh Steelers", "AFC North"), "SF": ("San Francisco 49ers", "NFC West"),
    "SEA": ("Seattle Seahawks", "NFC West"), "TB": ("Tampa Bay Buccaneers", "NFC South"),
    "TEN": ("Tennessee Titans", "AFC South"), "WSH": ("Washington Commanders", "NFC East"),
}
DIVISIONS = [c + " " + d for c in ("AFC", "NFC") for d in ("East", "North", "South", "West")]
HOST_CITY = {  # existing GO2CUP city guides
    "ATL": "atlanta", "NE": "boston-foxborough", "DAL": "dallas", "HOU": "houston", "KC": "kansas-city",
    "LAR": "los-angeles", "LAC": "los-angeles", "MIA": "miami", "NYG": "new-york-new-jersey",
    "NYJ": "new-york-new-jersey", "PHI": "philadelphia", "SF": "san-francisco-bay-area", "SEA": "seattle",
}
# Chiefs results so far, as published on chiefs.com/schedule (accessed 2026-10-20)
CHIEFS_RESULTS = [
    (1, "vs", "Denver Broncos", "W 31–10"), (2, "vs", "Indianapolis Colts", "W 33–30 (OT)"),
    (3, "at", "Miami Dolphins", "W 24–10"), (4, "at", "Las Vegas Raiders", "W 30–27"),
    (5, "", "Bye week", ""), (6, "vs", "Los Angeles Chargers", "W 22–6"),
]
FLIGHTS = "https://aviasales.tpk.lu/gsLDMhOV?marker=736515.worldcup26"
ADVERTISE = "/advertise.html#inquiry"


def e(s):
    return escape(str(s if s is not None else ""), quote=True)


def stay22(address):
    return "https://www.stay22.com/allez/roam?aid=1607597&address=" + quote(address, safe="")


def kickoff(g):
    if g["kickoffTBD"]:
        return None
    return datetime.fromisoformat(g["kickoff"].replace("Z", "+00:00")).astimezone(CT)


def when(g, long=False):
    k = kickoff(g)
    if not k:
        return "Date and time TBD"
    h = k.hour % 12 or 12
    t = "%d:%02d %s CT" % (h, k.minute, "PM" if k.hour >= 12 else "AM")
    d = k.strftime("%A, %B " if long else "%a, %b ") + str(k.day)
    return d + " · " + t


# Fan-facing city names where the club feed gives a postal locality instead
DISPLAY_CITY = {"Opa Locka": "Miami Gardens", "Paradise": "Las Vegas", "Saint-Denis": "Paris (Saint-Denis)", "East Melbourne": "Melbourne"}


def city_of(g):
    return DISPLAY_CITY.get(g["city"], g["city"])


def where(g):
    place = city_of(g) + ("" if g["country"] in ("USA", "") else ", " + g["country"])
    return "%s, %s" % (g["venue"], place)


# home stadium + city per team from its official home games (most common non-international venue)
HOME = {}
for a in TEAMS:
    c = Counter((g["venue"], city_of(g)) for g in GAMES if g["home"] == a and g["country"] in ("USA", ""))
    HOME[a] = c.most_common(1)[0][0] if c else ("", "")

REMAINING = [g for g in GAMES if not g["played"]]


def team_games(a):
    return sorted([g for g in REMAINING if a in (g["home"], g["away"])], key=lambda g: g["week"])


def opp_line(g, a):
    home = g["home"] == a
    return ("vs " if home else "at ") + TEAMS[g["away"] if home else g["home"]][0]


def sched_rows(a, weeks=range(7, 19)):
    gs = {g["week"]: g for g in team_games(a)}
    rows = []
    for w in weeks:
        g = gs.get(w)
        if not g:
            rows.append('<li class="bye"><span class="wk">Wk %d</span><span class="op">Bye week</span></li>' % w)
            continue
        intl = g["country"] not in ("USA", "")
        rows.append('<li><span class="wk">Wk %d</span><span class="op">%s%s</span><span class="tm">%s</span><span class="vn">%s%s</span></li>'
                    % (w, e(opp_line(g, a)), ' <span class="intl">%s</span>' % e(city_of(g)) if intl else "",
                       e(when(g)), e(where(g)), (" · " + e(g["tv"])) if g["tv"] else ""))
    return "".join(rows)


# ------------------------------------------------------------------ Chiefs
kc_next = team_games("KC")[0]
chiefs_results = "".join(
    '<li><span class="wk">Wk %d</span><span class="op">%s</span><span class="res">%s</span></li>'
    % (w, e((ha + " " + opp).strip()), e(r)) for w, ha, opp, r in CHIEFS_RESULTS)
chiefs_section = """
<section class="block chiefs" id="chiefs" aria-labelledby="chiefs-h">
  <div class="chiefs-head">
    <div>
      <h2 id="chiefs-h">Kansas City Chiefs</h2>
      <p class="lead">Our home team. 5–0 after Week 6, per chiefs.com. Arrowhead Stadium, Kansas City, Missouri.</p>
    </div>
    <div class="next">
      <p class="next-l">Next game · Week %d</p>
      <p class="next-g">%s</p>
      <p class="next-t">%s</p>
      <p class="next-v">%s%s</p>
    </div>
  </div>
  <div class="two">
    <div>
      <h3>Remaining 2026 schedule</h3>
      <ol class="sched">%s</ol>
      <p class="fine">Weeks 17 and 18 dates and kickoff times will be announced by the NFL. Sunday and Monday night games can be moved by flex scheduling. Source: <a href="https://www.chiefs.com/schedule/" rel="noopener">chiefs.com/schedule</a>.</p>
    </div>
    <div>
      <h3>Results so far</h3>
      <ol class="sched results">%s</ol>
      <h3 class="mt">Going to a game?</h3>
      <div class="cta-row">
        <a class="btn solid" href="%s" target="_blank" rel="sponsored noopener">Hotels near Arrowhead</a>
        <a class="btn" href="%s" target="_blank" rel="sponsored noopener">Find flights</a>
        <a class="btn" href="host-cities/kansas-city.html">Kansas City guide</a>
      </div>
      <!-- AFFILIATE: tickets -->
      <!-- AFFILIATE: merch -->
    </div>
  </div>
</section>
""" % (kc_next["week"], e(opp_line(kc_next, "KC")), e(when(kc_next, True)), e(where(kc_next)),
       (" · " + e(kc_next["tv"])) if kc_next["tv"] else "", sched_rows("KC"), chiefs_results,
       e(stay22("Arrowhead Stadium, Kansas City, MO")), e(FLIGHTS))

# ------------------------------------------------------------------ 32 teams
div_blocks = []
for dn in DIVISIONS:
    cards = []
    for a in sorted([t for t in TEAMS if TEAMS[t][1] == dn], key=lambda t: TEAMS[t][0]):
        name = TEAMS[a][0]
        venue, city = HOME[a]
        nxt = team_games(a)[0]
        links = '<a class="btn" href="%s" target="_blank" rel="sponsored noopener">Hotels near the stadium</a>' % e(stay22(venue + ", " + city))
        if a in HOST_CITY:
            links += '<a class="btn" href="host-cities/%s.html">City guide</a>' % HOST_CITY[a]
        cards.append("""<article class="team%s" id="team-%s">
  <h4>%s</h4>
  <p class="home">%s · %s</p>
  <p class="nx"><span>Next:</span> %s · %s</p>
  <details><summary>Remaining schedule</summary><ol class="sched">%s</ol></details>
  <div class="cta-row">%s</div>
</article>""" % (" kc" if a == "KC" else "", a.lower(), e(name), e(venue), e(city),
                 e(opp_line(nxt, a)), e(when(nxt)), sched_rows(a), links))
    div_blocks.append('<div class="division"><h3>%s</h3><div class="tgrid">%s</div></div>' % (dn, "".join(cards)))
teams_section = """
<section class="block" id="teams" aria-labelledby="teams-h">
  <h2 id="teams-h">All 32 teams</h2>
  <p class="lead">Every team by division, with its home stadium, next game and remaining 2026 schedule. Schedules come from each club's official website.</p>
  %s
</section>
""" % "".join(div_blocks)

# international games still to come
intl = [g for g in REMAINING if g["country"] not in ("USA", "")]
intl_html = "".join("<li><b>%s at %s</b> · %s · %s</li>" % (e(TEAMS[g["away"]][0]), e(TEAMS[g["home"]][0]), e(when(g)), e(where(g))) for g in intl)

travel_section = """
<section class="block travel" id="travel" aria-labelledby="travel-h">
  <h2 id="travel-h">Playoffs &amp; Super Bowl LXI travel</h2>
  <div class="two">
    <div>
      <h3>Super Bowl LXI · SoFi Stadium, Inglewood</h3>
      <p>Super Bowl LXI is set for SoFi Stadium in Inglewood, in the Los Angeles area, in February 2027. Hotels near the stadium sell out early, so book a refundable room now and adjust later.</p>
      <div class="cta-row">
        <a class="btn solid" href="%s" target="_blank" rel="sponsored noopener">Hotels near SoFi Stadium</a>
        <a class="btn" href="%s" target="_blank" rel="sponsored noopener">Flights to Los Angeles</a>
        <a class="btn" href="host-cities/los-angeles.html">Los Angeles guide</a>
      </div>
    </div>
    <div>
      <h3>Playoff trips</h3>
      <p>The playoffs start in January 2027, and home games go to the top seeds. If the Chiefs host a playoff game, it's at Arrowhead.</p>
      <div class="cta-row">
        <a class="btn solid" href="%s" target="_blank" rel="sponsored noopener">Hotels near Arrowhead</a>
        <a class="btn" href="%s" target="_blank" rel="sponsored noopener">Find flights</a>
      </div>
      <!-- AFFILIATE: tickets -->
    </div>
  </div>
  <h3 class="mt">Games abroad still to come</h3>
  <ul class="plain">%s</ul>
</section>
""" % (e(stay22("SoFi Stadium, Inglewood, CA")), e(FLIGHTS), e(stay22("Arrowhead Stadium, Kansas City, MO")), e(FLIGHTS), intl_html)

advertise_section = """
<section class="block advertise" id="advertise" aria-labelledby="adv-h">
  <h2 id="adv-h">Advertise on our NFL page</h2>
  <p>Put your business in front of NFL and soccer fans planning game days and road trips, with Kansas City fans first.</p>
  <a class="btn solid" href="%s" data-sdgx-form="inquiry" data-source="nfl page">Book your spot</a>
</section>
""" % e(ADVERTISE)

# ------------------------------------------------------------------ JSON-LD (only verified facts)
events = []
for g in team_games("KC"):
    if g["kickoffTBD"]:
        continue
    events.append({
        "@type": "SportsEvent",
        "name": "%s at %s" % (TEAMS[g["away"]][0], TEAMS[g["home"]][0]),
        "startDate": g["kickoff"],
        "eventStatus": "https://schema.org/EventScheduled",
        "location": {"@type": "Place", "name": g["venue"], "address": {"@type": "PostalAddress", "addressLocality": city_of(g), "addressCountry": g["country"] or "USA"}},
        "homeTeam": {"@type": "SportsTeam", "name": TEAMS[g["home"]][0]},
        "awayTeam": {"@type": "SportsTeam", "name": TEAMS[g["away"]][0]},
        "sport": "American football",
    })
ld = {
    "@context": "https://schema.org",
    "@graph": [
        {"@type": "WebPage", "@id": "https://sportdgx.com/nfl#webpage", "url": "https://sportdgx.com/nfl",
         "name": "NFL 2026 Season Hub", "dateModified": DATA["updated"],
         "description": "Kansas City Chiefs 2026 schedule, all 32 NFL teams by division, and playoff and Super Bowl LXI travel planning.",
         "isPartOf": {"@type": "WebSite", "name": "GO2CUP", "url": "https://sportdgx.com/"},
         "publisher": {"@type": "Organization", "name": "MainEntry LLC"}},
        {"@type": "ItemList", "name": "Kansas City Chiefs remaining 2026 games with confirmed dates",
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": ev} for i, ev in enumerate(events)]},
    ],
}

css = open(os.path.join(ROOT, "_tools", "nfl.css"), encoding="utf-8").read() + SWITCH_CSS
updated = datetime.fromisoformat(DATA["updated"]).strftime("%B ") + str(int(DATA["updated"][8:])) + ", " + DATA["updated"][:4]

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
<title>NFL 2026 Season Hub — Chiefs Schedule, All 32 Teams & Super Bowl Travel | GO2CUP</title>
<meta name="description" content="The Kansas City Chiefs' remaining 2026 schedule, all 32 NFL teams by division with their schedules, and playoff and Super Bowl LXI travel planning.">
<link rel="canonical" href="https://sportdgx.com/nfl">
<meta property="og:type" content="website">
<meta property="og:site_name" content="GO2CUP">
<meta property="og:title" content="NFL 2026 Season Hub">
<meta property="og:description" content="Chiefs schedule, all 32 teams by division, and playoff and Super Bowl LXI travel.">
<meta property="og:url" content="https://sportdgx.com/nfl">
<meta property="og:image" content="https://sportdgx.com/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<!-- Generated by _tools/build_nfl.py from data/nfl-2026-schedule.json. Edit those, not this file. -->
<script type="application/ld+json">
__LD__
</script>
<style>
__CSS__
</style>
</head>
<body>

<header>
  <nav class="nav" aria-label="Site">
    <a href="/" class="logo"><span class="b">GO</span><span class="w">2</span><span class="r">CUP</span></a>
    <div class="menu">
      <a href="/">Home</a>
      <a href="brazil-2027.html">Brazil 2027</a>
      <a href="nfl.html" class="active" aria-current="page">NFL</a>
      <a href="scoreboard.html">Scoreboard</a>
      <a href="where-to-stay.html">Where to Stay</a>
      <a href="sports-news.html">News</a>
    </div>
  </nav>
</header>
__BAR__
<section class="hero" aria-labelledby="hero-h">
  <div class="wrap">
    <h1 id="hero-h">NFL 2026 Season Hub</h1>
    <p>The Chiefs' road to the playoffs, all 32 teams and their schedules, and how to get to the big games, starting from Kansas City.</p>
    <div class="jump">
      <a href="#chiefs">Chiefs</a><a href="#teams">All 32 teams</a><a href="#travel">Super Bowl travel</a><a href="#advertise">Advertise</a>
    </div>
  </div>
</section>

<main class="wrap">
__CHIEFS__
__TEAMS__
__TRAVEL__
__ADVERTISE__
  <p class="fine">Schedules updated __UPDATED__ from each club's official website. Times are Central. Games can be moved by the NFL; check the club's site before you travel.</p>
</main>

<footer>
  <div class="wrap">
    GO2CUP is an independent fan and travel guide by MainEntry LLC. We are not affiliated with, endorsed by or sponsored by the NFL or any of its teams, venues or ticket sellers. Team names are used only to identify the teams.<br>
    GO2CUP may earn a commission from affiliate links. <a href="disclosure.html">Disclosure</a> · <a href="privacy.html">Privacy</a> · <a href="terms.html">Terms</a> · <a href="/">Home</a>
  </div>
</footer>
<script src="/assets/sdgx-forms.js" defer></script>
</body>
</html>
"""
for k, v in {"__LD__": json.dumps(ld, indent=1, ensure_ascii=False), "__CSS__": css, "__CHIEFS__": chiefs_section,
             "__TEAMS__": teams_section, "__TRAVEL__": travel_section, "__ADVERTISE__": advertise_section,
             "__UPDATED__": updated, "__BAR__": sport_bar("nfl.html")}.items():
    page = page.replace(k, v)
open(os.path.join(ROOT, "nfl.html"), "w", encoding="utf-8").write(page)
print("wrote nfl.html: %d remaining games, %d teams, %d Chiefs events in JSON-LD" % (len(REMAINING), len(TEAMS), len(events)))
