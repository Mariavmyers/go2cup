#!/usr/bin/env python3
"""Generate nfl.html as static, crawlable HTML from the NFL data files.

Run locally, then commit the emitted nfl.html (same pattern as assets/tw.css,
see _architecture/DATA-PUBLISHING-POLICY.md section 3.3):

    python3 _tools/build_nfl.py

Inputs:  data/nfl-teams.json, data/nfl-2026-games.json, data/nfl-sources.json
Output:  nfl.html
All primary content is written into the HTML. JavaScript only switches tabs,
switches the visible week, and filters the team list.
"""
import json
import os
from datetime import datetime
from html import escape
from urllib.parse import quote
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ET = ZoneInfo("America/New_York")
CONF_COLOR = {"AFC": "#ff4338", "NFC": "#2f80ff"}  # site brand colors, not league marks
DIVISIONS = [c + " " + d for c in ("AFC", "NFC") for d in ("East", "North", "South", "West")]


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


TEAMS = load("nfl-teams.json")
GAMES_DOC = load("nfl-2026-games.json")
SOURCES = load("nfl-sources.json")
T = {t["abbr"]: t for t in TEAMS["teams"]}
G = sorted(GAMES_DOC["games"], key=lambda g: g["date"])
FINALS = [g for g in G if g["status"] == "final"]


def e(s):
    return escape(str(s if s is not None else ""), quote=True)


def et(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(ET)


def day_label(iso):
    d = et(iso)
    return d.strftime("%A, %B ") + str(d.day)


def short_date(iso):
    d = et(iso)
    return d.strftime("%b ") + str(d.day)


def time_label(iso):
    d = et(iso)
    h = d.hour % 12 or 12
    return "%d:%02d %s ET" % (h, d.minute, "PM" if d.hour >= 12 else "AM")


def is_ot(g):
    return "OT" in (g.get("detail") or "")


def abroad(g):
    return bool(g.get("country")) and g["country"] != "USA"


def badge(a, size=""):
    conf = T[a]["conference"]
    return '<span class="badge%s" style="--c:%s" aria-hidden="true">%s</span>' % (
        " " + size if size else "", CONF_COLOR[conf], e(a))


# ---------------------------------------------------------------- records
def blank():
    return dict(w=0, l=0, t=0, pf=0, pa=0, dw=0, dl=0, dt=0, cw=0, cl=0, ct=0, res=[])


R = {a: blank() for a in T}
for g in FINALS:
    A, H = R[g["away"]], R[g["home"]]
    A["pf"] += g["awayScore"]; A["pa"] += g["homeScore"]
    H["pf"] += g["homeScore"]; H["pa"] += g["awayScore"]
    same_div = T[g["away"]]["division"] == T[g["home"]]["division"]
    same_conf = T[g["away"]]["conference"] == T[g["home"]]["conference"]
    if g["awayScore"] == g["homeScore"]:
        res = ("T", "T")
    elif g["awayScore"] > g["homeScore"]:
        res = ("W", "L")
    else:
        res = ("L", "W")
    for rec, r in ((A, res[0]), (H, res[1])):
        key = {"W": "w", "L": "l", "T": "t"}[r]
        rec[key] += 1
        rec["res"].append(r)
        if same_div:
            rec["d" + key] += 1
        if same_conf:
            rec["c" + key] += 1


def pct(w, l, t):
    n = w + l + t
    return (w + t / 2) / n if n else 0.0


for a, x in R.items():
    x["pct"] = pct(x["w"], x["l"], x["t"])
    x["dpct"] = pct(x["dw"], x["dl"], x["dt"])
    x["cpct"] = pct(x["cw"], x["cl"], x["ct"])
    x["diff"] = x["pf"] - x["pa"]
    last, n = (x["res"][-1] if x["res"] else ""), 0
    for r in reversed(x["res"]):
        if r != last:
            break
        n += 1
    x["streak"] = (last + str(n)) if last else ""
    x["rec"] = "%d–%d%s" % (x["w"], x["l"], ("–%d" % x["t"]) if x["t"] else "")


def h2h_pct(team, group):
    w = l = t = 0
    for g in FINALS:
        if team not in (g["away"], g["home"]):
            continue
        opp = g["home"] if g["away"] == team else g["away"]
        if opp not in group:
            continue
        us = g["awayScore"] if g["away"] == team else g["homeScore"]
        them = g["homeScore"] if g["away"] == team else g["awayScore"]
        if us > them: w += 1
        elif us < them: l += 1
        else: t += 1
    return pct(w, l, t)


def rank_division(abbrs):
    """Win pct, then (for tied teams) head-to-head among the tied group,
    division record, conference record, point differential. A simplified
    form of the league's division tiebreak steps."""
    by_pct = {}
    for a in abbrs:
        by_pct.setdefault(round(R[a]["pct"], 6), []).append(a)
    out = []
    for p in sorted(by_pct, reverse=True):
        group = by_pct[p]
        if len(group) > 1:
            group = sorted(group, key=lambda a: (h2h_pct(a, set(group) - {a}) if len(group) > 1 else 0,
                                                 R[a]["dpct"], R[a]["cpct"], R[a]["diff"]), reverse=True)
        out.extend(group)
    return out


# ---------------------------------------------------------------- sections
weeks = sorted({g["week"] for g in G})
complete_weeks = [w for w in weeks if all(x["status"] == "final" for x in G if x["week"] == w)]
last_complete = max(complete_weeks)
latest_with_finals = max(g["week"] for g in FINALS)
current_week = latest_with_finals
updated_label = datetime.fromisoformat(GAMES_DOC["updated"]).strftime("%B ") + str(int(GAMES_DOC["updated"][8:10])) + ", " + GAMES_DOC["updated"][:4]


def team_name(a):
    return T[a]["fullName"]


def result_line(g):
    w, l = (g["away"], g["home"]) if g["awayScore"] >= g["homeScore"] else (g["home"], g["away"])
    ws, ls = max(g["awayScore"], g["homeScore"]), min(g["awayScore"], g["homeScore"])
    return "%s %d, %s %d%s" % (team_name(w), ws, team_name(l), ls, " (OT)" if is_ot(g) else "")


def hero():
    kc = [g for g in FINALS if "KC" in (g["home"], g["away"])][-1]
    aw, hw = kc["awayScore"] > kc["homeScore"], kc["homeScore"] > kc["awayScore"]
    feature = (
        '<div class="side">%s<div class="tm">%s<small>%s</small></div></div>'
        '<div class="score"><span class="%s">%d</span>–<span class="%s">%d</span></div>'
        '<div class="side r">%s<div class="tm">%s<small>%s</small></div></div>'
        '<div class="cap">Chiefs latest: Week %d · %s · %s, %s%s</div>'
    ) % (badge(kc["away"], "lg"), e(team_name(kc["away"])), R[kc["away"]]["rec"],
         "lose" if hw else "", kc["awayScore"], "lose" if aw else "", kc["homeScore"],
         badge(kc["home"], "lg"), e(team_name(kc["home"])), R[kc["home"]]["rec"],
         kc["week"], day_label(kc["date"]), e(kc["venue"]), e(kc["city"]), " · Overtime" if is_ot(kc) else "")
    pts = sum(g["awayScore"] + g["homeScore"] for g in FINALS)
    stats = "".join('<div><b>%s</b>%s</div>' % (v, k) for v, k in [
        (len(complete_weeks), "weeks complete"), (len(FINALS), "games final"),
        ("%.1f" % (pts / len(FINALS)), "points per game"),
        (sum(1 for g in FINALS if is_ot(g)), "overtime games"),
        (sum(1 for g in FINALS if abroad(g)), "games abroad")])
    return feature, stats


def game_card(g):
    fin = g["status"] == "final"
    aw = fin and g["awayScore"] > g["homeScore"]
    hw = fin and g["homeScore"] > g["awayScore"]
    tags = ""
    if fin and is_ot(g):
        tags += ' <span class="tag ot">OT</span>'
    if fin and g["awayScore"] == g["homeScore"]:
        tags += ' <span class="tag tie">Tie</span>'
    if abroad(g):
        tags += ' <span class="tag intl">%s</span>' % e(g["city"])

    def row(a, score, lost):
        return ('<div class="trow%s">%s<span class="nm">%s<small>%s</small></span><span class="pts">%s</span></div>'
                % (" lost" if lost else "", badge(a, "sm"), e(team_name(a)), R[a]["rec"], score if fin else ""))

    label = "Final" if fin else time_label(g["date"])
    right = e(g["venue"]) + ((" · " + e(g["broadcast"])) if (g.get("broadcast") and not fin) else "")
    return ('<article class="game" aria-label="%s at %s">%s%s<div class="gmeta"><span>%s%s</span><span>%s</span></div></article>'
            % (e(team_name(g["away"])), e(team_name(g["home"])), row(g["away"], g["awayScore"], fin and hw),
               row(g["home"], g["homeScore"], fin and aw), label, tags, right))


def scores():
    buttons, sections = [], []
    for w in weeks:
        wg = [g for g in G if g["week"] == w]
        nf = sum(1 for g in wg if g["status"] == "final")
        lbl = "" if nf == len(wg) else (" · in progress" if nf else " · upcoming")
        buttons.append('<button class="wk%s" data-w="%d" aria-pressed="%s">Week %d%s</button>'
                       % ("" if nf == len(wg) else " up", w, "true" if w == current_week else "false", w, lbl))
        html, day = [], None
        for g in wg:
            d = day_label(g["date"])
            if d != day:
                if day:
                    html.append("</div>")
                html.append('<h4 class="daylbl">%s</h4><div class="grid">' % d)
                day = d
            html.append(game_card(g))
        html.append("</div>")
        sections.append('<section class="week" id="week-%d" data-w="%d" aria-labelledby="wk%dh"><h3 class="wkh" id="wk%dh">Week %d</h3>%s</section>'
                        % (w, w, w, w, w, "".join(html)))
    return "".join(buttons), "".join(sections)


def standings():
    out = []
    for conf in ("AFC", "NFC"):
        out.append('<h3 class="daylbl">%s</h3><div class="conf">' % conf)
        for dn in DIVISIONS:
            if not dn.startswith(conf):
                continue
            order = rank_division([a for a in T if T[a]["division"] == dn])
            rows = []
            for i, a in enumerate(order):
                x = R[a]
                rows.append('<tr%s><td><span class="tcell">%s%s</span></td><td>%d–%d–%d</td><td>%s</td><td>%d–%d%s</td><td>%s%d</td><td class="streak %s">%s</td></tr>'
                            % (' class="leader"' if i == 0 else "", badge(a, "sm"), e(T[a]["name"]), x["w"], x["l"], x["t"],
                               ("%.3f" % x["pct"]).lstrip("0") if x["pct"] < 1 else "1.000",
                               x["dw"], x["dl"], ("–%d" % x["dt"]) if x["dt"] else "",
                               "+" if x["diff"] > 0 else "", x["diff"], x["streak"][:1], x["streak"]))
            out.append('<div class="div"><h4>%s</h4><table><thead><tr><th scope="col">Team</th><th scope="col">W–L–T</th><th scope="col">Pct</th><th scope="col">Div</th><th scope="col">Diff</th><th scope="col">Streak</th></tr></thead><tbody>%s</tbody></table></div>'
                       % (dn, "".join(rows)))
        out.append("</div>")
    return "".join(out)


def teams():
    cards = []
    for t in sorted(T.values(), key=lambda t: (DIVISIONS.index(t["division"]), t["fullName"])):
        x = R[t["abbr"]]
        hotel = "https://www.stay22.com/allez/roam?aid=1607597&address=" + quote(t["stadium"] + ", " + t["city"] + ", " + t["state"], safe="")
        search = " ".join([t["fullName"], t["city"], t["state"], t["stadium"], t["abbr"]]).lower()
        links = ('<a class="btn" href="%s">City guide</a>' % e(t["hostCity"])) if t.get("hostCity") else ""
        links += '<a class="btn" href="%s" target="_blank" rel="sponsored noopener">Hotels near the stadium</a>' % e(hotel)
        cards.append(
            '<article class="team" data-div="%s" data-q="%s"><div class="top">%s<div><h4>%s</h4><p>%s</p></div></div>'
            '<div class="body"><div class="rec">%s</div><dl><dt>Home stadium</dt><dd>%s</dd><dt>City</dt><dd>%s, %s</dd>'
            '<dt>Points for / against</dt><dd>%d / %d</dd></dl></div><div class="links">%s</div></article>'
            % (e(t["division"]), e(search), badge(t["abbr"]), e(t["fullName"]), e(t["division"]), x["rec"],
               e(t["stadium"]), e(t["city"]), e(t["state"]), x["pf"], x["pa"], links))
    options = "".join("<option>%s</option>" % d for d in DIVISIONS)
    return options, "".join(cards)


def news():
    lw = [g for g in FINALS if g["week"] == last_complete]
    big = max(lw, key=lambda g: abs(g["awayScore"] - g["homeScore"]))
    close = [g for g in lw if abs(g["awayScore"] - g["homeScore"]) <= 3]
    ranked = sorted(T, key=lambda a: (R[a]["pct"], R[a]["diff"]), reverse=True)
    top = ranked[:4]
    winless = [a for a in T if R[a]["w"] == 0 and (R[a]["l"] + R[a]["t"]) > 0]
    kc = [g for g in FINALS if "KC" in (g["home"], g["away"])]
    intl = [g for g in FINALS if abroad(g)]
    high = max(FINALS, key=lambda g: g["awayScore"] + g["homeScore"])
    s = []
    s.append('<article class="story"><p class="when">Week %d recap · %s</p><h3>%s</h3><p>The most lopsided result of Week %d. %d of the week\'s %d games were decided by three points or fewer.</p></article>'
             % (last_complete, short_date(lw[-1]["date"]), e(result_line(big)), last_complete, len(close), len(lw)))
    if current_week > last_complete:
        cw = [g for g in G if g["week"] == current_week]
        left = [g for g in cw if g["status"] != "final"]
        s.append('<article class="story"><p class="when">Week %d so far</p><h3>%d of %d games are final</h3><p>Still to play: %s.</p></article>'
                 % (current_week, len(cw) - len(left), len(cw),
                    "; ".join("%s at %s, %s" % (e(T[g["away"]]["name"]), e(T[g["home"]]["name"]), day_label(g["date"])) for g in left)))
    s.append('<article class="story"><p class="when">Through %d games</p><h3>Best records in the league</h3><ul>%s</ul></article>'
             % (len(FINALS), "".join("<li>%s — %s</li>" % (e(team_name(a)), R[a]["rec"]) for a in top)))
    items = []
    for g in kc:
        home = g["home"] == "KC"
        opp = g["away"] if home else g["home"]
        us, them = (g["homeScore"], g["awayScore"]) if home else (g["awayScore"], g["homeScore"])
        items.append("<li>Week %d: %s %d–%d %s %s%s</li>" % (g["week"], "W" if us > them else "L" if us < them else "T", us, them,
                                                          "vs" if home else "at", e(T[opp]["name"]), " (OT)" if is_ot(g) else ""))
    s.append('<article class="story"><p class="when">Kansas City</p><h3>Chiefs are %s</h3><ul>%s</ul></article>' % (R["KC"]["rec"], "".join(items)))
    s.append('<article class="story"><p class="when">Global games</p><h3>%d games played outside the U.S.</h3><ul>%s</ul></article>'
             % (len(intl), "".join("<li>%s, %s: %s</li>" % (e(g["city"]), e(g["country"]), e(result_line(g))) for g in intl)))
    s.append('<article class="story"><p class="when">Highest-scoring game</p><h3>%s</h3><p>%d combined points in Week %d at %s.</p></article>'
             % (e(result_line(high)), high["awayScore"] + high["homeScore"], high["week"], e(high["venue"])))
    if winless:
        s.append('<article class="story"><p class="when">Still searching</p><h3>%s without a win</h3><p>%s.</p></article>'
                 % ("One team" if len(winless) == 1 else "%d teams" % len(winless),
                    ", ".join("%s (%s)" % (e(team_name(a)), R[a]["rec"]) for a in winless)))
    return "".join(s)


def sources_note():
    parts = []
    for src in SOURCES["sources"]:
        parts.append('%s (accessed %s)' % (e(src["publisher"]), src["accessedAt"][:10]))
    return "Scores compiled from " + "; ".join(parts) + ". Weeks 1–5 cross-checked between both sources."


# ---------------------------------------------------------------- page
feature, stat_html = hero()
week_buttons, week_sections = scores()
div_options, team_cards = teams()
css = open(os.path.join(ROOT, "_tools", "nfl.css.html"), encoding="utf-8").read()

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
<!-- pageStatus: draft. Keep noindex until licensing for the score data is resolved (DATA-PUBLISHING-POLICY.md 2.3, 4.2). -->
<meta name="robots" content="noindex">
<title>NFL 2026 Season — Scores, Standings & All 32 Teams | GO2CUP</title>
<meta name="description" content="Every 2026 NFL score since the September 9 kickoff, standings for all eight divisions, and a guide to all 32 teams, their cities and stadiums.">
<link rel="canonical" href="https://sportdgx.com/nfl">
<meta property="og:type" content="website">
<meta property="og:site_name" content="GO2CUP">
<meta property="og:title" content="NFL 2026 Season — Scores, Standings & All 32 Teams">
<meta property="og:description" content="Every 2026 NFL result week by week, division standings, and a city-by-city guide to all 32 teams.">
<meta property="og:url" content="https://sportdgx.com/nfl">
<meta property="og:image" content="https://sportdgx.com/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<!-- Generated by _tools/build_nfl.py from data/nfl-*.json. Edit the data or the generator, not this file. -->
__CSS__
</head>
<body>

<header>
  <nav class="nav">
    <a href="/" class="logo"><span class="b">GO</span><span class="w">2</span><span class="r">CUP</span></a>
    <div class="menu">
      <a href="/">Home</a>
      <a href="nfl.html" class="active">NFL 2026</a>
      <a href="scoreboard.html">World Cup Scoreboard</a>
      <a href="where-to-stay.html">Where to Stay</a>
      <a href="sports-news.html">News</a>
    </div>
  </nav>
</header>

<section class="hero" aria-labelledby="hero-title">
  <div class="wrap">
    <h1 id="hero-title">NFL 2026 season</h1>
    <p class="lede">Every score since the September 9 kickoff, the race in all eight divisions, and a city guide to all 32 teams.</p>
    <div class="feature">__FEATURE__</div>
    <div class="stats">__STATS__</div>
  </div>
</section>

<div class="tabs" role="tablist" aria-label="NFL 2026 sections">
  <div class="wrap">
    <a class="tab" role="tab" href="#scores" id="t-scores" aria-controls="p-scores" aria-selected="true">Scores</a>
    <a class="tab" role="tab" href="#standings" id="t-standings" aria-controls="p-standings" aria-selected="false">Standings</a>
    <a class="tab" role="tab" href="#teams" id="t-teams" aria-controls="p-teams" aria-selected="false">Teams &amp; cities</a>
    <a class="tab" role="tab" href="#news" id="t-news" aria-controls="p-news" aria-selected="false">News</a>
    <a class="tab" role="tab" href="#store" id="t-store" aria-controls="p-store" aria-selected="false">Store</a>
  </div>
</div>

<main class="wrap">

  <section class="panel" id="p-scores" role="tabpanel" aria-labelledby="t-scores">
    <h2 id="scores">Scores by week</h2>
    <p class="sub">Final scores, all times Eastern. Pick a week to see every game.</p>
    <div class="weeks" aria-label="Choose a week">__WEEKBUTTONS__</div>
    <div id="games">__WEEKS__</div>
  </section>

  <section class="panel" id="p-standings" role="tabpanel" aria-labelledby="t-standings">
    <h2 id="standings">Standings</h2>
    <p class="sub">Win–loss–tie records by division, worked out from every final score on this page. Ties count as half a win. Teams level on record are separated by head-to-head results, then division record, conference record and point differential (a simplified version of the league's tiebreak steps).</p>
    __STANDINGS__
  </section>

  <section class="panel" id="p-teams" role="tabpanel" aria-labelledby="t-teams">
    <h2 id="teams">All 32 teams</h2>
    <p class="sub">Where every team plays, its record so far, and travel guides for the cities that also hosted the World Cup.</p>
    <div class="filters">
      <label for="tsearch" class="vh">Search teams</label>
      <input id="tsearch" type="search" placeholder="Search a team or city">
      <label for="tdiv" class="vh">Filter by division</label>
      <select id="tdiv"><option value="">All divisions</option>__DIVOPTIONS__</select>
    </div>
    <div class="tgrid" id="team-list">__TEAMS__</div>
    <p class="loading" id="no-team" hidden>No team matches that search. Try a city name, like Kansas City.</p>
  </section>

  <section class="panel" id="p-news" role="tabpanel" aria-labelledby="t-news">
    <h2 id="news">News &amp; storylines</h2>
    <p class="sub">What the scores say so far this season. Updated each week.</p>
    <div class="news">__NEWS__</div>
    <p class="note">More sports coverage on our <a href="sports-news.html" style="text-decoration:underline">news page</a>.</p>
  </section>

  <section class="panel" id="p-store" role="tabpanel" aria-labelledby="t-store">
    <div class="store">
      <h2 id="store">The GO2CUP store is coming</h2>
      <p>Fan gear, game-day essentials and travel extras for NFL road trips. Join the list and we'll tell you the day it opens.</p>
      <a class="btn solid" href="https://mainentry.net/world-cup-2026-news">Tell me when it opens</a>
    </div>
  </section>

  <p class="note">Scores updated __UPDATED__. __SOURCES__</p>
</main>

<footer>
  <div class="wrap">
    GO2CUP is an independent fan and travel guide by MainEntry LLC. We are not affiliated with, endorsed by or sponsored by the NFL or any of its teams, venues or ticket sellers. Team names are used only to identify the teams.<br>
    GO2CUP may earn a commission from affiliate links. See our <a href="disclosure.html">disclosure</a> · <a href="privacy.html">Privacy</a> · <a href="terms.html">Terms</a> · <a href="/">Home</a>
  </div>
</footer>

<script>
(function(){
  // Progressive enhancement only: every score, standing and team is already in the HTML above.
  document.documentElement.classList.add('js');
  var tabs = [].slice.call(document.querySelectorAll('.tab'));
  function show(tab, push){
    tabs.forEach(function(t){
      var on = t === tab;
      t.setAttribute('aria-selected', on); t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
    });
    if (push) { try { history.replaceState(null, '', tab.getAttribute('href')); } catch(e){} }
  }
  tabs.forEach(function(t, i){
    t.addEventListener('click', function(ev){ ev.preventDefault(); show(t, true); });
    t.addEventListener('keydown', function(ev){
      var j = ev.key === 'ArrowRight' ? i + 1 : ev.key === 'ArrowLeft' ? i - 1 : null;
      if (j === null) return; ev.preventDefault(); j = (j + tabs.length) % tabs.length; tabs[j].focus(); show(tabs[j], true);
    });
  });
  show(document.getElementById('t-' + location.hash.slice(1)) || tabs[0], false);

  var btns = [].slice.call(document.querySelectorAll('.wk')), weeks = [].slice.call(document.querySelectorAll('.week'));
  function pick(w){
    btns.forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.w === w); });
    weeks.forEach(function(s){ s.hidden = s.dataset.w !== w; });
  }
  btns.forEach(function(b){ b.addEventListener('click', function(){ pick(b.dataset.w); }); });
  var start = btns.filter(function(b){ return b.getAttribute('aria-pressed') === 'true'; })[0];
  if (start) pick(start.dataset.w);

  var q = document.getElementById('tsearch'), dv = document.getElementById('tdiv'), cards = [].slice.call(document.querySelectorAll('.team'));
  function filter(){
    var s = q.value.trim().toLowerCase(), d = dv.value, n = 0;
    cards.forEach(function(c){ var ok = (!d || c.dataset.div === d) && (!s || c.dataset.q.indexOf(s) >= 0); c.hidden = !ok; if (ok) n++; });
    document.getElementById('no-team').hidden = n > 0;
  }
  q.addEventListener('input', filter); dv.addEventListener('change', filter);
})();
</script>
</body>
</html>
"""

for k, v in {
    "__CSS__": css, "__FEATURE__": feature, "__STATS__": stat_html, "__WEEKBUTTONS__": week_buttons,
    "__WEEKS__": week_sections, "__STANDINGS__": standings(), "__DIVOPTIONS__": div_options,
    "__TEAMS__": team_cards, "__NEWS__": news(), "__UPDATED__": updated_label, "__SOURCES__": sources_note(),
}.items():
    page = page.replace(k, v)

with open(os.path.join(ROOT, "nfl.html"), "w", encoding="utf-8") as f:
    f.write(page)
print("wrote nfl.html: %d games, %d final, weeks complete %s, current week %d" % (len(G), len(FINALS), complete_weeks, current_week))
