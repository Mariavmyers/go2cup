#!/usr/bin/env python3
"""Swap every Google Form link on the site for the on-site SportDGX forms (Make webhook).

    python3 _tools/apply_forms.py                         # convert links on every page
    python3 _tools/apply_forms.py --hook https://hook.us2.make.com/xxxx   # also set the webhook

Each old Google Form keeps its original purpose:
  newsletter -> SportDGX Insider sign-up (explicit consent box)
  guide      -> guide request (newsletter only if the person ticks the optional box)
  inquiry    -> Sponsors & Marketing inquiry (never subscribes anyone)
Links that opened a Google Form EDITOR are removed.

Safe to run again: pages already converted are left as they are.
"""
import glob
import os
import re
import sys
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from form_markup import static_form  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_TOKEN = "__SDGX_FORMS_HOOK__"

# old Google Form id -> (kind, guide name, source label). Purposes checked against each live form on 2026-10-23.
FORMS = {
    "1FAIpQLSd3_Nd1UgH81RW4oYpZX6zMwCj9ZWApRaVUzShIc4UISRw2hQ": ("inquiry", "", "sponsors & marketing link"),  # "Sponsors & Marketing Inquiry"
    "1FAIpQLScIKypiZUbbeyil5dGbeyANDTq2Hgj1TjUykwyOfeZLr0qDlw": ("newsletter", "", "newsletter link"),         # "Sports DGX - Super Blog" updates sign-up
    "1FAIpQLSfJIRLo6dBkPh57cKbVFnU1lz7dgutqzAHO2WsXiT2DDOp43g": ("guide", "Country Hopper Guide", "country hopper link"),  # "GO2CUP Fan Country Hopper Guide"
    "1FAIpQLSehWlmyUk0JrD1vzZaCsZKBRHj13Qy_frczkQmWDQut1o5xlg": ("guide", "Mexico Trip Guide", "mexico trip guide"),     # form deleted; page asks for a personalized guide
    "1FAIpQLSfeMl6t9m3ggYD-f1k1CT3eBxtSIWPQ4gYjtqhmnbDbxPNTmQ": ("newsletter", "", "streaming page"),          # button promises daily updates by email
    "1FAIpQLSeiVoHx28R79f3_G2lAAByBP23AroECJ8HpFqskUl0VRipiMg": ("newsletter", "", "matches calendar"),        # form deleted; "Get the highlights & my hot takes"
    "1FAIpQLScycBIkWw1pwZYREixqO6RgWVNpTRDDEyKROk-x7nInfsQziA": ("newsletter", "", "hot takes"),               # form deleted; "Sign Up Free"
    "3sus8VcWdGcSYu2E7": ("newsletter", "", "sports news briefing"),                                          # "GO2CUP Sports News Briefing Subscription"
}
FALLBACK = {  # where each link goes without JavaScript (each has a plain HTML form)
    "newsletter": "/insider.html#join",
    "inquiry": "/advertise.html#inquiry",
    "Country Hopper Guide": "/hopper-guide.html#get-guide",
    "Mexico Trip Guide": "/mexico-trip-guide.html#get-guide",
}
# pages that get the in-page guide form, replacing the named button
GUIDE_PAGES = {}  # World Cup 2026 guide offers were retired on 2026-10-23 (see _tools/wc2026_archive.py)
SCRIPT = '<script src="/assets/sdgx-forms.js" defer></script>'
FORM_URL = r'https?://(?:docs\.google\.com/forms/d/(?:e/)?([A-Za-z0-9_-]+)[^"\']*|forms\.gle/([A-Za-z0-9]+)[^"\']*)'
A_TAG = re.compile(r'<a\b([^>]*?)href=(["\'])' + FORM_URL + r'\2([^>]*)>(.*?)</a>', re.S | re.I)
NEWSLETTER_LABEL = "SportDGX Insider: Weekend Game Plan"


def clean_attrs(a):
    a = re.sub(r'\s*target=(["\'])_blank\1', "", a)
    a = re.sub(r'\s*rel=(["\'])noopener(?: noreferrer)?\1', "", a)
    return a


def convert(m):
    before, fid_long, fid_short, after, inner = m.group(1), m.group(3), m.group(4), m.group(5), m.group(6)
    fid = fid_long or fid_short
    if "/forms/d/e/" not in m.group(0) and "/forms/d/" in m.group(0):
        return ""  # link to a Google Form EDITOR: never public
    kind, guide, source = FORMS.get(fid, ("newsletter", "", "newsletter link"))
    text = " ".join(re.sub(r"<[^>]+>", " ", inner).split())
    if kind == "guide" and guide == "Country Hopper Guide" and not re.search(r"guide", text, re.I):
        kind, guide = "newsletter", ""  # "Country Hopper Newsletter", "host-city alert": newsletter links
    if text in ("Daily 2026 World Cup News", "Country Hopper Newsletter"):
        inner = NEWSLETTER_LABEL
    attrs = clean_attrs(before + after).strip()
    attrs = (" " + attrs) if attrs else ""
    href = FALLBACK[guide] if kind == "guide" else FALLBACK[kind]
    extra = ' data-guide="%s"' % escape(guide) if guide else ""
    return '<a href="%s" data-sdgx-form="%s"%s data-source="%s"%s>%s</a>' % (href, kind, extra, escape(source), attrs, inner)


def add_guide_form(path, s):
    name = os.path.basename(path)
    if name not in GUIDE_PAGES or 'data-sdgx-inline="guide"' in s:
        return s
    guide, label = GUIDE_PAGES[name]
    # replace the page's main guide button with the in-page form
    pat = re.compile(r'<a href="[^"]*" data-sdgx-form="guide"[^>]*>[^<]*' + re.escape(label) + r'[^<]*</a>')
    m = pat.search(s)
    assert m, "guide button not found on " + name
    box_id = "get-guide-form" if 'id="get-guide"' in s else "get-guide"
    box = ('<div id="%s" class="sdgx-inline-box" data-sdgx-inline="guide" data-guide="%s" data-source="%s page" style="max-width:560px;margin:18px auto;text-align:left">%s</div>'
           % (box_id, escape(guide), escape(name[:-5]), static_form("guide", guide, name[:-5] + " page", HOOK_TOKEN)))
    return s[:m.start()] + box + s[m.end():]


def fix_page(path):
    s = open(path, encoding="utf-8").read()
    orig = s
    s = A_TAG.sub(convert, s)
    s = add_guide_form(path, s)

    def footer(m):  # footer sign-up row: one link per form (the old row had 3 links, 2 now the same form)
        links = re.findall(r'<a [^>]*>.*?</a>', m.group(2), re.S)
        seen, keep = set(), []
        for a in links:
            k = re.search(r'data-sdgx-form="(\w+)"', a)
            k = k.group(1) if k else a
            if k not in seen:
                seen.add(k)
                keep.append(a)
        return m.group(1) + "\n      " + "\n      ".join(keep) + "\n    " + m.group(3)
    s = re.sub(r'(<div class="g2c-ft-signups">)(.*?)(</div>)', footer, s, flags=re.S)
    if ("data-sdgx-form" in s or "data-sdgx-inline" in s) and SCRIPT not in s:
        i = s.lower().rfind("</body>")
        s = s[:i] + SCRIPT + "\n" + s[i:] if i != -1 else s + "\n" + SCRIPT + "\n"
    if s != orig:
        open(path, "w", encoding="utf-8").write(s)
        return True
    return False


def set_hook(hook):
    assert re.match(r"^https://hook\.[a-z0-9]+\.make\.com/[A-Za-z0-9]+$", hook), "that doesn't look like a Make webhook URL"
    js = os.path.join(ROOT, "assets", "sdgx-forms.js")
    t = open(js, encoding="utf-8").read()
    open(js, "w", encoding="utf-8").write(re.sub(r"var HOOK = '[^']*';", "var HOOK = '%s';" % hook, t))
    n = 0
    for p in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        s = open(p, encoding="utf-8").read()
        s2 = re.sub(r'(<form class="sdgx-f sdgx-static"[^>]* action=")[^"]*(")', lambda m: m.group(1) + hook + m.group(2), s)
        if s2 != s:
            open(p, "w", encoding="utf-8").write(s2)
            n += 1
    print("webhook set in script and %d page(s) with plain HTML forms" % n)


if __name__ == "__main__":
    pages = [p for p in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)) if "/_" not in p.replace(ROOT, "")]
    changed = [p for p in pages if fix_page(p)]
    print("pages changed:", len(changed))
    left = [os.path.relpath(p, ROOT) for p in pages if re.search(r"docs\.google\.com/forms|forms\.gle", open(p, encoding="utf-8").read())]
    print("Google Form links left:", len(left), left)
    if "--hook" in sys.argv:
        set_hook(sys.argv[sys.argv.index("--hook") + 1])
