#!/usr/bin/env python3
"""Generates every founder card (HTML + .vcf + QR) from founders.json. Run: python3 build.py"""
import json, base64, html, io, os, re, sys
from PIL import Image, ImageOps
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))
import qr

ROOT = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(ROOT, 'founders.json')))
D, SITE = cfg['domain'], cfg['website']
e = lambda s: html.escape(s, quote=True)
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">'


HEAD_FX = '''<script>
    (function () { try {
      var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
      var nav = performance.getEntriesByType && performance.getEntriesByType('navigation')[0];
      var reload = !!(nav && nav.type === 'reload');
      var internal = false;
      try { internal = !!document.referrer && new URL(document.referrer).origin === location.origin; } catch (e) {}
      window.__splash = !reduce && (reload || !internal);
      if (window.__splash) { document.documentElement.classList.add('has-splash'); setTimeout(function () { document.documentElement.classList.remove('has-splash'); }, 6000); }
    } catch (e) {} })();
  </script>
  <link rel="stylesheet" href="/assets/splash.css">
  <script src="/assets/splash.js" defer></script>
  <script src="/assets/fx.js" defer></script>'''

ICONS = {
 'phone': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
 'mail': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="3"/><path d="m22 7-10 6L2 7"/></svg>',
 'globe': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
 'download': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/></svg>',
 'share': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><path d="m16 6-4-4-4 4"/><path d="M12 2v13"/></svg>',
 'copy': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
 'chevron': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg>',
 'WhatsApp': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.572-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.99c-.002 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>',
 'Facebook': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.5 22v-8h2.7l.4-3h-3.1V9.1c0-.9.3-1.5 1.6-1.5h1.7V4.9c-.3 0-1.3-.1-2.5-.1-2.5 0-4.1 1.5-4.1 4.3V11H8v3h2.2v8h3.3z"/></svg>',
 'Instagram': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1" fill="currentColor"/></svg>',
 'LinkedIn': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.94 8.5H4.12V20h2.82V8.5Z"/><path d="M5.53 3.97a1.64 1.64 0 1 0 0 3.28 1.64 1.64 0 0 0 0-3.28Z"/><path d="M20 20h-2.81v-5.58c0-1.33-.03-3.04-1.86-3.04-1.86 0-2.15 1.45-2.15 2.95V20H10.4V8.5h2.7v1.57h.04c.38-.72 1.31-1.86 3.2-1.86 3.43 0 4.06 2.26 4.06 5.21V20Z"/></svg>',
 'GitHub': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>',
}

def full_title(p):
    return f"{p['title']} · {p['role']}" if p.get('role') else p['title']

def square(src, px, q):
    im = ImageOps.exif_transpose(Image.open(os.path.join(ROOT, src))).convert('RGB')
    im = ImageOps.fit(im, (px, px), Image.LANCZOS, centering=(0.5, 0.35))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True); return b.getvalue()

def fold(line):
    out = []
    while len(line) > 75: out.append(line[:75]); line = ' ' + line[75:]
    return '\r\n'.join(out + [line])

def vcard(p, url, photo_small):
    email = p['email'] or cfg['company_email']
    L = ['BEGIN:VCARD', 'VERSION:3.0', f"N:{p['last']};{p['first']};;;", f"FN:{p['first']} {p['last']}",
         f"ORG:{cfg['company']}", f"TITLE:{full_title(p)}"]
    if p['phone']: L.append(f"TEL;TYPE=CELL:{p['phone']}")
    L.append(f"EMAIL;TYPE=INTERNET:{email}")
    L += [f"URL:{SITE}", f"URL;TYPE=card:{url}"]
    for name, link in p['links'].items(): L.append(f"URL;TYPE={name}:{link}")
    L.append('PHOTO;ENCODING=b;TYPE=JPEG:' + base64.b64encode(photo_small).decode())
    L.append('END:VCARD')
    return '\r\n'.join(fold(l) for l in L) + '\r\n'

def fmt_phone(n):
    m = re.fullmatch(r'\+94(\d{2})(\d{3})(\d{4})', n)
    return f'+94 {m.group(1)} {m.group(2)} {m.group(3)}' if m else n

def card(p):
    s = p['slug']; url = f"{D}/{s}/"; name = f"{p['first']} {p['last']}"
    email = p['email'] or cfg['company_email']
    title = f"{name} | {cfg['company']}"
    desc = f"{name}, {full_title(p)} at {cfg['company']}. Save contact details, email or connect on social media."
    def row(kind, icon, label, value, href, ext=False):
        t = ' target="_blank" rel="noopener noreferrer"' if ext else ''
        return (f'<a class="row-act {kind}" href="{e(href)}"{t}><span class="ico">{ICONS[icon]}</span>'
                f'<span class="txt"><b>{label}</b><small>{e(value)}</small></span><span class="chev">{ICONS["chevron"]}</span></a>')
    acts = []
    if p['phone']:
        digits = re.sub(r'\D', '', p['phone'])
        acts.append(row('call', 'phone', 'Call', fmt_phone(p['phone']), 'tel:' + p['phone']))
        acts.append(row('wa', 'WhatsApp', 'WhatsApp', 'Message on WhatsApp', f'https://wa.me/{digits}', True))
    acts.append(row('mail', 'mail', 'Email', email, 'mailto:' + email))
    acts.append(row('web', 'globe', 'Website', SITE.replace('https://', ''), SITE, True))
    soc = ''.join(f'<a class="soc {n.lower()}" href="{e(u)}" target="_blank" rel="noopener noreferrer" aria-label="{e(n)}" title="{e(n)}">{ICONS[n]}</a>' for n, u in p['links'].items())
    ld = {"@context": "https://schema.org", "@type": "Person", "name": name, "jobTitle": full_title(p),
          "worksFor": {"@type": "Organization", "name": cfg['company'], "url": SITE},
          "url": url, "image": f"{D}/assets/photos/{s}.jpg", "email": email, "sameAs": list(p['links'].values())}
    if p['phone']: ld["telephone"] = p['phone']
    svg = qr.to_svg(url, bg='#ffffff')
    open(os.path.join(ROOT, s, 'qr.svg'), 'w').write(svg)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="theme-color" content="#0070FF">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{url}">
  <meta name="robots" content="index, follow">
  <meta property="og:type" content="profile">
  <meta property="og:site_name" content="CYNOCOR">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{D}/assets/photos/{s}.jpg">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{e(title)}">
  <meta name="twitter:description" content="{e(desc)}">
  <meta name="twitter:image" content="{D}/assets/photos/{s}.jpg">
  <link rel="icon" href="/assets/logo3W.png" type="image/png">
  {FONTS}
  <link rel="stylesheet" href="/assets/cards.css">
  {HEAD_FX}
  <script type="application/ld+json">{json.dumps(ld)}</script>
</head>
<body class="cardpage">
  <div class="wrap">
    <main class="card">
      <section class="profile">
        <header class="banner">
          <a class="brand" href="{SITE}" aria-label="CYNOCOR website"><img src="/assets/logo3B.png" alt="" width="26" height="30"><span>CYNOCOR</span></a>
          <button class="icon-btn" id="share" type="button" aria-label="Share this card">{ICONS['share']}</button>
        </header>
        <div class="id">
          <img class="photo" src="/assets/photos/{s}.jpg" alt="{e(name)}" width="132" height="132" style="view-transition-name:ph-{s}">
          <h1>{e(name)}</h1>
          <p class="role"><span>{e(p['title'])}</span></p>
          {('<p class="focus">' + e(p['role']) + '</p>') if p.get('role') else ''}
          <p class="org">{e(cfg['company'])} &middot; Colombo, Sri Lanka</p>
          <p class="bio">{e(p['bio'])}</p>
        </div>
      </section>
      <section class="panel">
        <a class="save" href="/{s}/{s}.vcf" download="{e(name)}.vcf">{ICONS['download']}<span>Save to contacts</span></a>
        <nav class="acts" style="--n:{len(acts)}" aria-label="Contact options">{''.join(acts)}</nav>
        <div class="socs" aria-label="Social profiles">{soc}</div>
        <section class="qr" aria-label="QR code">
          <div class="qrbox">{svg}</div>
          <div class="qrtxt"><b>Scan to share</b><small>Open this card on any phone with the camera.</small>
            <button class="copy" id="copy" type="button">{ICONS['copy']}<span>Copy link</span></button></div>
        </section>
      </section>
      <div class="glare" aria-hidden="true"></div>
    </main>
    <p class="foot"><a href="/">All CYNOCOR cards</a></p>
  </div>
  <script>
    var data = {{ title: {json.dumps(title)}, url: location.href }};
    document.getElementById('share').addEventListener('click', function () {{
      if (navigator.share) {{ navigator.share(data).catch(function () {{}}); }}
      else if (navigator.clipboard) {{ navigator.clipboard.writeText(data.url); }}
    }});
    document.getElementById('copy').addEventListener('click', function () {{
      var l = this.querySelector('span'), t = l.textContent;
      if (navigator.clipboard) navigator.clipboard.writeText(data.url).then(function () {{ l.textContent = 'Copied'; setTimeout(function () {{ l.textContent = t; }}, 1600); }});
    }});
  </script>
</body>
</html>
'''

def directory():
    rows = ''.join(f'<a class="row" href="/{p["slug"]}/"><img src="/assets/photos/{p["slug"]}.jpg" alt="" width="64" height="64" style="view-transition-name:ph-{p["slug"]}"><div class="t"><b>{e(p["first"]+" "+p["last"])}</b><span>{e(full_title(p))}</span></div><span class="chev">{ICONS["chevron"]}</span></a>' for p in cfg['people'])
    title = 'CYNOCOR Contact Cards | Meet the Founders'
    desc = 'Digital contact cards for the CYNOCOR founders. Save contact details, email or connect on social media.'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{D}/">
  <meta name="robots" content="index, follow">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{D}/">
  <meta property="og:image" content="{SITE}/assets/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/assets/logo3W.png" type="image/png">
  {FONTS}
  <link rel="stylesheet" href="/assets/cards.css">
  {HEAD_FX}
</head>
<body>
  <div class="wrap dir">
    <header class="hero">
      <a class="brand" href="{SITE}" aria-label="CYNOCOR website"><img src="/assets/logo3B.png" alt="" width="26" height="30"><span>CYNOCOR</span></a>
      <h1>Meet the founders</h1>
      <p class="sub">Tap a card to save contact details.</p>
    </header>
    <div class="grid">{rows}</div>
  </div>
</body>
</html>
'''

for p in cfg['people']:
    os.makedirs(os.path.join(ROOT, p['slug']), exist_ok=True)
    open(os.path.join(ROOT, 'assets/photos', p['slug'] + '.jpg'), 'wb').write(square(p['photo'], 480, 85))
    open(os.path.join(ROOT, p['slug'], p['slug'] + '.vcf'), 'w', newline='').write(vcard(p, f"{D}/{p['slug']}/", square(p['photo'], 200, 80)))
    open(os.path.join(ROOT, p['slug'], 'index.html'), 'w').write(card(p))
open(os.path.join(ROOT, 'index.html'), 'w').write(directory())
open(os.path.join(ROOT, '404.html'), 'w').write(directory().replace('Meet the founders', 'Card not found').replace('Tap a card to save contact details.', 'That card does not exist. Pick one below.').replace('<meta name="robots" content="index, follow">', '<meta name="robots" content="noindex">'))
urls = [D + '/'] + [f"{D}/{p['slug']}/" for p in cfg['people']]
open(os.path.join(ROOT, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {D}/sitemap.xml\n')
open(os.path.join(ROOT, 'CNAME'), 'w').write('cards.cynocor.com')
print('built', len(cfg['people']), 'cards')
