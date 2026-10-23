"""Plain HTML versions of the SportDGX forms, for visitors without JavaScript.

They post straight to the Make webhook. The Make scenario answers a no-JavaScript post with a
redirect to /thanks.html once the record is saved. With JavaScript on, /assets/sdgx-forms.js
replaces these with the full forms. Field names match the script exactly.
"""
from html import escape

STYLE = ('<style>.sdgx-static{font-family:Inter,system-ui,sans-serif;color:#fff;background:#0a2413;border:1px solid rgba(33,194,90,.35);'
         'border-radius:18px;padding:22px;max-width:560px;text-align:left}.sdgx-static h3{font-family:"Bebas Neue",Oswald,sans-serif;font-weight:400;'
         'font-size:30px;margin:0 0 8px;color:#fff}.sdgx-static label{display:block;font-size:13px;font-weight:600;color:rgba(255,255,255,.75);margin:10px 0 4px}'
         '.sdgx-static input,.sdgx-static select,.sdgx-static textarea{width:100%;box-sizing:border-box;font:inherit;font-size:15px;color:#fff;background:#07180e;'
         'border:1px solid rgba(255,255,255,.25);border-radius:10px;padding:10px 12px}.sdgx-static label.cb{display:flex;gap:10px;font-weight:400}'
         '.sdgx-static label.cb input{width:18px;height:18px;flex:none}.sdgx-static button{margin-top:14px;width:100%;font:600 16px Oswald,sans-serif;'
         'letter-spacing:.08em;text-transform:uppercase;color:#07180e;background:#f5c518;border:0;border-radius:10px;padding:12px}'
         '.sdgx-static .hp{position:absolute;left:-9999px}.sdgx-static p{font-size:13px;color:rgba(255,255,255,.65);line-height:1.5}'
         '.sdgx-static a{color:rgba(255,255,255,.8)}</style>')


def _in(name, label, typ="text", req=False, maxlen=120):
    return '<label>%s%s<input name="%s" type="%s" maxlength="%d"%s></label>' % (
        escape(label), "" if req else " (optional)", name, typ, 254 if typ == "email" else maxlen, " required" if req else "")


def static_form(kind, guide, source, hook):
    if kind == "inquiry":
        title = "Advertise or partner with SportDGX"
        body = (_in("name", "Your name", req=True) + _in("business", "Business or organization") +
                _in("email", "Email", "email", True) + _in("phone", "Phone", "tel") +
                '<label>Inquiry type<select name="inquiry_type" required><option>Advertising</option><option>Sponsorship or partnership</option>'
                '<option>Consulting services</option><option>Something else</option></select></label>' + _in("city", "City") +
                '<label>Message<textarea name="message" rows="4" maxlength="2000" required></textarea></label>')
        note = "We use your details only to reply to this inquiry. This does not sign you up for any newsletter."
        button = "Send inquiry"
    elif kind == "guide":
        title = "Request the " + guide
        body = _in("email", "Email", "email", True) + _in("first_name", "First name")
        if "mexico" in guide.lower():
            body += (_in("departure_city", "Departing from") + _in("budget", "Budget") +
                     '<label>What should the itinerary cover? (optional)<textarea name="message" rows="3" maxlength="2000"></textarea></label>')
        else:
            body += _in("last_name", "Last name") + _in("team", "Which country are you cheering for?")
        body += ('<label class="cb"><input type="checkbox" name="newsletter_opt_in" value="yes"> <span>Also send me the free Weekend Game Plan email '
                 '(optional, unsubscribe anytime).</span></label>')
        note = "We use your email to send the guide. You get the newsletter only if you tick the box."
        button = "Request my guide"
    else:
        title = "Get the Weekend Game Plan"
        body = (_in("email", "Email", "email", True) + _in("first_name", "First name") +
                '<label>Your sports (optional)<select name="sport"><option value="">All of them</option><option>NFL</option><option>NBA</option>'
                '<option>Soccer</option><option>UFC</option><option>Boxing</option><option>Tennis</option><option>Formula 1</option></select></label>'
                '<label class="cb"><input type="checkbox" name="newsletter_opt_in" value="yes" required> <span>Yes, email me the SportDGX Insider '
                'Weekend Game Plan. I can unsubscribe at any time.</span></label>')
        note = "Sent by MainEntry LLC. We never sell your email."
        button = "Sign me up"
    purpose = {"newsletter": "Newsletter: Weekend Game Plan", "guide": "Guide request: " + guide, "inquiry": "Inquiry"}[kind]
    hidden = "".join('<input type="hidden" name="%s" value="%s">' % (k, escape(v)) for k, v in
                     [("form", kind), ("guide", guide), ("purpose", purpose), ("source", source), ("v", "sdgx-forms-2")])
    return (STYLE + '<form class="sdgx-f sdgx-static" method="post" action="%s" accept-charset="UTF-8"><h3>%s</h3>%s%s'
            '<div class="hp" aria-hidden="true"><label>Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label></div>'
            '<button type="submit">%s</button><p>%s <a href="/privacy.html">Privacy Policy</a></p></form>'
            % (escape(hook), escape(title), body, hidden, button, note))
