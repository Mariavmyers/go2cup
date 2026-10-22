/* SportDGX on-site forms -> Make webhook.
 * One file for the whole site. Two forms:
 *   newsletter : SportDGX Insider "Weekend Game Plan"
 *   advertise  : advertising / sponsorship inquiry
 * Use:
 *   <a href="/insider.html#join" data-sdgx-form="newsletter">...</a>   opens a pop-up form
 *   <div data-sdgx-inline="newsletter"></div>                          shows the form in the page
 * Without JavaScript the links still go to the Insider / Advertise pages.
 */
(function () {
  'use strict';
  var HOOK = 'MAKE_WEBHOOK_URL';   // set by _tools/apply_forms.py
  var PRIVACY = '/privacy.html';

  var COPY = {
    newsletter: {
      kick: 'SportDGX Insider · free · weekly',
      title: 'Get the Weekend Game Plan',
      lead: 'Every week: the biggest games, the cheapest seats we can find, and a hotel deal near the stadium. One email. Unsubscribe anytime.',
      button: 'Send me the Game Plan',
      done: 'You\'re in! Watch your inbox for the next Weekend Game Plan.'
    },
    advertise: {
      kick: 'Advertise with SportDGX',
      title: 'Reach fans before game day',
      lead: 'Put your business in front of fans planning trips to games: city pages, sport pages, and the Weekend Game Plan email. Tell us about your business and we\'ll reply within 2 business days.',
      button: 'Send inquiry',
      done: 'Thanks! We got your inquiry and will reply within 2 business days.'
    }
  };

  var CSS = '' +
    '.sdgx-f{font-family:Inter,"Barlow",system-ui,sans-serif;color:#fff;background:#0a2413;border:1px solid rgba(33,194,90,.35);border-radius:18px;padding:24px;max-width:560px;box-sizing:border-box;text-align:left}' +
    '.sdgx-f *{box-sizing:border-box}' +
    '.sdgx-f .k{font-family:Oswald,"Barlow Condensed",sans-serif;font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#21c25a;margin:0 0 6px}' +
    '.sdgx-f h3{font-family:"Bebas Neue",Oswald,sans-serif;font-weight:400;font-size:34px;line-height:1;letter-spacing:.5px;margin:0 0 8px;color:#fff}' +
    '.sdgx-f p.l{font-size:14.5px;line-height:1.55;color:rgba(255,255,255,.75);margin:0 0 16px}' +
    '.sdgx-f label{display:block;font-size:12.5px;font-weight:600;color:rgba(255,255,255,.7);margin:10px 0 4px}' +
    '.sdgx-f input,.sdgx-f select,.sdgx-f textarea{width:100%;font:inherit;font-size:15px;color:#fff;background:#07180e;border:1px solid rgba(255,255,255,.18);border-radius:10px;padding:11px 12px;outline:none}' +
    '.sdgx-f select{appearance:auto}.sdgx-f option{color:#000}' +
    '.sdgx-f input:focus,.sdgx-f select:focus,.sdgx-f textarea:focus{border-color:#21c25a;box-shadow:0 0 0 3px rgba(33,194,90,.2)}' +
    '.sdgx-f .row{display:grid;grid-template-columns:1fr 1fr;gap:0 10px}' +
    '.sdgx-f button{margin-top:16px;width:100%;font-family:Oswald,"Barlow Condensed",sans-serif;font-weight:600;font-size:16px;letter-spacing:.08em;text-transform:uppercase;color:#07180e;background:#f5c518;border:0;border-radius:10px;padding:13px 16px;cursor:pointer}' +
    '.sdgx-f button:hover{background:#fff}.sdgx-f button:disabled{opacity:.6;cursor:wait}' +
    '.sdgx-f .fine{font-size:12px;color:rgba(255,255,255,.5);margin:10px 0 0;line-height:1.45}.sdgx-f .fine a{color:rgba(255,255,255,.7)}' +
    '.sdgx-f .hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}' +
    '.sdgx-f .msg{margin-top:12px;font-size:14px;line-height:1.5}.sdgx-f .msg.ok{color:#21c25a;font-weight:600}.sdgx-f .msg.err{color:#ff4338}' +
    '.sdgx-ov{position:fixed;inset:0;z-index:99999;background:rgba(2,8,5,.78);display:flex;align-items:center;justify-content:center;padding:16px;overflow:auto}' +
    '.sdgx-ov .sdgx-f{position:relative;width:100%;box-shadow:0 20px 60px rgba(0,0,0,.6)}' +
    '.sdgx-ov .x{position:absolute;top:10px;right:12px;width:36px;height:36px;margin:0;padding:0;background:transparent;color:#fff;font-size:26px;line-height:1;border-radius:8px}' +
    '.sdgx-ov .x:hover{background:rgba(255,255,255,.1)}' +
    '@media(max-width:480px){.sdgx-f{padding:20px 16px}.sdgx-f .row{grid-template-columns:1fr}.sdgx-f h3{font-size:30px}}';

  function addCss() {
    if (document.getElementById('sdgx-forms-css')) return;
    var s = document.createElement('style'); s.id = 'sdgx-forms-css'; s.textContent = CSS;
    document.head.appendChild(s);
  }

  function build(kind, source) {
    var c = COPY[kind];
    var f = document.createElement('form');
    f.className = 'sdgx-f'; f.noValidate = false;
    var body;
    if (kind === 'advertise') {
      body =
        '<div class="row"><div><label for="sd-n">Your name</label><input id="sd-n" name="name" autocomplete="name" required></div>' +
        '<div><label for="sd-b">Business</label><input id="sd-b" name="business" autocomplete="organization" required></div></div>' +
        '<div class="row"><div><label for="sd-e">Email</label><input id="sd-e" name="email" type="email" autocomplete="email" required></div>' +
        '<div><label for="sd-p">Phone (optional)</label><input id="sd-p" name="phone" type="tel" autocomplete="tel"></div></div>' +
        '<div class="row"><div><label for="sd-c">City</label><input id="sd-c" name="city" placeholder="e.g. Kansas City"></div>' +
        '<div><label for="sd-i">Interested in</label><select id="sd-i" name="interest">' +
        '<option>Not sure yet</option><option>City page listing</option><option>Sport page feature</option>' +
        '<option>Weekend Game Plan email mention</option><option>Game-day sponsorship</option><option>Sponsored article</option></select></div></div>' +
        '<label for="sd-m">Tell us about your business</label><textarea id="sd-m" name="message" rows="3"></textarea>';
    } else {
      body =
        '<div class="row"><div><label for="sd-e">Email</label><input id="sd-e" name="email" type="email" autocomplete="email" required placeholder="you@email.com"></div>' +
        '<div><label for="sd-n">First name (optional)</label><input id="sd-n" name="first_name" autocomplete="given-name"></div></div>' +
        '<label for="sd-s">Your sports (optional)</label><select id="sd-s" name="sport"><option value="">All of them</option>' +
        '<option>NFL</option><option>NBA</option><option>Soccer</option><option>UFC</option><option>Boxing</option><option>Tennis</option><option>Formula 1</option></select>';
    }
    f.innerHTML =
      '<p class="k">' + c.kick + '</p><h3>' + c.title + '</h3><p class="l">' + c.lead + '</p>' + body +
      '<div class="hp" aria-hidden="true"><label>Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label></div>' +
      '<button type="submit">' + c.button + '</button>' +
      '<p class="fine">' + (kind === 'newsletter'
        ? 'By signing up you agree to get the SportDGX Insider email from MainEntry LLC. Unsubscribe anytime. '
        : 'We only use your details to reply to you. ') +
      '<a href="' + PRIVACY + '">Privacy Policy</a></p><div class="msg" role="status" aria-live="polite"></div>';
    // make label ids unique when several forms are on one page
    var n = Math.random().toString(36).slice(2, 7);
    [].forEach.call(f.querySelectorAll('[id]'), function (el) {
      var old = el.id; el.id = old + '-' + n;
      var l = f.querySelector('label[for="' + old + '"]'); if (l) l.htmlFor = el.id;
    });
    f.addEventListener('submit', function (ev) { ev.preventDefault(); send(f, kind, source); });
    return f;
  }

  function send(f, kind, source) {
    var msg = f.querySelector('.msg'), btn = f.querySelector('button[type=submit]');
    if (!f.checkValidity()) { f.reportValidity(); return; }
    var data = new URLSearchParams(new FormData(f));
    if (data.get('website')) { msg.className = 'msg ok'; msg.textContent = COPY[kind].done; f.reset(); return; } // bot
    data.delete('website');
    data.set('form', kind);
    data.set('offer', kind === 'newsletter' ? 'Weekend Game Plan' : 'Advertising inquiry');
    data.set('source', source || '');
    data.set('page', location.pathname);
    data.set('submitted_at', new Date().toISOString());
    if (!/^https:\/\/hook\.[a-z0-9]+\.make\.com\//.test(HOOK)) {
      msg.className = 'msg err';
      msg.innerHTML = 'Sign-ups open soon. For now, email <a href="mailto:hello@mainentry.net" style="color:inherit">hello@mainentry.net</a>.';
      return;
    }
    btn.disabled = true; msg.className = 'msg'; msg.textContent = 'Sending...';
    fetch(HOOK, { method: 'POST', mode: 'no-cors', body: data })
      .then(function () {
        msg.className = 'msg ok'; msg.textContent = COPY[kind].done;
        [].forEach.call(f.querySelectorAll('input,select,textarea,button'), function (el) { el.disabled = true; });
        try { if (window.gtag) gtag('event', kind === 'newsletter' ? 'sign_up' : 'generate_lead', { method: 'sdgx_form', form_source: source || '' }); } catch (e) {}
      })
      .catch(function () {
        btn.disabled = false; msg.className = 'msg err';
        msg.innerHTML = 'That didn\'t go through. Please try again, or email <a href="mailto:hello@mainentry.net" style="color:inherit">hello@mainentry.net</a>.';
      });
  }

  function openModal(kind, source) {
    var ov = document.createElement('div');
    ov.className = 'sdgx-ov'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true');
    var f = build(kind, source);
    f.setAttribute('aria-label', COPY[kind].title);
    var x = document.createElement('button');
    x.type = 'button'; x.className = 'x'; x.setAttribute('aria-label', 'Close'); x.innerHTML = '&times;';
    f.insertBefore(x, f.firstChild);
    ov.appendChild(f);
    var last = document.activeElement;
    function close() { ov.remove(); document.removeEventListener('keydown', esc); if (last && last.focus) last.focus(); }
    function esc(e) { if (e.key === 'Escape') close(); }
    x.addEventListener('click', close);
    ov.addEventListener('click', function (e) { if (e.target === ov) close(); });
    document.addEventListener('keydown', esc);
    document.body.appendChild(ov);
    var first = f.querySelector('input:not([name=website])'); if (first) first.focus();
  }

  function init() {
    addCss();
    [].forEach.call(document.querySelectorAll('[data-sdgx-inline]'), function (box) {
      if (box.firstChild && box.querySelector('form.sdgx-f')) return;
      var kind = box.getAttribute('data-sdgx-inline');
      box.innerHTML = ''; box.appendChild(build(kind, box.getAttribute('data-source') || 'inline'));
    });
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[data-sdgx-form]');
      if (!a || e.ctrlKey || e.metaKey || e.shiftKey) return;
      e.preventDefault();
      openModal(a.getAttribute('data-sdgx-form'), a.getAttribute('data-source') || (a.textContent || '').trim().slice(0, 60));
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
}());
