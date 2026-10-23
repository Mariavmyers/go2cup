/* SportDGX on-site forms -> Make webhook.
 *
 * Three forms, each keeping the purpose of the Google Form it replaced:
 *   newsletter : SportDGX Insider sign-up (needs a ticked consent box)
 *   guide      : guide request (Country Hopper Guide, Mexico Trip Guide); newsletter is a separate, unticked opt-in
 *   inquiry    : sponsorship / advertising / partnership / consulting inquiry; never subscribes anyone
 *
 * Use:
 *   <a href="/insider.html#join" data-sdgx-form="newsletter">...</a>             opens a pop-up form
 *   <a href="/hopper-guide.html#get-guide" data-sdgx-form="guide" data-guide="Country Hopper Guide">...</a>
 *   <div data-sdgx-inline="newsletter">[plain HTML fallback form]</div>         form shown in the page
 * Without JavaScript the links go to pages with a plain HTML form that posts straight to the webhook.
 *
 * The webhook URL is public by nature (it is visible to any browser). Abuse protection lives in
 * three places: here (honeypot, time trap, length limits, duplicate guard), in the "v" field the
 * Make scenario requires, and in the Make scenario's filters.
 */
(function () {
  'use strict';
  var HOOK = 'https://hook.us2.make.com/gaa3exq8a7pfh1mikkk77pxdxgxtqqlg';   // set by _tools/apply_forms.py --hook
  var VERSION = 'sdgx-forms-2';
  var PRIVACY = '/privacy.html';
  var CONTACT = 'contact@sportdgx.com';
  var MIN_MS = 2500;              // humans need longer than this to fill a form

  var COPY = {
    newsletter: {
      kick: 'SportDGX Insider · free · weekly',
      title: 'Get the Weekend Game Plan',
      lead: 'Every week: the biggest games, the cheapest seats we can find, and a hotel deal near the stadium. One email. Unsubscribe anytime.',
      button: 'Sign me up',
      done: 'Thanks! Your sign-up was received. The Weekend Game Plan goes to this address; you can unsubscribe at any time.'
    },
    guide: {
      kick: 'Free fan guide',
      title: 'Request the %GUIDE%',
      lead: 'Tell us where to send it. We\'ll email the guide to you.',
      button: 'Request my guide',
      done: 'Thanks! Your guide request was received. We\'ll email the guide to this address.'
    },
    inquiry: {
      kick: 'Sponsors & marketing',
      title: 'Advertise or partner with SportDGX',
      lead: 'Advertising, sponsorship, partnership or consulting: tell us what you have in mind and we\'ll reply by email.',
      button: 'Send inquiry',
      done: 'Thanks! Your inquiry was received. We\'ll reply by email.'
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
    '.sdgx-f label.cb{display:flex;gap:10px;align-items:flex-start;font-weight:400;font-size:13.5px;line-height:1.45;color:rgba(255,255,255,.85);margin:14px 0 0;cursor:pointer}' +
    '.sdgx-f label.cb input{width:18px;height:18px;flex:none;margin:1px 0 0;accent-color:#21c25a}' +
    '.sdgx-f button{margin-top:16px;width:100%;font-family:Oswald,"Barlow Condensed",sans-serif;font-weight:600;font-size:16px;letter-spacing:.08em;text-transform:uppercase;color:#07180e;background:#f5c518;border:0;border-radius:10px;padding:13px 16px;cursor:pointer}' +
    '.sdgx-f button:hover{background:#fff}.sdgx-f button:disabled{opacity:.6;cursor:not-allowed}' +
    '.sdgx-f .fine{font-size:12px;color:rgba(255,255,255,.55);margin:10px 0 0;line-height:1.45}.sdgx-f .fine a{color:rgba(255,255,255,.75)}' +
    '.sdgx-f .hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}' +
    '.sdgx-f .msg{margin-top:12px;font-size:14px;line-height:1.5}.sdgx-f .msg:empty{display:none}.sdgx-f .msg.ok{color:#21c25a;font-weight:600}.sdgx-f .msg.err{color:#ff7a70}' +
    '.sdgx-f .msg a{color:inherit}' +
    '.sdgx-ov{position:fixed;inset:0;z-index:99999;background:rgba(2,8,5,.78);display:flex;align-items:flex-start;justify-content:center;padding:16px;overflow:auto}' +
    '.sdgx-ov .sdgx-f{position:relative;width:100%;margin:auto 0;box-shadow:0 20px 60px rgba(0,0,0,.6)}' +
    '.sdgx-ov .x{position:absolute;top:10px;right:12px;width:36px;height:36px;margin:0;padding:0;background:transparent;color:#fff;font-size:26px;line-height:1;border-radius:8px}' +
    '.sdgx-ov .x:hover{background:rgba(255,255,255,.1)}' +
    '@media(max-width:480px){.sdgx-f{padding:20px 16px}.sdgx-f .row{grid-template-columns:1fr}.sdgx-f h3{font-size:30px}}';

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function addCss() {
    if (document.getElementById('sdgx-forms-css')) return;
    var s = document.createElement('style'); s.id = 'sdgx-forms-css'; s.textContent = CSS;
    document.head.appendChild(s);
  }

  function input(id, name, label, type, req, extra) {
    return '<div><label for="' + id + '">' + label + (req ? '' : ' (optional)') + '</label><input id="' + id + '" name="' + name +
      '" type="' + (type || 'text') + '"' + (req ? ' required' : '') + ' maxlength="' + (type === 'email' ? 254 : 120) + '"' + (extra || '') + '></div>';
  }

  function fields(kind, guide) {
    if (kind === 'inquiry') {
      return '<div class="row">' + input('sd-n', 'name', 'Your name', 'text', true, ' autocomplete="name"') +
        input('sd-b', 'business', 'Business or organization', 'text', false, ' autocomplete="organization"') + '</div>' +
        '<div class="row">' + input('sd-e', 'email', 'Email', 'email', true, ' autocomplete="email"') +
        input('sd-p', 'phone', 'Phone', 'tel', false, ' autocomplete="tel"') + '</div>' +
        '<div class="row"><div><label for="sd-t">Inquiry type</label><select id="sd-t" name="inquiry_type" required>' +
        '<option>Advertising</option><option>Sponsorship or partnership</option><option>Consulting services</option><option>Something else</option></select></div>' +
        input('sd-c', 'city', 'City', 'text', false, ' placeholder="e.g. Kansas City"') + '</div>' +
        '<label for="sd-m">Message</label><textarea id="sd-m" name="message" rows="4" maxlength="2000" required></textarea>';
    }
    if (kind === 'guide') {
      var mexico = /mexico/i.test(guide);
      return '<div class="row">' + input('sd-e', 'email', 'Email', 'email', true, ' autocomplete="email" placeholder="you@email.com"') +
        input('sd-n', 'first_name', 'First name', 'text', false, ' autocomplete="given-name"') + '</div>' +
        (mexico
          ? '<div class="row">' + input('sd-d', 'departure_city', 'Departing from', 'text', false, ' placeholder="e.g. Kansas City"') +
            input('sd-g', 'budget', 'Budget', 'text', false, ' placeholder="e.g. $1,500"') + '</div>' +
            '<label for="sd-m">What should the itinerary cover? (optional)</label><textarea id="sd-m" name="message" rows="3" maxlength="2000"></textarea>'
          : '<div class="row">' + input('sd-l', 'last_name', 'Last name', 'text', false, ' autocomplete="family-name"') +
            input('sd-t', 'team', 'Which country are you cheering for?', 'text', false) + '</div>') +
        '<label class="cb"><input type="checkbox" name="newsletter_opt_in" value="yes"> <span>Also send me the free <b>Weekend Game Plan</b> email (optional, unsubscribe anytime).</span></label>';
    }
    return '<div class="row">' + input('sd-e', 'email', 'Email', 'email', true, ' autocomplete="email" placeholder="you@email.com"') +
      input('sd-n', 'first_name', 'First name', 'text', false, ' autocomplete="given-name"') + '</div>' +
      '<label for="sd-s">Your sports (optional)</label><select id="sd-s" name="sport"><option value="">All of them</option>' +
      '<option>NFL</option><option>NBA</option><option>Soccer</option><option>UFC</option><option>Boxing</option><option>Tennis</option><option>Formula 1</option></select>' +
      '<label class="cb"><input type="checkbox" name="newsletter_opt_in" value="yes" required> <span>Yes, email me the SportDGX Insider <b>Weekend Game Plan</b>. I can unsubscribe at any time.</span></label>';
  }

  function fine(kind) {
    if (kind === 'inquiry') return 'We use your details only to reply to this inquiry. This does not sign you up for any newsletter. ';
    if (kind === 'guide') return 'We use your email to send the guide. You get the newsletter only if you tick the box. ';
    return 'Sent by MainEntry LLC. We never sell your email. ';
  }

  function build(kind, source, guide) {
    var c = COPY[kind];
    var f = document.createElement('form');
    f.className = 'sdgx-f';
    f.setAttribute('data-kind', kind);
    f.innerHTML =
      '<p class="k">' + c.kick + '</p><h3>' + esc(c.title.replace('%GUIDE%', guide || 'guide')) + '</h3><p class="l">' + c.lead + '</p>' + fields(kind, guide || '') +
      '<div class="hp" aria-hidden="true"><label>Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label></div>' +
      '<button type="submit">' + c.button + '</button>' +
      '<p class="fine">' + fine(kind) + '<a href="' + PRIVACY + '">Privacy Policy</a></p><div class="msg" role="status" aria-live="polite"></div>';
    var n = Math.random().toString(36).slice(2, 7);   // unique ids when several forms are on one page
    [].forEach.call(f.querySelectorAll('[id]'), function (el) {
      var old = el.id; el.id = old + '-' + n;
      var l = f.querySelector('label[for="' + old + '"]'); if (l) l.htmlFor = el.id;
    });
    f._shownAt = Date.now();
    f.addEventListener('submit', function (ev) { ev.preventDefault(); send(f, kind, source, guide); });
    return f;
  }

  // What to tell the person after a successful submission. For guides, Make reports whether the
  // download link was emailed ("sent"), failed, or is handled by hand (empty), and we say only that.
  function doneText(kind, reply, email) {
    if (kind === 'guide') {
      var st = (reply && reply.guide_status) || '';
      if (st === 'sent') return 'Done! We\'ve emailed the download link to ' + email + '. If it isn\'t in your inbox in a few minutes, check spam or promotions.';
      if (st === 'failed') return 'Your request was received, but the email didn\'t go out automatically. We\'ll send the guide to ' + email + ' by hand.';
    }
    return COPY[kind].done;
  }

  function fail(msg, html) { msg.className = 'msg err'; msg.innerHTML = html; }

  function send(f, kind, source, guide) {
    var msg = f.querySelector('.msg'), btn = f.querySelector('button[type=submit]');
    if (f._busy || f._done) return;                               // duplicate clicks / Enter presses
    if (!f.checkValidity()) { f.reportValidity(); return; }
    var data = new URLSearchParams(new FormData(f));
    if (data.get('email')) data.set('email', data.get('email').trim().toLowerCase());   // one key per address for duplicate checks
    if (data.get('website')) return;                               // bot filled the hidden field: send nothing, claim nothing
    if (Date.now() - f._shownAt < MIN_MS) { fail(msg, 'Please take a second to check your details, then press the button again.'); f._shownAt = 0; return; }
    data.delete('website');
    if (!data.get('newsletter_opt_in')) data.set('newsletter_opt_in', 'no');
    data.set('form', kind);
    data.set('purpose', kind === 'newsletter' ? 'Newsletter: Weekend Game Plan' : kind === 'guide' ? 'Guide request: ' + (guide || '') : 'Inquiry');
    if (guide) data.set('guide', guide);
    data.set('source', (source || '').slice(0, 80));
    data.set('page', location.pathname);
    data.set('submitted_at', new Date().toISOString());
    data.set('submission_id', (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(36).slice(2));
    data.set('js', '1');
    data.set('v', VERSION);
    if (/@sportdgx\.test$/i.test(data.get('email') || '')) data.set('test', 'yes');   // test addresses never reach MailerLite
    var key = 'sdgx:' + kind + ':' + (guide || '') + ':' + (data.get('email') || '').toLowerCase();
    try { if (sessionStorage.getItem(key)) { msg.className = 'msg ok'; msg.textContent = 'We already received this from you a moment ago, so we didn\'t send it twice.'; return; } } catch (e) {}
    if (!/^https:\/\/hook\.[a-z0-9]+\.make\.com\/[A-Za-z0-9]+$/.test(HOOK)) {
      fail(msg, 'This form isn\'t connected yet. Please email <a href="mailto:' + CONTACT + '">' + CONTACT + '</a> instead.');
      return;
    }
    f._busy = true; btn.disabled = true; msg.className = 'msg'; msg.textContent = 'Sending...';
    var ctl = window.AbortController ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, 15000);
    fetch(HOOK, { method: 'POST', body: data, signal: ctl ? ctl.signal : undefined })
      .then(function (res) {
        return res.text().then(function (t) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          var j = null;
          try { j = JSON.parse(t); } catch (e) { j = null; }
          if (!j || j.ok !== true) throw new Error('unexpected reply');   // only the scenario's own reply counts as success
          return j;
        });
      })
      .then(function (j) {
        clearTimeout(timer); f._busy = false; f._done = true;
        msg.className = 'msg ok'; msg.textContent = doneText(kind, j, data.get('email'));
        [].forEach.call(f.querySelectorAll('input,select,textarea,button:not(.x)'), function (el) { el.disabled = true; });
        try { sessionStorage.setItem(key, '1'); } catch (e) {}
        try { if (window.gtag) gtag('event', kind === 'inquiry' ? 'generate_lead' : 'sign_up', { method: 'sdgx_form', form_kind: kind, form_source: source || '' }); } catch (e) {}
      })
      .catch(function () {
        clearTimeout(timer); f._busy = false; btn.disabled = false;
        fail(msg, 'That didn\'t go through, so nothing was sent. Please try again, or email <a href="mailto:' + CONTACT + '">' + CONTACT + '</a>.');
      });
  }

  function openModal(kind, source, guide) {
    var ov = document.createElement('div');
    ov.className = 'sdgx-ov'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true');
    var f = build(kind, source, guide);
    f.setAttribute('aria-label', f.querySelector('h3').textContent);
    var x = document.createElement('button');
    x.type = 'button'; x.className = 'x'; x.setAttribute('aria-label', 'Close'); x.innerHTML = '&times;';
    f.insertBefore(x, f.firstChild);
    ov.appendChild(f);
    var last = document.activeElement;
    function close() { ov.remove(); document.removeEventListener('keydown', onKey); if (last && last.focus) last.focus(); }
    function onKey(e) { if (e.key === 'Escape') close(); }
    x.addEventListener('click', close);
    ov.addEventListener('click', function (e) { if (e.target === ov) close(); });
    document.addEventListener('keydown', onKey);
    document.body.appendChild(ov);
    var first = f.querySelector('input:not([name=website])'); if (first) first.focus();
  }

  var KINDS = { newsletter: 1, guide: 1, inquiry: 1, advertise: 'inquiry' };
  function kindOf(k) { return KINDS[k] === 1 ? k : (KINDS[k] || 'newsletter'); }

  function init() {
    addCss();
    [].forEach.call(document.querySelectorAll('[data-sdgx-inline]'), function (box) {
      if (box.querySelector('form.sdgx-f[data-kind]')) return;
      box.innerHTML = '';
      box.appendChild(build(kindOf(box.getAttribute('data-sdgx-inline')), box.getAttribute('data-source') || 'inline', box.getAttribute('data-guide') || ''));
    });
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[data-sdgx-form]');
      if (!a || e.ctrlKey || e.metaKey || e.shiftKey || e.button > 0) return;
      e.preventDefault();
      openModal(kindOf(a.getAttribute('data-sdgx-form')), a.getAttribute('data-source') || (a.textContent || '').trim().slice(0, 60), a.getAttribute('data-guide') || '');
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
}());
