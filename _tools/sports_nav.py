"""Shared sport switcher used by every sport hub page (and the homepage tabs)."""
from html import escape

SPORTS = [
    # slug/page, label, accent color, dark background
    ("nfl.html", "NFL", "#21c25a", "#07180e"),
    ("nba.html", "NBA", "#ff7a1a", "#0b1020"),
    ("soccer.html", "Soccer", "#2fe0c8", "#041618"),
    ("ufc.html", "UFC", "#ff3b3b", "#120708"),
    ("boxing.html", "Boxing", "#f5b041", "#150b05"),
    ("tennis.html", "Tennis", "#d7f53a", "#0d0b22"),
    ("racing.html", "F1", "#ffb020", "#0a0d12"),
]

SWITCH_CSS = """
.sportbar{border-bottom:1px solid rgba(255,255,255,.08);background:rgba(0,0,0,.25)}
.sportbar .in{max-width:1100px;margin:0 auto;padding:0 18px;display:flex;gap:6px;overflow-x:auto;scrollbar-width:none}
.sportbar .in::-webkit-scrollbar{display:none}
.sportbar a{flex:none;display:flex;align-items:center;gap:7px;padding:11px 12px 9px;font-family:'Oswald',sans-serif;font-size:14px;letter-spacing:.6px;text-transform:uppercase;color:#b9c7c0;text-decoration:none;border-bottom:3px solid transparent}
.sportbar a i{width:9px;height:9px;border-radius:50%;background:var(--sc);box-shadow:0 0 10px var(--sc)}
.sportbar a:hover{color:#fff}
.sportbar a[aria-current=page]{color:#fff;border-bottom-color:var(--sc)}
"""


def sport_bar(current_page):
    links = []
    for page, label, color, _bg in SPORTS:
        cur = ' aria-current="page"' if page == current_page else ""
        links.append('<a href="/%s" style="--sc:%s"%s><i></i>%s</a>' % (page, color, cur, escape(label)))
    return '<nav class="sportbar" aria-label="Sports"><div class="in">%s</div></nav>' % "".join(links)
