#!/usr/bin/env python3
"""One-time homepage edit for the World Cup 2026 retirement (2026-10-23). Safe to run again."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "index.html")
s = open(P, encoding="utf-8").read()


def cut(s, start, end, new, keep_end=True):
    i = s.find(start)
    if i == -1:
        return s
    j = s.find(end, i)
    assert j != -1, end
    return s[:i] + new + (s[j:] if keep_end else s[j + len(end):])


# 1. World Cup FAQ structured data in <head>
s = re.sub(r'\n<script type="application/ld\+json">\s*\{\s*"@context":"https://schema.org",\s*"@type":"FAQPage".*?</script>\n', "\n", s, count=1, flags=re.S)

# 2. nav button: the retired guide becomes the newsletter
s = re.sub(r'(</ul>)\s*\n\s*\n(</nav>)',
           r'\1\n  <a href="/insider.html#join" data-sdgx-form="newsletter" data-source="homepage nav" class="nav-cta">GET THE WEEKEND GAME PLAN →</a>\n\2', s, count=1)

# 3. tournament stats row (present tense)
s = cut(s, "<!-- STATS ROW -->", "<!-- EXPLORE GO2CUP -->", "")

# 4. quick links
s = s.replace('<p class="cat-desc">Latest World Cup 2026, NFL, Chiefs, Formula One, and sports-business updates.</p>\n        <div class="cat-tags"><span class="cat-tag">World Cup</span>',
              '<p class="cat-desc">Latest NFL, Chiefs, NBA, soccer, UFC, boxing, tennis and Formula One news.</p>\n        <div class="cat-tags"><span class="cat-tag">Soccer</span>')
s = s.replace('<div class="cat-title">World Cup Host Cities</div>\n        <p class="cat-desc">Follow host-city travel, fan zones, stadium areas, and World Cup planning.</p>\n        <div class="cat-tags"><span class="cat-tag">16 Cities</span><span class="cat-tag">USA · MX · CA</span></div>',
              '<div class="cat-title">City Guides</div>\n        <p class="cat-desc">Teams, next games, stadiums and hotels in 16 North American sports cities.</p>\n        <div class="cat-tags"><span class="cat-tag">16 Cities</span><span class="cat-tag">NFL · NBA · Soccer</span></div>')
s = s.replace('<a href="/world-cup-history.html" class="cat-card gold">', '<a href="/world-cup-2026.html" class="cat-card gold">\n        <span class="cat-icon">🏆</span>\n        <div class="cat-title">World Cup 2026 Archive</div>\n        <p class="cat-desc">Results, recaps and the guides we published. Spain won the final.</p>\n        <div class="cat-tags"><span class="cat-tag">Archive</span><span class="cat-tag">June 11 – July 19, 2026</span></div>\n        <div class="cat-arrow">↗</div>\n      </a>\n      <a href="/world-cup-history.html" class="cat-card gold">', 1) if 'href="/world-cup-2026.html" class="cat-card gold"' not in s else s

# 5. guide promos, World Cup hub sections -> business + newsletter
BIZ = '''<!-- BUSINESS DIRECTORY -->
<section class="biz-section" id="business">
  <div class="biz-bg-word">BUSINESS</div>
  <div class="biz-inner fade-in">
    <div>
      <div class="biz-label">For Local Business &amp; Entrepreneurs</div>
      <h2 class="biz-title">FANS ARE<br>COMING TO<br><span>YOUR CITY.</span></h2>
      <p class="biz-body">
        Every NFL Sunday, NBA night, title fight and big match brings visitors who need a place to eat, sleep, park and celebrate. Put your business on the SportDGX city and sport pages fans read before they go.
      </p>
      <div class="biz-cta-wrap">
        <a href="/advertise.html#inquiry" data-sdgx-form="inquiry" data-source="homepage business section" class="btn-white">Advertise With Us →</a>
        <a href="/advertise.html" class="btn-outline-white">See Placements</a>
      </div>
    </div>
    <div>
      <p style="font-family:'Oswald',sans-serif;font-size:13px;letter-spacing:.15em;text-transform:uppercase;color:rgba(255,255,255,.6);margin:0 0 14px;">Who advertises with us</p>
      <div class="biz-categories">
        <a href="/advertise.html" class="biz-cat"><span class="biz-cat-icon">🍴</span><div class="biz-cat-title">Restaurants &amp; Bars</div><div class="biz-cat-desc">Get found by fans looking for food and watch parties near the stadium.</div></a>
        <a href="/advertise.html" class="biz-cat"><span class="biz-cat-icon">🏨</span><div class="biz-cat-title">Hotels &amp; Rentals</div><div class="biz-cat-desc">Reach fans booking a stay for game day.</div></a>
        <a href="/advertise.html" class="biz-cat"><span class="biz-cat-icon">🚌</span><div class="biz-cat-title">Parking, Transport &amp; Tours</div><div class="biz-cat-desc">Shuttles, parking, drivers and tours for game-day crowds.</div></a>
        <a href="/advertise.html" class="biz-cat"><span class="biz-cat-icon">🛍</span><div class="biz-cat-title">Retail &amp; Services</div><div class="biz-cat-desc">From team gear to local services, be found before the game.</div></a>
        <a href="/advertise.html" class="biz-cat"><span class="biz-cat-icon">🎭</span><div class="biz-cat-title">Entertainment &amp; Events</div><div class="biz-cat-desc">Viewing parties, concerts and fan events.</div></a>
        <a href="/advertise.html" class="biz-cat"><span class="biz-cat-icon">💼</span><div class="biz-cat-title">Brands &amp; Sponsors</div><div class="biz-cat-desc">Sponsored placements and partnerships, clearly labeled.</div></a>
      </div>
    </div>
  </div>
</section>
<!-- FOMO NEWSLETTER -->
<section class="fomo-strip" id="newsletter">
  <div class="fomo-title">
    GET THE FREE<br>
    WEEKEND <span>GAME PLAN.</span>
  </div>
  <p class="fomo-body">
    One email before every weekend: the big games, the cheapest seats we can find from official and trusted sellers, and a hotel near the stadium.
  </p>
  <div>
    <a href="/insider.html#join" data-sdgx-form="newsletter" data-source="homepage newsletter strip" class="btn-white">Join SportDGX Insider →</a>
  </div>
  <div class="fomo-micro">Free weekly email. Unsubscribe anytime. We never sell your email.</div>
</section>
'''
s = cut(s, "<!-- PLANNING KIT CALLOUT -->", "<!-- ANCHOR TARGETS FOR NAV -->", BIZ)

# 6. category nav: World Cup emergency pages -> current hubs
s = s.replace('<a href="emergency.html" class="nav-blue">✈️ Safety</a>\n  <a href="emergency.html" class="nav-red">🆘 US • MX • CA</a>',
              '<a href="nfl.html" class="nav-blue">🏈 NFL</a>\n  <a href="world-cup-2026.html" class="nav-red">🏆 WC 2026 Archive</a>')
s = s.replace('<a href="host-cities.html" class="nav-gold">🏆 Host City</a>', '<a href="host-cities.html" class="nav-gold">🏙️ City Guides</a>')

# 7. World Cup FAQ, host-nation cards, champions banner and results -> one archive section
ARCHIVE = '''<!-- WORLD CUP 2026 ARCHIVE (the tournament ended July 19, 2026; full coverage at /world-cup-2026.html) -->
<section id="wc2026-archive" aria-labelledby="wc26-h" style="background:#07180e;border-top:1px solid rgba(245,197,24,.35);padding:56px 18px;color:#e8f2ec;font-family:Inter,system-ui,sans-serif;">
  <div style="max-width:1100px;margin:0 auto;">
    <p style="font-family:'Oswald',sans-serif;font-size:13px;letter-spacing:.3em;text-transform:uppercase;color:#f5c518;margin:0 0 8px;">Archive &middot; June 11 &ndash; July 19, 2026</p>
    <h2 id="wc26-h" style="font-family:'Bebas Neue',sans-serif;font-weight:400;font-size:clamp(2.6rem,6vw,4.4rem);line-height:.95;margin:0 0 14px;color:#fff;">World Cup 2026 <span style="color:#f5c518;">Archive</span></h2>
    <p style="font-size:17px;max-width:760px;margin:0 0 22px;color:rgba(232,242,236,.85);">
      <img src="https://flagcdn.com/w40/es.png" srcset="https://flagcdn.com/w80/es.png 2x" width="28" height="19" alt="Spain" style="display:inline-block;vertical-align:-3px;border-radius:2px;margin-right:6px;">
      <strong style="color:#fff;">Spain are world champions.</strong> They beat Argentina 1&ndash;0 after extra time at MetLife Stadium on July 19, 2026. England beat France 6&ndash;4 for third place. The first 48-team World Cup was played across the United States, Mexico and Canada: 104 matches in 16 cities.
    </p>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:0 0 24px;">
      <a href="/articles/world-cup-final-2026-spain-argentina.html" style="display:block;background:#0a2413;border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:16px;color:#fff;text-decoration:none;font-family:'Oswald',sans-serif;letter-spacing:.03em;">The final: Spain 1&ndash;0 Argentina &rarr;</a>
      <a href="/scoreboard.html" style="display:block;background:#0a2413;border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:16px;color:#fff;text-decoration:none;font-family:'Oswald',sans-serif;letter-spacing:.03em;">Every result: scoreboard &rarr;</a>
      <a href="/wc2026-matches-calendar.html" style="display:block;background:#0a2413;border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:16px;color:#fff;text-decoration:none;font-family:'Oswald',sans-serif;letter-spacing:.03em;">All 104 matches &rarr;</a>
      <a href="/worldcup-story.html" style="display:block;background:#0a2413;border:1px solid rgba(255,255,255,.1);border-radius:14px;padding:16px;color:#fff;text-decoration:none;font-family:'Oswald',sans-serif;letter-spacing:.03em;">The best, the worst, the unforgettable &rarr;</a>
    </div>
    <a href="/world-cup-2026.html" style="display:inline-block;background:#f5c518;color:#07180e;font-family:'Oswald',sans-serif;font-weight:600;letter-spacing:.08em;text-transform:uppercase;text-decoration:none;border-radius:10px;padding:12px 20px;">Browse the full archive &rarr;</a>
    <p style="font-size:13px;color:rgba(232,242,236,.55);margin:18px 0 0;">The travel guides and offers we ran for the tournament have been retired. GO2CUP is independent and not affiliated with FIFA.</p>
  </div>
</section>

'''
s = cut(s, "<!-- ── FAQ ── -->", "<!-- FOOTER -->", ARCHIVE)
for a, b in [
    ('content="GO2CUP, World Cup 2026, Soccer 2026, NFL,', 'content="GO2CUP, SportDGX, Women\'s World Cup 2027, NFL, NBA, soccer,'),
    ('fan-travel publication covering World Cup 2026, host cities, and fan experiences across the USA, Mexico, and Canada.',
     'fan-travel publication covering the NFL, NBA, soccer, the Women\'s World Cup 2027 and the cities fans travel to.'),
    ('<li><a href="/articles/world-cup-final-2026-spain-argentina.html"', '<li><a href="/world-cup-2026.html"'),
    ('>&#127942; CHAMPIONS</a></li>', '>&#127942; WC 2026 ARCHIVE</a></li>'),
    ('The World Cup Final stage — be seen by millions of fans', 'Put your brand in front of fans planning game days'),
]:
    s = s.replace(a, b)
open(P, "w", encoding="utf-8").write(s)
print("index.html updated")
