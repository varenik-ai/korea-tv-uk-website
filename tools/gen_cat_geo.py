#!/usr/bin/env python3
"""Rebuild korea-tv.uk category pages (7, KO) and geo pages (5, EN) on russian-tv.com templates
(varenik-ai/russian-tv-site@3df9191: novosti/index.html and russkie-kanaly-v-ssha/index.html).
Kept from each existing page: <head> (meta, JSON-LD, GA4), h1, texts, FAQ, legal note. Channel data from the home pages.
Usage: python3 -I gen_cat_geo.py <russian category html> <russian geo html> <korea repo dir>"""
import html as H, os, re, sys

cat_ru, geo_ru, repo = sys.argv[1:4]
RC = open(cat_ru, encoding='utf-8').read()
RG = open(geo_ru, encoding='utf-8').read()
os.chdir(repo)

def one(pat, s, flags=re.S):
    m = re.search(pat, s, flags); assert m, pat[:90]; return m
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, (old[:90], c); return s.replace(old, new)

KOREAN_COLORS = ('--accent:#003580;--accent2:#1a5fd9;--red:#CC0000;', '--accent:#0047A0;--accent2:#1c66d4;--red:#CD2E3A;')
cs = re.findall(r'<style[^>]*>(.*?)</style>', RC, re.S); assert 'font-face' in cs[1]
CAT_CSS = rep(cs[0], *KOREAN_COLORS)
gs = re.findall(r'<style[^>]*>(.*?)</style>', RG, re.S); assert 'font-face' in gs[0]
GEO_CSS = rep(gs[1], *KOREAN_COLORS)
CAT_TG_SVG = one(r'class="tg-btn">\s*(<svg.*?</svg>)', RC).group(1)
GEO_TG_SVG = one(r'class="tg-btn">\s*(<svg.*?</svg>)', RG).group(1)

SITE, TG = 'https://korea-tv.uk', 'https://t.me/Korea_TV_hub'
CAT_SLUGS = ['korean-international-channels', 'korean-general-channels', 'korean-educational-channels', 'korean-public-broadcasting', 'korean-regional-channels',
             'korean-religious-channels', 'korean-business-shopping-channels', 'korean-music-radio-channels']
def slug(cid): return cid.replace('_', '-') + '-live'
def strip_emoji(label): return re.sub(r'^[^\w가-힣]+', '', label).strip()

def channels(path):
    src = open(path, encoding='utf-8').read()
    block = one(r'const CHANNEL_GROUPS = \[\n(.*?)\n\];', src).group(1)
    groups = []
    for gm in re.finditer(r"\{ label: ?'([^']+)', channels: ?\[\n(.*?)\n\s*\] \}", block, re.S):
        chs = [dict(id=c[0], name=c[1].replace("\\'", "'"), desc=c[2].replace("\\'", "'"), icon=c[3], color=c[4], iconBg=c[5])
               for c in re.findall(r"\{ id:'([^']+)', name:'((?:[^'\\]|\\.)*)', desc:'((?:[^'\\]|\\.)*)', icon:'([^']*)', color:'([^']*)', iconBg:'([^']*)'", gm.group(2))]
        groups.append(dict(label=gm.group(1), channels=chs))
    assert len(groups) == 8 and sum(len(g['channels']) for g in groups) == 39
    return groups
KO, EN = channels('index.html'), channels('en/index.html')

def head_of(old, css):
    head = old[:old.find('</head>')]
    head, n = re.subn(r'<style>.*?</style>', lambda m: '<style>' + css + '</style>', head, count=1, flags=re.S); assert n == 1
    return head

def faq_html(old):
    items = re.findall(r'<details>\s*<summary>(.*?)(?: <span>▾</span>)?</summary>\s*<p>(.*?)</p>\s*</details>', old, re.S)
    assert len(items) >= 3, len(items)
    return '\n'.join('    <details>\n      <summary>%s <span>▾</span></summary>\n      <p>%s</p>\n    </details>' % (q, a) for q, a in items)

legal_of = lambda old: one(r'(<div class="legal-note".*?</div>)', old).group(1)

# ── категории (KO) ───────────────────────────────────────────────────────────
def build_cat(i):
    path = CAT_SLUGS[i] + '/index.html'
    old = open(path, encoding='utf-8').read()
    g = KO[i]
    h1 = one(r'<h1>(.*?)</h1>', old).group(1)
    seo = re.search(r'<div class="seo-block"><div class="card"><h2>(.*?)</h2>(.*?)</div></div>', old, re.S) or one(r'<div class="seo-box">\s*<h2>(.*?)</h2>\s*(.*?)\n  </div>', old)
    nav = '\n'.join('    <a href="%s/%s/"%s>%s</a>' % (SITE, CAT_SLUGS[j], " class='cur'" if j == i else ' ', H.escape(KO[j]['label'])) for j in range(8))
    cards = ''.join('''
        <a href="%s/%s/" class="cat-ch-card">
          <div class="cat-ch-icon" style="background:%s;color:%s">%s</div>
          <div class="cat-ch-name">%s</div>
          <div class="cat-ch-desc">%s</div>
          <div class="cat-ch-live"><span class="cat-live-dot"></span>LIVE</div>
        </a>
''' % (SITE, slug(c['id']), c['iconBg'], c['color'], H.escape(c['icon']), H.escape(c['name']), H.escape(c['desc'])) for c in g['channels'])
    foot = '\n'.join('    <a href="%s/%s/">%s</a>' % (SITE, CAT_SLUGS[j], H.escape(strip_emoji(KO[j]['label']))) for j in range(8))
    out = f'''{head_of(old, CAT_CSS)}</head>
<body>
<header>
  <a href="{SITE}/" class="logo"><span style="font-size:26px">🇰🇷</span><span class="logo-text"><span class="r">한</span><span class="b">국</span></span><span class="w">TV</span></a>
  <a href="{TG}" target="_blank" class="tg-btn">
    {CAT_TG_SVG}
    텔레그램
  </a>
</header>
<div class="breadcrumb">
  <a href="{SITE}/">홈</a><span>›</span>
  <a href="{SITE}/#channels">채널</a><span>›</span>
  <span>{H.escape(strip_emoji(g['label']))}</span>
</div>
<div class="wrap">
  <div class="page-header">
    <h1>{h1}</h1>
    <div class="meta">
      <span class="badge">{len(g['channels'])}개 채널</span>
      <span class="live-badge"><span class="live-dot"></span>실시간 24/7</span>
    </div>
  </div>

  <nav class="cat-nav" aria-label="카테고리">
{nav}
  </nav>

  <div class="ch-grid">
{cards}
</div>

  <div class="seo-box">
    <h2>{seo.group(1)}</h2>
    {seo.group(2)}
  </div>

  <div class="faq-box" style="margin-top:16px">
    <h2>자주 묻는 질문</h2>
{faq_html(old)}
  </div>
</div>

<footer>
  <div>🇰🇷 <a href="{SITE}/">한국 TV</a> — 무료 한국 방송 온라인 시청</div>
  <div style="margin-top:6px">
{foot}
    <a href="{TG}" target="_blank">Telegram</a>
  </div>
  {legal_of(old)}
</footer>
</body>
</html>
'''
    open(path, 'w', encoding='utf-8').write(out)

# ── страницы по странам (EN) ─────────────────────────────────────────────────
GEO = [('korean-tv-in-usa', '🇺🇸', 'the USA', 'USA'), ('korean-tv-in-japan', '🇯🇵', 'Japan', 'Japan'), ('korean-tv-in-china', '🇨🇳', 'China', 'China'),
       ('korean-tv-in-canada', '🇨🇦', 'Canada', 'Canada'), ('korean-tv-in-australia', '🇦🇺', 'Australia', 'Australia')]

def build_geo(k):
    sl, flag, in_name, short = GEO[k]
    path = sl + '/index.html'
    old = open(path, encoding='utf-8').read()
    h1 = one(r'<h1>(.*?)</h1>', old).group(1)
    intro = re.search(r'<div class="card about-intro-card"[^>]*><h2>(.*?)</h2>(.*?)</div>', old, re.S) or one(r'<div class="seo-box">\s*<h2>(.*?)</h2>\s*(.*?)\n  </div>', old)
    cards = ''.join('''      <a href="%s/en/%s/" class="ch-card">
        <div class="ch-icon" style="background:%s;color:%s">%s</div>
        <div class="ch-name">%s</div>
        <div class="ch-desc">%s</div>
        <div class="ch-live"><span class="live-dot"></span>LIVE</div>
      </a>
''' % (SITE, slug(c['id']), c['iconBg'], c['color'], H.escape(c['icon']), H.escape(c['name']), H.escape(c['desc'])) for g in EN for c in g['channels'])
    others = '\n'.join('      <a href="%s/%s/">%s %s</a>' % (SITE, s, f, sh) for s, f, _, sh in GEO if s != sl)
    out = f'''{head_of(old, GEO_CSS)}</head>
<body>
<header>
  <a href="{SITE}/en/" class="logo"><span class="logo-flag">🇰🇷</span><span class="logo-text"><span class="r">한</span><span class="b">국</span></span><span class="w">TV</span></a>
  <a href="{TG}" target="_blank" class="tg-btn">
    {GEO_TG_SVG}
    Telegram
  </a>
</header>

<div class="breadcrumb">
  <a href="{SITE}/en/">Home</a><span>›</span>
  <span>Korean TV in {in_name}</span>
</div>

<div class="hero">
  <div class="hero-flag">{flag}</div>
  <h1>{h1}</h1>
  <p>39 Korean live channels — no VPN, no registration, no payment. Works on any device.</p>
  <div class="hero-badges">
    <span class="badge">✅ No VPN</span>
    <span class="badge">🆓 Free</span>
    <span class="badge">📱 All devices</span>
    <span class="badge">📡 39 channels</span>
    <span class="badge">🕐 Live 24/7</span>
  </div>
  <a href="{SITE}/en/" class="hero-cta">▶ Watch now — free</a>
</div>

<div class="wrap">
  <div class="info-grid">
    <div class="info-card"><div class="info-icon">📡</div><div class="info-val">39</div><div class="info-lbl">live channels</div></div>
    <div class="info-card"><div class="info-icon">🆓</div><div class="info-val">$0</div><div class="info-lbl">no subscription</div></div>
    <div class="info-card"><div class="info-icon">🌍</div><div class="info-val">No VPN</div><div class="info-lbl">works in {in_name}</div></div>
    <div class="info-card"><div class="info-icon">📱</div><div class="info-val">Any</div><div class="info-lbl">device</div></div>
  </div>

  <h2>All 39 Korean channels</h2>
  <div class="ch-grid">
{cards}</div>

  <div class="seo-box">
    <h2>{intro.group(1)}</h2>
    {intro.group(2)}
  </div>

  <div class="faq-box">
    <h2>FAQ</h2>
{faq_html(old)}
  </div>

  <div class="other-countries">
    <h2>Korean TV in other countries</h2>
    <div class="country-links">
{others}
    </div>
  </div>
</div>

<footer>
  <div>🇰🇷 <a href="{SITE}/en/">Korea TV</a> — free Korean TV online</div>
  <div style="margin-top:6px">
    <a href="{SITE}/en/">All channels</a>
    <a href="{SITE}/korean-international-channels/">International</a>
    <a href="{SITE}/korean-educational-channels/">EBS</a>
    <a href="{SITE}/korean-public-broadcasting/">Public</a>
    <a href="{SITE}/korean-regional-channels/">Regional</a>
    <a href="{TG}" target="_blank">Telegram</a>
  </div>
  <div style="margin-top:8px;color:#383855;font-size:11px">This site does not store any video content. Streams are provided by third parties.</div>
  {legal_of(old)}
</footer>
</body>
</html>
'''
    open(path, 'w', encoding='utf-8').write(out)

for i in range(8): build_cat(i)
for k in range(5): build_geo(k)
print('categories 8, geo 5 written')
