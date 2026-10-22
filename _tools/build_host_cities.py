#!/usr/bin/env python3
"""Write the top of host-cities.html: ticker, "Cities we cover now", Brazil 2027 cities.

    python3 _tools/build_host_cities.py

Reads data/nfl-2026-schedule.json and data/sports/*.json, so the "next up" games and
the ticker refresh every time this runs. Everything below the WORLD CUP 2026 ARCHIVE
marker is left untouched.
"""
import json
import os
import re
from datetime import date, datetime
from html import escape
from urllib.parse import quote
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "host-cities.html")
TODAY = datetime.now(ZoneInfo("America/Chicago")).date()
FLIGHTS = "https://aviasales.tpk.lu/gsLDMhOV?marker=736515.worldcup26"
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

NFL = {"KC": "Chiefs", "DAL": "Cowboys", "ATL": "Falcons", "MIA": "Dolphins", "HOU": "Texans", "LAR": "Rams",
       "LAC": "Chargers", "NYG": "Giants", "NYJ": "Jets", "PHI": "Eagles", "SEA": "Seahawks", "SF": "49ers",
       "NE": "Patriots", "MIN": "Vikings", "LV": "Raiders", "DEN": "Broncos", "ARI": "Cardinals", "BUF": "Bills",
       "CIN": "Bengals", "WSH": "Commanders", "JAX": "Jaguars", "TB": "Buccaneers", "NO": "Saints", "CAR": "Panthers",
       "GB": "Packers", "DET": "Lions", "CHI": "Bears", "BAL": "Ravens", "PIT": "Steelers", "CLE": "Browns",
       "IND": "Colts", "TEN": "Titans"}

# slug, name, country code (FlagCDN), time zone, NFL home teams + stadium city in the data,
# teams by sport, main stadium for the hotel link, words that match events in data/sports
CITIES = [
    ("kansas-city", "Kansas City", "us", "America/Chicago", ["KC"], {"NFL": ["Chiefs"], "Soccer": ["Sporting KC", "KC Current"]}, "Arrowhead Stadium, Kansas City, MO", ["Kansas City"]),
    ("dallas", "Dallas", "us", "America/Chicago", ["DAL"], {"NFL": ["Cowboys"], "NBA": ["Mavericks"], "Soccer": ["FC Dallas"]}, "AT&T Stadium, Arlington, TX", ["Dallas", "Arlington"]),
    ("atlanta", "Atlanta", "us", "America/New_York", ["ATL"], {"NFL": ["Falcons"], "NBA": ["Hawks"], "Soccer": ["Atlanta United"]}, "Mercedes-Benz Stadium, Atlanta, GA", ["Atlanta"]),
    ("miami", "Miami", "us", "America/New_York", ["MIA"], {"NFL": ["Dolphins"], "NBA": ["Heat"], "Soccer": ["Inter Miami"]}, "Hard Rock Stadium, Miami Gardens, FL", ["Miami"]),
    ("houston", "Houston", "us", "America/Chicago", ["HOU"], {"NFL": ["Texans"], "NBA": ["Rockets"], "Soccer": ["Houston Dynamo", "Houston Dash"]}, "NRG Stadium, Houston, TX", ["Houston"]),
    ("los-angeles", "Los Angeles", "us", "America/Los_Angeles", ["LAR", "LAC"], {"NFL": ["Rams", "Chargers"], "NBA": ["Lakers", "Clippers"], "Soccer": ["LAFC", "LA Galaxy", "Angel City"]}, "SoFi Stadium, Inglewood, CA", ["Los Angeles", "Inglewood", "Carson"]),
    ("new-york-new-jersey", "New York / New Jersey", "us", "America/New_York", ["NYG", "NYJ"], {"NFL": ["Giants", "Jets"], "NBA": ["Knicks", "Nets"], "Soccer": ["NYCFC", "Red Bulls", "Gotham FC"]}, "MetLife Stadium, East Rutherford, NJ", ["New York", "Brooklyn", "Harrison", "East Rutherford"]),
    ("philadelphia", "Philadelphia", "us", "America/New_York", ["PHI"], {"NFL": ["Eagles"], "NBA": ["76ers"], "Soccer": ["Philadelphia Union"]}, "Lincoln Financial Field, Philadelphia, PA", ["Philadelphia"]),
    ("seattle", "Seattle", "us", "America/Los_Angeles", ["SEA"], {"NFL": ["Seahawks"], "Soccer": ["Sounders", "Seattle Reign"]}, "Lumen Field, Seattle, WA", ["Seattle"]),
    ("san-francisco-bay-area", "San Francisco Bay Area", "us", "America/Los_Angeles", ["SF"], {"NFL": ["49ers"], "NBA": ["Warriors"], "Soccer": ["Earthquakes", "Bay FC"]}, "Levi's Stadium, Santa Clara, CA", ["San Francisco", "Santa Clara", "San Jose"]),
    ("boston-foxborough", "Boston", "us", "America/New_York", ["NE"], {"NFL": ["Patriots"], "NBA": ["Celtics"], "Soccer": ["Revolution", "Boston Legacy"]}, "Gillette Stadium, Foxborough, MA", ["Boston", "Foxborough"]),
    ("toronto", "Toronto", "ca", "America/Toronto", [], {"NBA": ["Raptors"], "Soccer": ["Toronto FC"]}, "BMO Field, Toronto, ON", ["Toronto"]),
    ("vancouver", "Vancouver", "ca", "America/Vancouver", [], {"Soccer": ["Whitecaps"]}, "BC Place, Vancouver, BC", ["Vancouver"]),
    ("mexico-city", "Mexico City", "mx", "America/Mexico_City", [], {"Liga MX": ["América", "Cruz Azul", "Pumas"]}, "Estadio Banorte, Mexico City", ["Mexico City"]),
    ("guadalajara", "Guadalajara", "mx", "America/Mexico_City", [], {"Liga MX": ["Chivas", "Atlas"]}, "Estadio Akron, Guadalajara", ["Guadalajara"]),
    ("monterrey", "Monterrey", "mx", "America/Monterrey", [], {"Liga MX": ["Rayados", "Tigres"]}, "Estadio BBVA, Monterrey", ["Monterrey"]),
]
STADIUM_CITY = {"KC": "Kansas City", "DAL": "Arlington", "ATL": "Atlanta", "MIA": "Opa Locka", "HOU": "Houston",
                "LAR": "Inglewood", "LAC": "Inglewood", "NYG": "East Rutherford", "NYJ": "East Rutherford",
                "PHI": "Philadelphia", "SEA": "Seattle", "SF": "Santa Clara", "NE": "Foxborough"}
SPORT_COLOR = {"NFL": "#21c25a", "NBA": "#ff7a1a", "Soccer": "#2fe0c8", "Liga MX": "#2fe0c8", "UFC": "#ff4338", "F1": "#f5c518"}
SPORT_PAGE = {"NFL": "/nfl.html", "NBA": "/nba.html", "Soccer": "/soccer.html", "UFC": "/ufc.html", "Boxing": "/boxing.html", "Tennis": "/tennis.html", "F1": "/racing.html"}

BRAZIL = [
    ("Rio de Janeiro", "Estádio do Maracanã", "Opener · QF · Semi · Final"),
    ("São Paulo", "Neo Química Arena", "QF · Semi · 3rd place"),
    ("Belo Horizonte", "Mineirão", "Group stage → QF"),
    ("Brasília", "Estádio Mané Garrincha", "Group stage → R16"),
    ("Fortaleza", "Arena Castelão", "Group stage → QF"),
    ("Salvador", "Arena Fonte Nova", "Group stage → R16"),
    ("Recife", "Arena Pernambuco", "Group stage → R16"),
    ("Porto Alegre", "Estádio Beira-Rio", "Group stage → R16"),
]


def e(s):
    return escape(str(s), quote=True)


def hotels(address):
    return "https://www.stay22.com/allez/roam?aid=1607597&address=" + quote(address, safe="")


def d(iso):
    return date(*(int(x) for x in iso[:10].split("-")))


def short(dt):
    return "%s %s %d" % (DOW[dt.weekday()], MON[dt.month - 1], dt.day)


games = json.load(open(os.path.join(ROOT, "data", "nfl-2026-schedule.json"), encoding="utf-8"))["games"]
other = []  # (date, sport label, title, place, page)
for slug, label in [("nba", "NBA"), ("soccer", "Soccer"), ("ufc", "UFC"), ("boxing", "Boxing"), ("tennis", "Tennis"), ("racing", "F1")]:
    D = json.load(open(os.path.join(ROOT, "data", "sports", slug + ".json"), encoding="utf-8"))
    for sec in D["sections"]:
        for it in sec["items"]:
            if d(it.get("end", it["date"])) >= TODAY:
                other.append((d(it["date"]), label, it["title"], it.get("place", "") + " " + it.get("city", ""), SPORT_PAGE[label], it))


def next_up(c):
    slug, name, cc, tz, teams, _, _, words = c
    out = []
    for g in sorted([g for g in games if not g["played"] and g["kickoff"]], key=lambda g: g["kickoff"]):
        home_here = g["home"] in teams and g["city"] == STADIUM_CITY.get(g["home"])
        intl_here = g["city"] in words
        if home_here or intl_here:
            k = datetime.fromisoformat(g["kickoff"].replace("Z", "+00:00")).astimezone(ZoneInfo(tz))
            if k.date() < TODAY:
                continue
            t = k.strftime("%I:%M %p").lstrip("0") + " " + k.strftime("%Z").replace("CDT", "CT").replace("CST", "CT").replace("EDT", "ET").replace("EST", "ET").replace("PDT", "PT").replace("PST", "PT")
            out.append((k.date(), "NFL", "%s vs. %s" % (NFL[g["home"]], NFL[g["away"]]), "%s · %s" % (short(k), t), "/nfl.html"))
            break
    for dt, label, title, place, page, it in sorted(other, key=lambda x: x[0]):
        if any(re.search(r"\b%s\b" % re.escape(w), place, re.I) for w in words):
            when = short(dt) + ((" · " + it["time"]) if it.get("time") else "")
            out.append((dt, label, title, when, page))
    return sorted(out, key=lambda x: x[0])[:3]


def city_card(c):
    slug, name, cc, tz, teams, clubs, stadium, words = c
    chips = "".join('<span class="hc-chip" style="--sc:%s"><b>%s</b> %s</span>' % (SPORT_COLOR[s], e(s), e(" · ".join(t))) for s, t in clubs.items())
    ups = next_up(c)
    if ups:
        rows = "".join('<li><a href="%s"><span class="hc-tag" style="--sc:%s">%s</span><span class="hc-what">%s</span><span class="hc-when">%s</span></a></li>'
                       % (p, SPORT_COLOR.get(lbl, "#f5c518"), e(lbl), e(t), e(w)) for _, lbl, t, w, p in ups)
    else:
        rows = '<li class="hc-none">Nothing on our calendars here yet. The <a href="host-cities/%s.html">city guide</a> has things to do.</li>' % slug
    city_q = name.split(" / ")[0]
    return ('<article class="hc-card" id="city-%s">'
            '<div class="hc-top"><img src="https://flagcdn.com/w40/%s.png" width="28" height="19" alt="" loading="lazy">'
            '<h3><a href="host-cities/%s.html">%s</a></h3></div>'
            '<div class="hc-chips">%s</div>'
            '<p class="hc-lab">Next up</p><ul class="hc-up">%s</ul>'
            '<div class="hc-btns"><a class="hc-b hc-b1" href="%s" target="_blank" rel="sponsored noopener">Hotels near %s</a>'
            '<a class="hc-b" href="%s" target="_blank" rel="sponsored noopener">Flights</a>'
            '<a class="hc-b" href="host-cities/%s.html">City guide</a></div></article>'
            % (slug, cc, slug, e(name), chips, rows, e(hotels(stadium)), e(stadium.split(",")[0]), FLIGHTS, slug)) if city_q else ""


def brazil_card(b):
    name, stadium, role = b
    return ('<article class="hc-br"><div class="hc-top"><img src="https://flagcdn.com/w40/br.png" width="28" height="20" alt="" loading="lazy">'
            '<h3>%s</h3></div><p class="hc-stad">%s</p><p class="hc-role">%s</p>'
            '<div class="hc-btns"><a class="hc-b hc-b1" href="%s" target="_blank" rel="sponsored noopener">Hotels</a>'
            '<a class="hc-b" href="/brazil-2027.html#cities">Guide</a></div></article>'
            % (e(name), e(stadium), e(role), e(hotels(stadium + ", " + name + ", Brazil"))))


# ── ticker: next big events across every sport ──
tick = []  # (date, text)
nxt = sorted([g for g in games if not g["played"] and g["kickoff"] and "KC" in (g["home"], g["away"])], key=lambda g: g["kickoff"])
if nxt:
    g = nxt[0]
    k = datetime.fromisoformat(g["kickoff"].replace("Z", "+00:00")).astimezone(ZoneInfo("America/Chicago"))
    tick.append((k.date(), "%s %d: NFL · Chiefs %s %s" % (MON[k.month - 1].upper(), k.day, "vs" if g["home"] == "KC" else "at", NFL[g["home"] if g["away"] == "KC" else g["away"]])))
seen = {}
for dt, label, title, place, page, it in sorted(other, key=lambda x: x[0]):
    if seen.get(label, 0) >= 1 or d(it["date"]) < TODAY:
        continue
    seen[label] = seen.get(label, 0) + 1
    tick.append((dt, "%s %d: %s%s" % (MON[dt.month - 1].upper(), dt.day, "" if label.lower() in title.lower() else label + " · ", title.replace(" (c)", ""))))
tick.append((date(2026, 12, 11), "DEC 11: BRAZIL 2027 DRAW IN RIO"))
tick = [t for _, t in sorted(tick, key=lambda x: x[0])]
items = "".join('<span class="ticker-item"><span class="dot">●</span> %s</span>' % e(t.upper()) for t in tick)
ticker = '<div class="ticker-wrap">\n  <div class="ticker-track">\n    %s%s\n  </div>\n</div>' % (items, items)

css = """<style id="hc-css">
.hc-sec{max-width:1400px;margin:0 auto;padding:56px 22px 8px}
.hc-kick{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:12px;letter-spacing:.3em;text-transform:uppercase;color:var(--gold);margin:0 0 6px}
.hc-h{font-family:'Bebas Neue',sans-serif;font-size:clamp(2.4rem,5vw,4rem);line-height:.95;margin:0;color:#fff;letter-spacing:.5px}
.hc-lead{color:rgba(255,255,255,.62);max-width:720px;margin:10px 0 26px;font-size:15px;line-height:1.55}
.hc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.hc-card,.hc-br{background:#070d1f;border:1px solid rgba(255,255,255,.07);border-radius:18px;padding:18px 18px 16px;display:flex;flex-direction:column;gap:10px;transition:border-color .2s,transform .2s}
.hc-card:hover,.hc-br:hover{border-color:rgba(201,168,76,.5);transform:translateY(-2px)}
.hc-top{display:flex;align-items:center;gap:10px}
.hc-top img{border-radius:3px;flex:none}
.hc-top h3{font-family:'Bebas Neue',sans-serif;font-size:1.9rem;letter-spacing:.5px;margin:0;line-height:1}
.hc-top h3 a{color:#fff;text-decoration:none}.hc-top h3 a:hover{color:var(--gold)}
.hc-chips{display:flex;flex-wrap:wrap;gap:6px}
.hc-chip{font-family:'Barlow Condensed',sans-serif;font-size:12.5px;color:rgba(255,255,255,.8);border:1px solid color-mix(in srgb,var(--sc) 45%,transparent);background:color-mix(in srgb,var(--sc) 10%,transparent);border-radius:999px;padding:3px 10px}
.hc-chip b{color:var(--sc);letter-spacing:.06em;margin-right:2px}
.hc-lab{font-family:'Barlow Condensed',sans-serif;font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:rgba(255,255,255,.4);margin:4px 0 0}
.hc-up{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
.hc-up a{display:grid;grid-template-columns:auto 1fr;gap:2px 10px;text-decoration:none;padding:8px 10px;border-radius:10px;background:rgba(255,255,255,.035)}
.hc-up a:hover{background:rgba(255,255,255,.07)}
.hc-tag{grid-row:span 2;align-self:center;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:11px;letter-spacing:.08em;color:#020617;background:var(--sc);border-radius:5px;padding:2px 7px}
.hc-what{color:#fff;font-size:14px;font-weight:600;line-height:1.25}
.hc-when{color:rgba(255,255,255,.5);font-size:12.5px}
.hc-none{color:rgba(255,255,255,.5);font-size:13.5px;line-height:1.5}.hc-up .hc-none a{display:inline;padding:0;background:none;color:var(--gold);text-decoration:underline}
.hc-btns{display:flex;flex-wrap:wrap;gap:8px;margin-top:auto;padding-top:4px}
.hc-b{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:13px;letter-spacing:.08em;text-transform:uppercase;text-decoration:none;color:#fff;border:1px solid rgba(255,255,255,.18);border-radius:10px;padding:8px 12px}
.hc-b:hover{border-color:var(--gold);color:var(--gold)}
.hc-b1{background:var(--gold);border-color:var(--gold);color:#020617}.hc-b1:hover{background:#fff;color:#020617;border-color:#fff}
.hc-br-grid{grid-template-columns:repeat(auto-fill,minmax(230px,1fr))}
.hc-stad{margin:0;color:rgba(255,255,255,.75);font-size:14px}
.hc-role{margin:0;font-family:'Barlow Condensed',sans-serif;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#21c25a}
.hc-brazil{background:linear-gradient(180deg,rgba(33,194,90,.07),transparent 70%);border-top:1px solid rgba(33,194,90,.25);margin-top:48px;max-width:none}
.hc-brazil>*{max-width:1356px;margin-left:auto;margin-right:auto}
.hc-cta{display:inline-block;margin-top:18px;font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#21c25a;text-decoration:none}
.hc-arch{max-width:1400px;margin:64px auto 0;padding:0 22px;border-top:1px solid rgba(255,255,255,.08)}
.hc-arch .hc-h{font-size:clamp(2rem,4vw,3.2rem);padding-top:40px}
.hc-note{font-size:12px;color:rgba(255,255,255,.4);margin-top:14px}
@media(max-width:520px){.hc-sec{padding:40px 16px 4px}.hc-grid{grid-template-columns:1fr}}
</style>"""

top = """<!-- HOST CITIES NOW (generated by _tools/build_host_cities.py) -->
<section class="hc-sec" id="cities-now" aria-labelledby="hc-now-h">
  <p class="hc-kick">Updated %s</p>
  <h2 class="hc-h" id="hc-now-h">Cities we cover now</h2>
  <p class="hc-lead">The 16 World Cup 2026 cities are still sports cities every week. Here are the teams, the next big games, and hotels close to the stadium.</p>
  <div class="hc-grid">%s</div>
  <p class="hc-note">Schedules come from the official league and team sites. Kickoff times are local. Check the official site before you travel. Hotel and flight links are affiliate links; we may earn a commission at no extra cost to you.</p>
</section>
<section class="hc-sec hc-brazil" id="brazil-2027-cities" aria-labelledby="hc-br-h">
  <p class="hc-kick" style="color:#21c25a">Next: Women's World Cup · June 24 – July 25, 2027</p>
  <h2 class="hc-h" id="hc-br-h">Brazil 2027 host cities</h2>
  <p class="hc-lead">Eight cities, 64 matches, and the final at the Maracanã. Hotels in Rio and São Paulo fill up early, so it pays to look now.</p>
  <div class="hc-grid hc-br-grid">%s</div>
  <a class="hc-cta" href="/brazil-2027.html">Full Brazil 2027 fan guide &rarr;</a>
</section>
<div class="hc-arch" id="world-cup-2026-archive">
  <p class="hc-kick" style="padding-top:40px">Archive</p>
  <h2 class="hc-h" style="padding-top:0">World Cup 2026 host cities</h2>
  <p class="hc-lead">The 2026 tournament ran June 11 to July 19 across the United States, Mexico and Canada. Our city guides stay here for reference.</p>
</div>
<!-- /HOST CITIES NOW -->""" % ("%s %d, %d" % (["January","February","March","April","May","June","July","August","September","October","November","December"][TODAY.month - 1], TODAY.day, TODAY.year),
                            "".join(city_card(c) for c in CITIES), "".join(brazil_card(b) for b in BRAZIL))

s = open(PAGE, encoding="utf-8").read()
s = re.sub(r'<div class="ticker-wrap">.*?</div>\s*</div>', lambda m: ticker, s, count=1, flags=re.S)
s = re.sub(r'\n?<style id="hc-css">.*?</style>', "", s, flags=re.S)
s = s.replace("</head>", css + "\n</head>", 1)
if "<!-- HOST CITIES NOW" in s:
    s = re.sub(r"<!-- HOST CITIES NOW.*?<!-- /HOST CITIES NOW -->", lambda m: top, s, flags=re.S)
else:
    anchor = '<main class="max-w-[1700px] mx-auto px-6 py-12">'
    assert s.count(anchor) == 1
    s = s.replace(anchor, top + "\n\n" + anchor)
# one-time swaps of stale World Cup 2026 header text (no-ops once done)
for old, new in [
    ("<title>GO2CUP | Nation Hub</title>", "<title>Host Cities & Sports City Guides: NFL, NBA, Soccer, Brazil 2027 | SportDGX</title>"),
    ('<meta property="og:title" content="GO2CUP | Nation Hub">', '<meta property="og:title" content="Host Cities & Sports City Guides | SportDGX">'),
    ('<meta property="og:description" content="GO2CUP | Nation Hub">', '<meta property="og:description" content="Teams, next games and hotels near the stadium in 16 North American sports cities, plus the Brazil 2027 host cities.">'),
    ('<meta name="twitter:title" content="GO2CUP | Nation Hub">', '<meta name="twitter:title" content="Host Cities & Sports City Guides | SportDGX">'),
    ('<meta name="twitter:description" content="GO2CUP | Nation Hub">', '<meta name="twitter:description" content="Teams, next games and hotels near the stadium in 16 sports cities, plus the Brazil 2027 host cities.">\n<meta name="description" content="Teams, next games and hotels near the stadium in 16 North American sports cities, plus the Brazil 2027 host cities.">'),
    ('2026 FAN <span style="color:var(--gold)">GUIDE</span>', 'CITY <span style="color:var(--gold)">GUIDES</span>'),
    ('>Stadiums · Cities · Kickoffs<', '>Teams · Games · Hotels · Brazil 2027<'),
    ('<a href="/streaming.html" style="display:flex', '<a href="/brazil-2027.html" style="display:flex'),
    ('&#9654; Watch World Cup 2026 Live</span>', "&#9654; Next: Women's World Cup Brazil 2027</span>"),
    ('>Stream Now &rarr;</span>', '>Plan your trip &rarr;</span>'),
]:
    s = s.replace(old, new)
open(PAGE, "w", encoding="utf-8").write(s)
print("host cities: %d city cards, %d Brazil cards, ticker: %s" % (len(CITIES), len(BRAZIL), " | ".join(tick)))
for c in CITIES:
    print(" ", c[1], [(u[1], u[2], u[3]) for u in next_up(c)])
