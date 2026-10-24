#!/usr/bin/env python3
"""World Cup 2026 is history on SportDGX: retire its offers and label its pages as an archive.

    python3 _tools/wc2026_archive.py

Safe to run again. What it does:
  1. Retired offers (Country Hopper, Mexico Trip Guide, trip budget calculator, trip panel,
     multi-city trip guide, VIP aviation, language hub, "intelligence hub") become short
     retirement notices at the same URL (noindex), pointing to the archive.
  2. Every link, button or form for those offers, every World Cup guide form and every
     resale-ticket (viagogo) link is removed site-wide.
  3. World Cup 2026 pages get an "archive" label; host-city pages get a note that the guide was
     first written for the tournament. Their titles and descriptions are rewritten in past tense,
     and World Cup FAQ/Event structured data is removed (Article data stays).
  4. Builds the archive hub /world-cup-2026.html and /404.html.
"""
import glob
import json
import os
import re
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_form_pages import FOOT, HEAD  # noqa: E402
from sports_nav import SWITCH_CSS, sport_bar  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL = "Spain beat Argentina 1–0 after extra time in the final at MetLife Stadium on July 19, 2026"

# ---------------------------------------------------------------- retired offers
RETIRED = {
    "hopper-guide.html": ("GO2CUP Fan Country Hopper Starter Guide",
                          "a free planning guide for traveling between the World Cup 2026 host countries"),
    "mexico-trip-guide.html": ("Mexico Trip Guide",
                               "a personalized trip-planning offer for the World Cup 2026 matches in Mexico"),
    "budget-calculator.html": ("World Cup 2026 Trip Budget Calculator",
                               "a cost calculator for World Cup 2026 trips"),
    "trip-panel.html": ("Plan Your World Cup Trip panel", "a booking panel for World Cup 2026 trips"),
    "articles/multi-city-world-cup-trip.html": ("Multi-City World Cup Trip guide (Country Hopper)",
                                                "a guide to planning a multi-city World Cup 2026 trip"),
    "fbo-vip.html": ("World Cup 2026 VIP Private Aviation guide",
                     "a private-aviation guide for World Cup 2026 travelers"),
    "interpreter-support.html": ("World Cup 2026 Global Language Access Hub",
                                 "a language-access hub for World Cup 2026 fans and venues"),
    "high-net-worth fans.html": ("World Cup Intelligence Hub 2026", "a World Cup 2026 VIP fan hub"),
}
RETIRED_HREF = (r'(?:hopper-guide|mexico-trip-guide|budget-calculator|trip-panel|multi-city-world-cup-trip|'
                r'fbo-vip|interpreter-support|high-net-worth(?:%20| )fans)(?:\.html)?(?:#[^"]*)?')
DEAD_LINK = re.compile(r'<a\b[^>]*href="[^"]*(?:/|^|")?' + RETIRED_HREF + r'"[^>]*>.*?</a>'
                       r'|<a\b[^>]*data-sdgx-(?:form|inline)="guide"[^>]*>.*?</a>'
                       r'|<a\b[^>]*href="https?://(?:www\.)?viagogo\.[^"]*"[^>]*>.*?</a>'
                       r'|<a\b[^>]*href="#"[^>]*class="band-btn band-btn-(?:store|tickets)"[^>]*>.*?</a>', re.S | re.I)
DEAD_LI = re.compile(r'<li\b[^>]*>\s*(?:' + DEAD_LINK.pattern + r')\s*</li>', re.S | re.I)
# "Get Your Tickets" blocks that only sent fans to resale tickets
TICKET_BLOCK = re.compile(r'<h2[^>]*>[^<]*Tickets[^<]*</h2>(?:(?!<h2|</section>|<div class="related).)*?viagogo\.[^>]*>.*?</a>\s*',
                          re.S | re.I)

# ---------------------------------------------------------------- archive pages: new title + description
A = " (Archive) | GO2CUP"
ARCHIVE = {
    "article-1.html": ("Mexico vs. South Africa: The World Cup 2026 Opening Match" + A,
                       "Archived pre-match fan guide to the World Cup 2026 opening match at Estadio Azteca on June 11, 2026. Mexico beat South Africa 2–0."),
    "article-2.html": ("World Cup 2026 Host City Updates" + A,
                       "Archived pre-tournament notes on the World Cup 2026 host cities in the USA, Mexico and Canada: stadiums, fan zones and transport, as written before the tournament."),
    "article-3.html": ("The GO2CUP Fan Travel Playbook for World Cup 2026" + A,
                       "Archived World Cup 2026 fan travel playbook, written before the tournament (June 11 – July 19, 2026). Kept for the record; its travel offers are retired."),
    "articles/48-team-world-cup-explained.html": ("The 48-Team World Cup Explained" + A,
                       "World Cup 2026 was the first 48-team tournament: 12 groups, a new Round of 32 and 104 matches across the USA, Mexico and Canada. An explainer from the GO2CUP archive."),
    "articles/argentina-fans-kansas-city.html": ("Argentine Fans in Kansas City at World Cup 2026" + A,
                       "Archived pre-tournament guide for Argentina fans traveling to Kansas City for World Cup 2026, written before the matches were played."),
    "articles/argentina-world-cup-2026-gossip.html": ("Argentina at World Cup 2026: Pre-Tournament Squad News" + A,
                       "Archived pre-tournament squad news on Argentina at World Cup 2026. Argentina reached the final and lost 1–0 to Spain after extra time."),
    "articles/best-hotels-estadio-azteca.html": ("Hotels Near Estadio Azteca for World Cup 2026" + A,
                       "Archived pre-tournament hotel guide for World Cup 2026 matches at Estadio Azteca in Mexico City. Kept for the record; ticket and booking offers are retired."),
    "articles/bronze-final-england-france-2026.html": None,
    "articles/colombia-vs-ghana-kansas-city.html": ("Colombia vs Ghana in Kansas City: Round of 32 Fan Guide" + A,
                       "Archived matchday fan guide for Colombia vs Ghana at Kansas City Stadium on July 3, 2026, in the World Cup 2026 Round of 32."),
    "articles/colombia-vs-ghana-kansas-city-es.html": ("Colombia vs Ghana en Kansas City: Guía del Hincha (Archivo) | GO2CUP",
                       "Guía del hincha archivada para Colombia vs Ghana en el Kansas City Stadium, 3 de julio de 2026, dieciseisavos del Mundial 2026."),
    "articles/dallas-fan-guide.html": ("Dallas Fan Guide: World Cup 2026 at AT&T Stadium" + A,
                       "Archived pre-tournament fan guide to World Cup 2026 matches in Dallas at AT&T Stadium, Arlington. Kept for the record; ticket and booking offers are retired."),
    "articles/flights-to-world-cup.html": ("Flying to World Cup 2026: Host-City Routes" + A,
                       "Archived pre-tournament flight guide to the World Cup 2026 host cities in the USA, Mexico and Canada."),
    "articles/houston-fan-guide.html": ("Houston Fan Guide: World Cup 2026 at NRG Stadium" + A,
                       "Archived pre-tournament fan guide to World Cup 2026 matches in Houston at NRG Stadium. Kept for the record; ticket and booking offers are retired."),
    "articles/how-to-get-world-cup-tickets.html": ("How World Cup 2026 Ticketing Worked" + A,
                       "How World Cup 2026 ticketing worked: FIFA's lottery phases and official resale. An explainer from the GO2CUP archive."),
    "articles/in-memoriam-jayden-adams.html": None,
    "articles/kansas-city-fan-guide.html": ("Kansas City Fan Guide: World Cup 2026 at Arrowhead Stadium" + A,
                       "Archived pre-tournament fan guide to World Cup 2026 matches in Kansas City at Arrowhead Stadium. Kept for the record; ticket and booking offers are retired."),
    "articles/kansas-city-matchday-tips.html": ("Kansas City World Cup 2026 Matchday Tips" + A,
                       "Archived matchday tips for World Cup 2026 games in Kansas City: parking, BBQ and fan zones, as written before the tournament."),
    "articles/los-angeles-fan-guide.html": ("Los Angeles Fan Guide: World Cup 2026 at SoFi Stadium" + A,
                       "Archived pre-tournament fan guide to World Cup 2026 matches at SoFi Stadium in Inglewood. Kept for the record; ticket and booking offers are retired."),
    "articles/messi-yamal-full-circle.html": None,
    "articles/mexico-city-fan-guide.html": ("Mexico City Fan Guide: World Cup 2026 at Estadio Azteca" + A,
                       "Archived pre-tournament fan guide to World Cup 2026 in Mexico City and Estadio Azteca. Kept for the record; ticket and booking offers are retired."),
    "articles/miami-fan-guide.html": ("Miami Fan Guide: World Cup 2026 at Hard Rock Stadium" + A,
                       "Archived pre-tournament fan guide to World Cup 2026 matches at Hard Rock Stadium in Miami Gardens. Kept for the record; ticket and booking offers are retired."),
    "articles/new-york-new-jersey-fan-guide.html": ("New York / New Jersey Fan Guide: World Cup 2026 at MetLife" + A,
                       "Archived pre-tournament fan guide to World Cup 2026 at MetLife Stadium, host of the July 19 final. Kept for the record; ticket and booking offers are retired."),
    "articles/safety-tips-mexico.html": ("Safety Tips for World Cup 2026 Fans in Mexico" + A,
                       "Archived safety guide written for World Cup 2026 fans visiting Mexico City, Guadalajara and Monterrey. Check current official travel advisories before any trip."),
    "articles/seattle-fan-guide.html": ("Seattle Fan Guide: World Cup 2026 at Lumen Field" + A,
                       "Archived pre-tournament fan guide to World Cup 2026 matches in Seattle at Lumen Field. Kept for the record; ticket and booking offers are retired."),
    "articles/toronto-fan-guide.html": ("Toronto Fan Guide: World Cup 2026 at BMO Field" + A,
                       "Archived pre-tournament fan guide to World Cup 2026 matches at BMO Field in Toronto. Kept for the record; ticket and booking offers are retired."),
    "articles/what-to-pack-world-cup.html": ("What to Pack for World Cup 2026: Fan Checklist" + A,
                       "Archived packing checklist written for World Cup 2026 fans, kept for the record."),
    "articles/world-cup-2026-aftermath.html": None,
    "articles/world-cup-budget-guide.html": ("World Cup 2026 Budget Guide" + A,
                       "Archived pre-tournament cost breakdown for attending World Cup 2026: budget, mid-range and luxury estimates as published before the tournament."),
    "articles/world-cup-final-2026-spain-argentina.html": None,
    "articles/world-cup-final-2026-where-to-stay.html": ("World Cup 2026 Final: Where Fans Stayed Near MetLife" + A,
                       "Archived pre-final travel guide for the World Cup 2026 Final at MetLife Stadium on July 19, 2026, which Spain won 1–0 after extra time. Booking offers are retired."),
    "articles/world-cup-match-schedule.html": ("World Cup 2026 Group Stage Schedule by Host City" + A,
                       "The World Cup 2026 group stage schedule by host city, as published before the tournament. For final scores, see the GO2CUP scoreboard."),
    "articles/world-cup-opening-ceremony.html": ("World Cup 2026 Opening Ceremony Preview" + A,
                       "Archived preview of the World Cup 2026 Opening Ceremony at Estadio Azteca on June 11, 2026. Mexico then beat South Africa 2–0 in the opening match."),
    "articles/world-cup-results-june-19-2026.html": None,
    "articles/world-cup-results-june-20-2026.html": None,
    "beyound-the-stadium.html": ("Beyond the Stadium: World Cup 2026 Opening Weekend in 16 Host Cities" + A,
                       "Archived snapshot of the World Cup 2026 opening weekend beyond the stadiums: fan zones, food and culture across the 16 host cities."),
    "blog.html": ("GO2CUP Blog: World Cup 2026 Archive | GO2CUP",
                  "The GO2CUP blog archive from World Cup 2026: host-city guides, ticketing explainers, match recaps and fan stories."),
    "blog/historic-firsts.html": ("Historic Firsts: The First 48-Team, Three-Nation World Cup" + A,
                       "World Cup 2026 was the first with 48 teams and three host nations. Its records and firsts, from the GO2CUP archive."),
    "emergency.html": ("World Cup 2026 Emergency Directory" + A,
                       "Archived emergency directory published for World Cup 2026 fans: 911, embassies and consulates in the USA, Mexico and Canada. Verify contacts with official sources."),
    "go2cup-emergency-directory-cleaned.html": ("World Cup 2026 Emergency Directory" + A,
                       "Archived emergency directory published for World Cup 2026 fans: 911, embassies and consulates in the USA, Mexico and Canada. Verify contacts with official sources."),
    "first-match-mexico.html": ("World Cup 2026 Opening Match: Mexico 2–0 South Africa" + A,
                       "Mexico beat South Africa 2–0 in the World Cup 2026 opening match at Estadio Azteca on June 11, 2026. Archived match page from GO2CUP."),
    "mexico-first-match.html": ("World Cup 2026 Opening Ceremony at Estadio Azteca" + A,
                       "The World Cup 2026 Opening Ceremony at Estadio Azteca, Mexico City, on June 11, 2026, followed by Mexico's 2–0 win over South Africa. Archived page."),
    "hot-takes.html": ("World Cup 2026 Team Analysis: The Good, The Bad & The Ugly" + A,
                       "Maria's World Cup 2026 read on every team, the Good, the Bad and the Ugly, kept in the GO2CUP archive."),
    "matches-board.html": ("World Cup 2026 Matches Board" + A, "The World Cup 2026 group-stage matches board, kept in the GO2CUP archive."),
    "newsletter-Farol.html": ("The Farol: Welcome Post (World Cup 2026 Archive) | GO2CUP",
                              "The Farol's welcome post from the run-up to World Cup 2026, kept in the GO2CUP archive."),
    "opening-ceremony-recap.html": None,
    "phase2-knockout.html": None,
    "r32-standings.html": None,
    "scoreboard.html": None,
    "streaming.html": None,
    "the-48-team-format.html": ("The World Cup 2026 48-Team Format Explained" + A,
                       "How the 48-team World Cup 2026 worked: 12 groups, 104 matches and the new Round of 32. An explainer from the GO2CUP archive."),
    "wc2026-matches-calendar.html": ("World Cup 2026 Full Match Calendar & Results" + A,
                       "All 104 World Cup 2026 matches, June 11 – July 19, 2026, with kickoff times and results. " + FINAL + "."),
    "worldcup-story.html": ("World Cup 2026: The Best, The Worst, The Unforgettable" + A,
                       "The best goals, biggest upsets and breakout stars of World Cup 2026, as GO2CUP covered them during the tournament."),
}

# ---------------------------------------------------------------- city guides (still useful)
CITY = {  # slug: (city name, stadium)
    "atlanta": ("Atlanta", "Mercedes-Benz Stadium"), "boston-foxborough": ("Boston", "Gillette Stadium"),
    "dallas": ("Dallas", "AT&T Stadium"), "guadalajara": ("Guadalajara", "Estadio Akron"),
    "houston": ("Houston", "NRG Stadium"), "kansas-city": ("Kansas City", "Arrowhead Stadium"),
    "los-angeles": ("Los Angeles", "SoFi Stadium"), "mexico-city": ("Mexico City", "Estadio Azteca"),
    "miami": ("Miami", "Hard Rock Stadium"), "monterrey": ("Monterrey", "Estadio BBVA"),
    "new-york-new-jersey": ("New York / New Jersey", "MetLife Stadium"),
    "philadelphia": ("Philadelphia", "Lincoln Financial Field"),
    "san-francisco-bay-area": ("San Francisco Bay Area", "Levi's Stadium"), "seattle": ("Seattle", "Lumen Field"),
    "toronto": ("Toronto", "BMO Field"), "vancouver": ("Vancouver", "BC Place"),
}
CITY_PAGES = {"host-cities/%s.html" % k: k for k in CITY}
CITY_PAGES.update({k + ".html": k for k in ["boston-foxborough", "dallas", "houston", "miami", "monterrey",
                                             "new-york-new-jersey", "seattle", "toronto"]})
CITY_PAGES["articles/best-neighborhoods-mexico-city.html"] = "mexico-city"


def city_meta(path, slug):
    name, stadium = CITY[slug]
    if path.startswith("articles/"):
        return ("Best Neighborhoods to Stay in Mexico City | GO2CUP",
                "Roma Norte, Condesa, Polanco, Reforma and Centro Histórico compared for visitors to Mexico City. First written for World Cup 2026.")
    return ("%s City Guide: %s, Neighborhoods & Things to Do | GO2CUP" % (name, stadium),
            "%s travel guide: %s, where to stay, getting around and must-sees. First written for World Cup 2026; match details are kept for the record." % (name, stadium))


# site-wide wording that described the site as a World Cup 2026 resource
REWORD = [
    ("Independent World Cup 2026 fan resource.", "Independent sports-news and fan-travel publisher."),
    ("fan-built World Cup 2026 travel intelligence hub", "fan-built sports and travel intelligence hub"),
    ("fan-built World Cup 2026 resource", "fan-built sports and fan-travel resource"),
    ("travel-planning resource for World Cup 2026", "travel-planning resource for sports fans"),
    ("your independent World Cup 2026 fan travel resource for USA, Mexico, and Canada", "your independent sports and fan-travel guide"),
    ("Booking.com and Viagogo links", "Booking.com links"),
]

BOX = ('style="background:#0a2413;border-bottom:2px solid #f5c518;color:#e8f2ec;font:15px/1.5 Inter,system-ui,sans-serif;'
       'padding:10px 18px;text-align:center;position:relative;z-index:50"')
LINK = 'style="color:#f5c518;font-weight:700;white-space:nowrap"'
BANNER = ('<!-- WC2026-ARCHIVE:START --><div class="wc26-archive-note" role="note" %s><strong style="font-family:Oswald,sans-serif;'
          'letter-spacing:.06em;text-transform:uppercase;color:#f5c518">World Cup 2026 archive</strong> &middot; The tournament was played '
          'June 11 &ndash; July 19, 2026, and Spain won the final. This page is kept for the record as first published; its dates, '
          'offers and travel advice are no longer active. <a href="/world-cup-2026.html" %s>Browse the archive &rarr;</a></div>'
          '<!-- WC2026-ARCHIVE:END -->') % (BOX, LINK)
CITY_NOTE = ('<!-- WC2026-ARCHIVE:START --><div class="wc26-archive-note" role="note" %s><strong style="font-family:Oswald,sans-serif;'
             'letter-spacing:.06em;text-transform:uppercase;color:#f5c518">Note</strong> &middot; This city guide was first written for '
             'World Cup 2026, which ended on July 19, 2026. Neighborhood, transport and attraction tips still apply; World Cup match '
             'details are kept for the record. <a href="/world-cup-2026.html" %s>World Cup 2026 archive &rarr;</a></div>'
             '<!-- WC2026-ARCHIVE:END -->') % (BOX, LINK)

# ---------------------------------------------------------------- hand edits (sentences that pointed at retired offers)
MANUAL = {
    "articles/best-hotels-estadio-azteca.html": [
        (re.compile(r'\s*Planning your full Mexico trip\? Our <a[^>]*mexico-trip-guide[^>]*>[^<]*</a>[^.<]*\.', re.S), ""),
    ],
    "articles/best-neighborhoods-mexico-city.html": [
        (re.compile(r' or read our comprehensive <a[^>]*mexico-trip-guide[^>]*>[^<]*</a>'), ""),
    ],
    "articles/how-to-get-world-cup-tickets.html": [
        (re.compile(r'\s*<li><strong>Viagogo</strong>.*?</li>', re.S), ""),
        (re.compile(r'\s*<div class="cta-box">\s*<p><strong>Search available World Cup 2026 tickets on Viagogo.*?</div>', re.S), ""),
        (re.compile(r'\s*<!-- NEWSLETTER MID -->\s*<div class="newsletter-box">\s*<h3>Ticket Drop Alerts</h3>.*?</div>', re.S), ""),
    ],
    "article-3.html": [
        (re.compile(r'\s*<div class="step-item">\s*<div class="step-num">01</div>\s*<div class="step-content">\s*'
                    r'<div class="step-title">Secondary Market \(StubHub, Viagogo\)</div>.*?</div>\s*</div>\s*</div>', re.S), ""),
        (re.compile(r'The GO2CUP "Country Hopper" approach'), "The GO2CUP approach"),
    ],
    "articles/world-cup-opening-ceremony.html": [
        (re.compile(r'\s*Planning your whole Mexico visit\? Check our <a[^>]*mexico-trip-guide[^>]*>[^<]*</a>[^.<]*\.', re.S), ""),
    ],
}


# ---------------------------------------------------------------- World Cup booking blocks on archive pages
AFF = r'(?:tpk\.lu|tp\.media|aviasales|klook|tiqets|viator|kiwitaxi|airalo|yesim|booking\.com|expedia|getyourguide|go\.city|gocity|collect\.fifa\.com)'
AFF_LINK = re.compile(r'<a\b[^>]*href="https?://[^"]*' + AFF + r'[^"]*"[^>]*>.*?</a>', re.S | re.I)
ALL = "*"


def drop_h2(heading):  # an <h2 class="section"> block up to the next one
    return (re.compile(r'<h2 class="section">' + heading + r'</h2>.*?(?=<h2 class="section">)', re.S), "")


ARCHIVE_EDITS = {
    ALL: [
        (re.compile(r'<div class="aff">.*?</div>\s*</div>', re.S), ""),
        (re.compile(r'<div class="cta-box">\s*<div class="cta-box-label">[^<]*</div>\s*<h3>[^<]*</h3>\s*<p>.*?</p>\s*'
                    r'<div class="cta-btn-row">.*?</div>\s*</div>', re.S), ""),
        (re.compile(r'How to Get Tickets for World Cup 2026 &mdash; Official &amp; Resale Options|'
                    r'How to Get Tickets for World Cup 2026 — Official &amp; Resale Options'), "How World Cup 2026 Ticketing Worked"),
    ],
    "beyound-the-stadium.html": [
        (re.compile(r'\s*<!-- GLOBAL CTA -->\s*<div class="global-cta">\s*<h2>Heading to a Host City\?</h2>.*?</div>\s*</div>', re.S), ""),
    ],
    "articles/colombia-vs-ghana-kansas-city.html": [
        drop_h2(r"Book Kansas City — Before It Sells Out"), drop_h2(r"Traveling With Family\?"),
        drop_h2(r"Flight Delayed or Canceled\?")],
    "articles/colombia-vs-ghana-kansas-city-es.html": [
        drop_h2(r"Reserve Kansas City — Antes de Que Se Agote"), drop_h2(r"¿Viaja en Familia\?"),
        drop_h2(r"¿Vuelo Retrasado o Cancelado\?")],
    "first-match-mexico.html": [
        (re.compile(r'\s*<!-- HERO AFFILIATE CTAs -->\s*<div class="subscribe-section">.*?</p>\s*</div>\s*</section>', re.S), "\n</section>"),
        (re.compile(r'<div class="caas-inline">.*?<div class="caas-inline-btns">.*?</div>\s*</div>\s*</div>', re.S), ""),
        (re.compile(r'<div class="cta-caas-wrapper">.*?<p class="cta-hub-note">.*?</p>\s*</div>', re.S), ""),
    ],
    "worldcup-story.html": [
        (re.compile(r'<h3 class="book-head">Plan Your Final Weekend</h3>.*?(?=</section>)', re.S), ""),
        (re.compile(r'<div class="countdown-inner">.*?Countdown to the Final · July 19, 2026 · MetLife Stadium\s*</div>\s*</div>', re.S),
         '<div class="countdown-inner">\n    <div class="cd-event-label" style="border-left:0;padding-left:0;text-align:center">\n'
         '      <strong>🏆 FINAL RESULT</strong>\n      Spain 1–0 Argentina (a.e.t.) · July 19, 2026 · MetLife Stadium\n    </div>\n  </div>'),
    ],
    "phase2-knockout.html": [
        (re.compile(r'\s*<!-- ===== SLIM AFFILIATE STRIP[^>]*-->\s*<div class="p2-aff">.*?</div>', re.S), ""),
    ],
    "articles/world-cup-final-2026-where-to-stay.html": [
        (re.compile(r'\s*<div class="book">\s*<p class="book-label">Book Your Trip</p>.*?</div>\s*</div>', re.S), ""),
        (re.compile(r'\s*<h3>Save with a city pass</h3>.*?<div class="gold-pass-container">.*?</div>', re.S), ""),
        (re.compile(r'\s*<div class="callout">\s*<strong>Traveling light.*?</div>\s*</div>', re.S), ""),
        (re.compile(r'\s*<p>Whichever you pick, <strong>book now\.</strong>[^<]*</p>'), ""),
    ],
    "articles/world-cup-budget-guide.html": [
        (re.compile(r'\s*<!-- CTA -->\s*<div class="cta-box">\s*<h3>Ready to Book Your Stay\?</h3>.*?</div>', re.S), ""),
        (re.compile(r'\s*<p>For ticket purchasing, check the secondary market on\s+—[^<]*</p>'), ""),
    ],
    "articles/48-team-world-cup-explained.html": [
        (re.compile(r'\s*<!-- NEWSLETTER MID -->\s*<div class="newsletter-box">\s*<h3>Plan Your 2026 World Cup Trip</h3>.*?</div>', re.S), ""),
    ],
    "hot-takes.html": [
        (re.compile(r'\s*<div class="trip">\s*<p>Headed to one of these matches\?.*?</div>', re.S), ""),
        (re.compile(r'<section[^>]*>\s*<a href="articles/world-cup-final-2026-where-to-stay\.html"[^>]*>.*?</section>\s*', re.S), ""),
        (re.compile(r'plus my honest, data-aware read on who can win it\. Sent through the tournament\. Free\.'),
         "Maria's honest takes now cover the NFL, NBA, soccer and more in the free Weekend Game Plan email."),
    ],
    "go2cup-emergency-directory-cleaned.html": [
        (re.compile(r'\s*<li><a href="/go2cup/free-guide"[^>]*>Free Guide</a></li>'), ""),
    ],
    "article-3.html": [
        (re.compile(r'MULTI-CITY PLANNING: THE COUNTRY HOPPER APPROACH'), "MULTI-CITY PLANNING"),
    ],
    "the-48-team-format.html": [(re.compile(r'World Cup 2026 Planning Guide'), "World Cup 2026 Explainer")],
    "newsletter-Farol.html": [
        (re.compile(r'<div class="countdown-bar" id="countdown">.*?<span class="countdown-label">SEC</span>\s*</div>\s*</div>', re.S),
         '<div class="countdown-bar" id="countdown"><span style="font-family:Bebas Neue,sans-serif;font-size:18px;letter-spacing:2px;color:#f5c518;">'
         'WORLD CUP 2026 IS HISTORY &middot; SPAIN WON THE FINAL</span></div>'),
        (re.compile(r'<script>\s*// Live countdown to June 11, 2026 Opening Ceremony.*?</script>', re.S), ""),
    ],
}
# past tense for sentences that still described the tournament as ahead (archive and city pages)
TENSE = [
    ("World Cup will officially begin — and it will begin exactly", "World Cup officially began — and it began exactly"),
    ("Estadio Azteca in Mexico City will fall silent for one extraordinary moment — and then erupt. The 2026 World Cup Opening Ceremony will begin in",
     "Estadio Azteca in Mexico City fell silent for one extraordinary moment — and then erupted. The 2026 World Cup Opening Ceremony began in"),
    ("the Opening Ceremony will take place on the Azteca pitch", "the Opening Ceremony took place on the Azteca pitch"),
    ("Argentina is coming to the 2026 World Cup to defend", "Argentina came to the 2026 World Cup to defend"),
    (" will host ", " hosted "),
]


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def set_meta(s, title, desc):
    t, d = escape(title, quote=False), escape(desc)
    s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % t, s, count=1, flags=re.S)
    for attr, name, val in [("name", "description", d), ("property", "og:title", escape(title)),
                            ("property", "og:description", d), ("name", "twitter:title", escape(title)),
                            ("name", "twitter:description", d)]:
        pat = re.compile(r'<meta\s+%s="%s"\s+content="[^"]*"\s*/?>' % (attr, re.escape(name)))
        tag = '<meta %s="%s" content="%s">' % (attr, name, val)
        if pat.search(s):
            s = pat.sub(lambda m: tag, s, count=1)
        elif name == "description":
            s = s.replace("</title>", "</title>\n" + tag, 1)
    return s


DROP_TYPES = {"FAQPage", "Event", "SportsEvent", "Question"}


def clean_jsonld(s, desc):
    def fix(m):
        raw = m.group(2)
        try:
            data = json.loads(raw)
        except ValueError:
            return m.group(0)  # leave anything we can't read safely

        def keep(node):
            t = node.get("@type") if isinstance(node, dict) else None
            t = t if isinstance(t, list) else [t]
            return not any(x in DROP_TYPES for x in t)

        def touch(node):
            if isinstance(node, dict) and desc and any(x in ("Article", "NewsArticle", "BlogPosting", "WebPage")
                                                       for x in (node.get("@type") if isinstance(node.get("@type"), list) else [node.get("@type")])):
                node["description"] = desc
            return node

        if isinstance(data, dict) and "@graph" in data:
            data["@graph"] = [touch(n) for n in data["@graph"] if keep(n)]
            if not data["@graph"]:
                return ""
        elif isinstance(data, dict):
            if not keep(data):
                return ""
            touch(data)
        elif isinstance(data, list):
            data = [touch(n) for n in data if keep(n)]
            if not data:
                return ""
        return m.group(1) + "\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n" + m.group(3)
    return re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)', fix, s, flags=re.S)


def add_banner(s, html):
    s = re.sub(r'\n?<!-- WC2026-ARCHIVE:START -->.*?<!-- WC2026-ARCHIVE:END -->', '', s, flags=re.S)
    m = re.search(r'<body\b[^>]*>', s, re.I)
    return s[:m.end()] + "\n" + html + s[m.end():] if m else s


def strip_offers(path, s):
    for pat, new in MANUAL.get(path, []):
        s = pat.sub(new, s)
    if path in ARCHIVE:
        for pat, new in ARCHIVE_EDITS.get(path, []) + ARCHIVE_EDITS[ALL]:
            s = pat.sub(new, s)
        s = AFF_LINK.sub("", s)
    if path in ARCHIVE or path in CITY_PAGES:
        for a, b in TENSE:
            s = s.replace(a, b)
    s = TICKET_BLOCK.sub("", s)
    s = DEAD_LI.sub("", s)
    s = DEAD_LINK.sub("", s)
    return s


def page(slug, title, desc, body, noindex=False):
    html = HEAD % {"title": escape(title, quote=False), "desc": escape(desc), "slug": slug, "switch": SWITCH_CSS,
                   "bar": sport_bar(""), "cur_ins": "", "cur_adv": ""} + body + FOOT
    html = html.replace("<!-- Generated by _tools/build_form_pages.py. Edit that, not this file. -->",
                        "<!-- Generated by _tools/wc2026_archive.py. Edit that, not this file. -->")
    if noindex:
        html = html.replace('<meta name="theme-color"', '<meta name="robots" content="noindex">\n<meta name="theme-color"')
    return html


def retired_page(path, name, what):
    slug = path[:-5].replace(" ", "%20")
    body = """
<section class="hero" aria-labelledby="h1">
  <div class="wrap" style="display:block;max-width:760px">
    <p class="kicker">Retired &middot; World Cup 2026</p>
    <h1 id="h1">This offer has <span>ended</span></h1>
    <p class="lead">The <strong>%s</strong> was %s. World Cup 2026 ended on July 19, 2026, so it is no longer offered, downloaded or emailed.</p>
    <p class="lead">Our coverage of the tournament, including results and the guides we published, is in the <a href="/world-cup-2026.html">World Cup 2026 archive</a>.</p>
    <p class="lead"><a href="/brazil-2027.html">Women's World Cup Brazil 2027</a> &middot; <a href="/sports-news.html">Latest sports news</a> &middot; <a href="/insider.html">SportDGX Insider</a></p>
  </div>
</section>
""" % (escape(name), escape(what))
    return page(slug, "%s (Retired) | GO2CUP" % name, "The %s has been retired. World Cup 2026 coverage is in the GO2CUP archive." % name,
                body, noindex=True)


def hub():
    def li(href, text, note=""):
        return '<div class="card"><h3><a href="%s">%s</a></h3>%s</div>' % (href, text, "<p>%s</p>" % note if note else "")
    results = [("/articles/world-cup-final-2026-spain-argentina.html", "The Final: Spain 1–0 Argentina (a.e.t.)", "July 19, 2026, MetLife Stadium."),
               ("/articles/bronze-final-england-france-2026.html", "Third place: England 6–4 France", "The highest-scoring bronze final."),
               ("/scoreboard.html", "Scoreboard", "Every World Cup 2026 result."),
               ("/wc2026-matches-calendar.html", "Full match calendar", "All 104 matches with results."),
               ("/r32-standings.html", "Final group standings & Round of 32", ""),
               ("/phase2-knockout.html", "How the knockout stage began", ""),
               ("/first-match-mexico.html", "Opening match: Mexico 2–0 South Africa", "June 11, 2026, Estadio Azteca."),
               ("/opening-ceremony-recap.html", "Opening Ceremony & Match Day 1 recap", ""),
               ("/articles/world-cup-results-june-19-2026.html", "June 19 results", ""),
               ("/articles/world-cup-results-june-20-2026.html", "June 20 results", ""),
               ("/articles/world-cup-2026-aftermath.html", "After the final: July 19–23", ""),
               ("/worldcup-story.html", "The best, the worst, the unforgettable", "")]
    stories = [("/articles/messi-yamal-full-circle.html", "Messi, Yamal and the photo that predicted a final", ""),
               ("/articles/in-memoriam-jayden-adams.html", "In memoriam: Jayden Adams", ""),
               ("/hot-takes.html", "Team analysis: the Good, the Bad & the Ugly", ""),
               ("/blog/historic-firsts.html", "Historic firsts: 48 teams, three hosts", ""),
               ("/the-48-team-format.html", "The 48-team format explained", ""),
               ("/articles/how-to-get-world-cup-tickets.html", "How the ticketing worked", ""),
               ("/streaming.html", "Where the tournament aired", "")]
    guides = [(p, ARCHIVE[p][0].split(" (Archive)")[0]) for p in sorted(ARCHIVE) if ARCHIVE[p] and "fan-guide" in p]
    guides += [("/host-cities/%s.html" % k, "%s city guide" % v[0]) for k, v in CITY.items()]
    body = """
<section class="hero" aria-labelledby="h1">
  <div class="wrap" style="display:block;max-width:900px">
    <p class="kicker">Archive &middot; June 11 &ndash; July 19, 2026</p>
    <h1 id="h1">World Cup 2026 <span>Archive</span></h1>
    <p class="lead">The first 48-team World Cup was played across the United States, Mexico and Canada. %s. This page collects GO2CUP's coverage for the record.</p>
  </div>
</section>
<main class="wrap">
  <h2>Results &amp; records</h2>
  <div class="grid">%s</div>
  <h2>Stories &amp; explainers</h2>
  <div class="grid">%s</div>
  <h2>Pre-tournament guides (archived)</h2>
  <p class="fine">Written before or during the tournament and kept as first published. Their dates, ticket notes and booking links are no longer active. City tips on the host-city pages still apply.</p>
  <div class="grid">%s</div>
  <h2>What's next</h2>
  <div class="grid">%s%s%s</div>
  <p class="fine">GO2CUP / SportDGX is an independent publisher by MainEntry LLC and is not affiliated with FIFA.</p>
</main>
""" % (FINAL, "".join(li(*r) for r in results), "".join(li(*r) for r in stories),
       "".join(li("/" + p if not p.startswith("/") else p, t) for p, t in guides),
       li("/brazil-2027.html", "Women's World Cup Brazil 2027", "June 24 – July 25, 2027."),
       li("/world-cup-history.html", "World Cup history, 1930–2026", ""),
       li("/sports-news.html", "Latest sports news", ""))
    return page("world-cup-2026", "World Cup 2026 Archive: Results, Stories & Guides | GO2CUP",
                "The GO2CUP World Cup 2026 archive: " + FINAL + ". Results, match recaps, stories and the guides we published.", body)


def not_found():
    body = """
<section class="hero" aria-labelledby="h1">
  <div class="wrap" style="display:block;max-width:760px">
    <p class="kicker">404</p>
    <h1 id="h1">Page <span>not found</span></h1>
    <p class="lead">This page or file isn't here. Visit the home page for current coverage or browse the <a href="/world-cup-2026.html">World Cup 2026 archive</a>.</p>
    <p class="lead"><a href="/">SportDGX home</a> &middot; <a href="/sports-news.html">Latest news</a> &middot; <a href="/brazil-2027.html">Brazil 2027</a></p>
  </div>
</section>
"""
    return page("404", "Page Not Found | SportDGX", "This page could not be found.", body, noindex=True)


def main():
    pages = [p for p in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True) if "/_" not in rel(p) and not rel(p).startswith("_")]
    changed = []
    for p in sorted(pages):
        r = rel(p)
        if r in ['hopper-guide.html','mexico-trip-guide.html','articles/multi-city-world-cup-trip.html']:
            os.remove(p)
            changed.append(r)
            continue
        if r in RETIRED:
            new = retired_page(r, *RETIRED[r])
        elif r in ("world-cup-2026.html", "404.html"):
            continue
        else:
            s = open(p, encoding="utf-8").read()
            new = strip_offers(r, s)
            if r in ARCHIVE:
                meta = ARCHIVE[r]
                if meta:
                    new = set_meta(new, *meta)
                new = clean_jsonld(new, meta[1] if meta else None)
                new = add_banner(new, BANNER)
            elif r in CITY_PAGES:
                meta = city_meta(r, CITY_PAGES[r])
                new = set_meta(new, *meta)
                new = clean_jsonld(new, meta[1])
                new = add_banner(new, CITY_NOTE)
                new = new.replace(">Between the Matches<", ">Things to Do<")
            for a, b in REWORD:
                new = new.replace(a, b)
            if new == s:
                continue
        open(p, "w", encoding="utf-8").write(new)
        changed.append(r)
    for slug, html in (("world-cup-2026.html", hub()), ("404.html", not_found())):
        open(os.path.join(ROOT, slug), "w", encoding="utf-8").write(html)
        changed.append(slug)
    print("pages written:", len(changed))


if __name__ == "__main__":
    main()
