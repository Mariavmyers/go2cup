#!/usr/bin/env python3
"""Swap every Google Form link on the site for the on-site SportDGX forms (Make webhook).

    python3 _tools/apply_forms.py                       # rewrite links on every page
    python3 _tools/apply_forms.py --hook https://hook.us2.make.com/xxxx   # also set the webhook

Safe to run again: pages already converted are left as they are.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADVERTISE_ID = "1FAIpQLSd3_Nd1UgH81RW4oYpZX6zMwCj9ZWApRaVUzShIc4UISRw2hQ"
SOURCE = {  # old Google Form -> label kept with each sign-up so you can see where it came from
    "1FAIpQLScIKypiZUbbeyil5dGbeyANDTq2Hgj1TjUykwyOfeZLr0qDlw": "newsletter link",
    "1FAIpQLSfJIRLo6dBkPh57cKbVFnU1lz7dgutqzAHO2WsXiT2DDOp43g": "country hopper link",
    "1FAIpQLSehWlmyUk0JrD1vzZaCsZKBRHj13Qy_frczkQmWDQut1o5xlg": "mexico trip guide",
    "1FAIpQLSfeMl6t9m3ggYD-f1k1CT3eBxtSIWPQ4gYjtqhmnbDbxPNTmQ": "streaming page",
    "1FAIpQLSeiVoHx28R79f3_G2lAAByBP23AroECJ8HpFqskUl0VRipiMg": "matches calendar",
    "1FAIpQLScycBIkWw1pwZYREixqO6RgWVNpTRDDEyKROk-x7nInfsQziA": "hot takes",
    "3sus8VcWdGcSYu2E7": "sports news briefing",
}
SCRIPT = '<script src="/assets/sdgx-forms.js" defer></script>'
FORM_URL = r'https?://(?:docs\.google\.com/forms/d/(?:e/)?([A-Za-z0-9_-]+)[^"\']*|forms\.gle/([A-Za-z0-9]+)[^"\']*)'
A_TAG = re.compile(r'<a\b([^>]*?)href=(["\'])' + FORM_URL + r'\2([^>]*)>(.*?)</a>', re.S | re.I)
NEWSLETTER_LABEL = "SportDGX Insider: Weekend Game Plan"


def clean_attrs(a):
    a = re.sub(r'\s*target=(["\'])_blank\1', "", a)
    a = re.sub(r'\s*rel=(["\'])noopener(?: noreferrer)?\1', "", a)
    return a


def convert(m):
    before, q, fid_long, fid_short, after, inner = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6)
    fid = fid_long or fid_short
    if fid_long and "/forms/d/e/" not in m.group(0) and "/forms/d/" in m.group(0):
        return ""  # link to the form EDITOR: never public
    attrs = clean_attrs(before + after).strip()
    attrs = (" " + attrs) if attrs else ""
    if fid == ADVERTISE_ID:
        return '<a href="/advertise.html" data-sdgx-form="advertise"%s>%s</a>' % (attrs, inner)
    label = inner
    if re.sub(r"<[^>]+>", "", inner).strip() in ("Daily 2026 World Cup News", "Country Hopper Newsletter"):
        label = NEWSLETTER_LABEL
    return '<a href="/insider.html#join" data-sdgx-form="newsletter" data-source="%s"%s>%s</a>' % (SOURCE.get(fid, "newsletter link"), attrs, label)


def fix_page(path):
    s = open(path, encoding="utf-8").read()
    orig = s
    s = A_TAG.sub(convert, s)
    # footer sign-up row: keep a single Insider link (the old row had 3 links, 2 of them now the same form)
    def footer(m):
        links = re.findall(r'<a [^>]*>.*?</a>', m.group(2), re.S)
        seen, keep = set(), []
        for a in links:
            k = re.search(r'data-sdgx-form="(\w+)"', a)
            k = k.group(1) if k else a
            if k not in seen:
                seen.add(k)
                keep.append(a)
        return m.group(1) + "\n      " + "\n      ".join(keep) + "\n    " + m.group(3)
    # old "Sponsors & Marketing" boxes had a form that only pretended to send: swap for the real one
    s = re.sub(r'<form class="space-y-2" onsubmit="return false;">.*?</form>',
               '<a href="/advertise.html" data-sdgx-form="advertise" data-source="sponsors box" class="g2c-optin-btn" style="text-decoration:none">Send an inquiry &rarr;</a>',
               s, flags=re.S)
    s = re.sub(r'(<div class="g2c-ft-signups">)(.*?)(</div>)', footer, s, flags=re.S)
    if ("data-sdgx-form" in s or "data-sdgx-inline" in s) and SCRIPT not in s:
        i = s.lower().rfind("</body>")
        s = s[:i] + SCRIPT + "\n" + s[i:] if i != -1 else s + "\n" + SCRIPT + "\n"
    if s != orig:
        open(path, "w", encoding="utf-8").write(s)
        return True
    return False


changed = [p for p in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))
           if "/_" not in p.replace(ROOT, "") and fix_page(p)]
print("pages changed:", len(changed))
left = [p for p in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)
        if re.search(r"docs\.google\.com/forms|forms\.gle", open(p, encoding="utf-8").read())]
print("Google Form links left:", len(left), [os.path.relpath(p, ROOT) for p in left])

if "--hook" in sys.argv:
    hook = sys.argv[sys.argv.index("--hook") + 1]
    assert re.match(r"^https://hook\.[a-z0-9]+\.make\.com/[A-Za-z0-9]+$", hook), "that doesn't look like a Make webhook URL"
    js = os.path.join(ROOT, "assets", "sdgx-forms.js")
    t = open(js, encoding="utf-8").read()
    t = re.sub(r"var HOOK = '[^']*';", "var HOOK = '%s';" % hook, t)
    open(js, "w", encoding="utf-8").write(t)
    print("webhook set")
