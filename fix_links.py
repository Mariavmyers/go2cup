import os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

LINK_MAP = {
    'klook.com':           'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=4110&u=https%3A%2F%2Fklook.com&campaign_id=137',
    'yesim.tech':          'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=5998&u=https%3A%2F%2Fyesim.tech&campaign_id=224',
    'yesim.app':           'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=5998&u=https%3A%2F%2Fyesim.tech&campaign_id=224',
    'kiwitaxi.com':        'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=647&u=https%3A%2F%2Fkiwitaxi.com&campaign_id=1',
    'localrent.com':       'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=2043&u=https%3A%2F%2Flocalrent.com%2Fen&campaign_id=87',
    'welcomepickups.com':  'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=8919&u=https%3A%2F%2Fwelcomepickups.com&campaign_id=627',
    'tiqets.com':          'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=2074&u=https%3A%2F%2Ftiqets.com&campaign_id=89',
    'airalo.com':          'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=8310&u=https%3A%2F%2Fairalo.com&campaign_id=541',
    'gettransfer.com':     'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=4439&u=https%3A%2F%2Fgettransfer.com&campaign_id=147',
    'drimsim.com':         'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=2762&u=https%3A%2F%2Fw1.drimsim.com&campaign_id=102',
    'getrentacar.com':     'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=5996&u=https%3A%2F%2Fgetrentacar.com&campaign_id=222',
    'airhelp.com':         'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=9139&u=https%3A%2F%2Fairhelp.com&campaign_id=120',
    'gocity.com':          'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=1942&u=https%3A%2F%2Fgocity.com&campaign_id=62',
    'ektatraveling.com':   'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=5869&u=https%3A%2F%2Fektatraveling.com&campaign_id=225',
    'economybookings.com': 'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=2018&u=https%3A%2F%2Fwww.economybookings.com&campaign_id=10',
    'bikesbooking.com':    'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=1767&u=https%3A%2F%2Fbikesbooking.com&campaign_id=57',
    'qeeq.com':            'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=4845&u=https%3A%2F%2Fqeeq.com&campaign_id=172',
    'wegotrip.com':        'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=4487&u=https%3A%2F%2Fwegotrip.com&campaign_id=150',
    'autoeurope.eu':       'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=4354&u=https%3A%2F%2Fautoeurope.eu&campaign_id=143',
    'autoeurope.com':      'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=4354&u=https%3A%2F%2Fautoeurope.eu&campaign_id=143',
    'searadar.com':        'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=5907&u=https%3A%2F%2Fsearadar.com&campaign_id=258',
    'radicalstorage.com':  'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=5867&u=https%3A%2F%2Fradicalstorage.com&campaign_id=209',
    'ticketnetwork.com':   'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=1948&u=https%3A%2F%2Fticketnetwork.com&campaign_id=72',
    'aviasales.com':       'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=4114&u=https%3A%2F%2Faviasales.com&campaign_id=100',
    'intui.travel':        'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=657&u=https%3A%2F%2Fintui.travel&campaign_id=22',
    'compensair.com':      'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=4129&u=https%3A%2F%2Fcompensair.com&campaign_id=86',
    'saily.com':           'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=8979&u=https%3A%2F%2Fsaily.com&campaign_id=629',
    'kkday.com':           'https://tp.media/r?marker=736515.worldcup26&trs=536726&p=9074&u=https%3A%2F%2Fkkday.com&campaign_id=633',
}

NEW_CAR_LINKS = '''\n    <a href="https://tp.media/r?marker=736515.worldcup26&trs=536726&p=2043&u=https%3A%2F%2Flocalrent.com%2Fen&campaign_id=87" target="_blank" rel="noopener" class="aff-btn aff-gold">🚗 LocalRent — Local Deals</a>
    <a href="https://tp.media/r?marker=736515.worldcup26&trs=536726&p=1767&u=https%3A%2F%2Fbikesbooking.com&campaign_id=57" target="_blank" rel="noopener" class="aff-btn aff-green">🚲 BikesBooking — Rent a Bike</a>'''

NEW_ACTIVITY_CARDS = '''    <div class="activity-card">
      <div class="activity-icon">🎟</div>
      <div class="activity-name">KKday — Tours &amp; Experiences</div>
      <div class="activity-desc">Asia's top experience platform covering Miami and North America. Day trips, stadium tours, and activity bundles for World Cup fans.</div>
      <a href="https://tp.media/r?marker=736515.worldcup26&trs=536726&p=9074&u=https%3A%2F%2Fkkday.com&campaign_id=633" target="_blank" rel="noopener" class="activity-cta">Browse KKday &#x2192;</a>
    </div>
    <div class="activity-card">
      <div class="activity-icon">✈️</div>
      <div class="activity-name">Ekta Traveling — Curated Trips</div>
      <div class="activity-desc">Curated group travel for sports fans. Multi-city World Cup itineraries and guided packages for international visitors.</div>
      <a href="https://tp.media/r?marker=736515.worldcup26&trs=536726&p=5869&u=https%3A%2F%2Fektatraveling.com&campaign_id=225" target="_blank" rel="noopener" class="activity-cta">Explore Ekta Traveling &#x2192;</a>
    </div>
    <div class="activity-card">
      <div class="activity-icon">⛵</div>
      <div class="activity-name">SeaRadar — Boats &amp; Yachts</div>
      <div class="activity-desc">Rent a boat, jet ski, or yacht in Miami. Explore Biscayne Bay — perfect for group celebrations between World Cup matches.</div>
      <a href="https://tp.media/r?marker=736515.worldcup26&trs=536726&p=5907&u=https%3A%2F%2Fsearadar.com&campaign_id=258" target="_blank" rel="noopener" class="activity-cta">Find a Boat &#x2192;</a>
    </div>
'''

HREF_RE = re.compile(r'(href=["\'])(.*?)(["\'])', re.IGNORECASE)

files_changed = []

for dirpath, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d != '.git']
    for fn in files:
        if not fn.lower().endswith('.html'):
            continue
        path = os.path.join(dirpath, fn)
        try:
            with open(path, encoding='utf-8', errors='replace') as f:
                original = f.read()
        except Exception as e:
            print(f'SKIP {path}: {e}')
            continue

        def replace_href(m):
            q1, url, q2 = m.group(1), m.group(2), m.group(3)
            for domain, turl in LINK_MAP.items():
                if domain in url.lower() and url != turl:
                    return q1 + turl + q2
            return m.group(0)

        txt = HREF_RE.sub(replace_href, original)

        # miami-city.html specific injections
        if 'miami-city' in fn:
            # Inject LocalRent + BikesBooking after last existing car-rental aff-btn, before closing </div></section>
            # Find the GetRentacar button and add after it
            getrentacar_btn = '<a href="https://tp.media/r?marker=736515.worldcup26&trs=536726&p=5996&u=https%3A%2F%2Fgetrentacar.com&campaign_id=222" target="_blank" rel="noopener" class="aff-btn aff-purple">🚗 GetRentacar</a>'
            if getrentacar_btn in txt and 'LocalRent' not in txt:
                txt = txt.replace(getrentacar_btn, getrentacar_btn + NEW_CAR_LINKS, 1)

            # Inject KKday, Ekta, SeaRadar activity cards before the closing of the activity-grid div
            # Look for the closing pattern of the activity section
            if 'KKday' not in txt:
                # Find the last activity-card closing tag before the activity section ends
                activity_section_close = '</div>\n</section>\n\n<!-- ===== INSURANCE'
                if activity_section_close in txt:
                    txt = txt.replace(
                        activity_section_close,
                        NEW_ACTIVITY_CARDS + '</div>\n</section>\n\n<!-- ===== INSURANCE',
                        1
                    )
                else:
                    # Try alternate whitespace
                    activity_section_close2 = '</div>\r\n</section>\r\n\r\n<!-- ===== INSURANCE'
                    if activity_section_close2 in txt:
                        txt = txt.replace(
                            activity_section_close2,
                            NEW_ACTIVITY_CARDS + '</div>\r\n</section>\r\n\r\n<!-- ===== INSURANCE',
                            1
                        )
                    else:
                        print(f'WARNING: Could not find activity section close in {path}')

        if txt != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(txt)
            files_changed.append(os.path.relpath(path, '.'))

print(f'\nFiles updated: {len(files_changed)}')
for fp in sorted(files_changed):
    print(f'  {fp}')
