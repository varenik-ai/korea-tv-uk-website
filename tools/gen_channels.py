#!/usr/bin/env python3
"""Rebuild korea-tv.uk channel pages (39 KO + 39 EN) on the russian-tv.com channel page template
(varenik-ai/russian-tv-site@3df9191, perviy-kanal-live/index.html).
Kept from each existing korea-tv.uk page: <head> (title, meta, canonical, hreflang, OG, JSON-LD, GA4), the "about" paragraphs,
FAQ, similar channels. Channel data (name, desc, icon, colours, category) comes from the home page CHANNEL_GROUPS.
Usage: python3 -I gen_channels.py <russian channel page html> <korea repo dir>"""
import html as H, os, re, sys

ru_path, repo = sys.argv[1], sys.argv[2]
RU = open(ru_path, encoding='utf-8').read()
os.chdir(repo)

def one(pat, s, flags=re.S):
    m = re.search(pat, s, flags); assert m, pat[:90]; return m

def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, (old[:90], c); return s.replace(old, new)

# ── шаблон Russia ────────────────────────────────────────────────────────────
styles = re.findall(r'<style[^>]*>(.*?)</style>', RU, re.S)
assert len(styles) == 3 and 'font-face' in styles[1]
CSS = styles[0]
CSS = rep(CSS, '--accent:#003580;--accent2:#1a5fd9;--red:#CC0000;', '--accent:#0047A0;--accent2:#1c66d4;--red:#CD2E3A;')   # корейские цвета
CSS2 = styles[2] + '.ch-icon-s.ch-logo-s{background:#fff!important}'   # korea-tv.uk: логотипы на светлой плашке
body = RU[RU.find('<body'):RU.find('<script', RU.find('<body'))]
SVG = re.findall(r'<svg.*?</svg>', body, re.S)
assert len(SVG) == 8, len(SVG)
SVG_TG, SVG_DESK, SVG_PULSE, SVG_MOB, SVG_MOB_ARROW, SVG_CARD, SVG_CARD_BTN, SVG_FOOT = SVG
MAIN = [b for a, b in re.findall(r'<script(?![^>]*src)([^>]*)>(.*?)</script>', RU, re.S) if 'createHls' in b][0]

TG = 'https://t.me/Korea_TV_hub'
SITE = 'https://korea-tv.uk'
CAT_SLUGS = ['korean-international-channels', 'korean-general-channels', 'korean-educational-channels', 'korean-public-broadcasting', 'korean-regional-channels',
             'korean-religious-channels', 'korean-business-shopping-channels', 'korean-music-radio-channels']
POPULAR = ['arirang', 'ebs1', 'ktv', 'tbs', 'ebs_kids']

def slug(cid): return cid.replace('_', '-') + '-live'
def strip_emoji(label): return re.sub(r'^[^\w가-힣]+', '', label).strip()

def channels(path):
    src = open(path, encoding='utf-8').read()
    block = one(r'const CHANNEL_GROUPS = \[\n(.*?)\n\];', src).group(1)
    groups = []
    for gm in re.finditer(r"\{ label: ?'([^']+)', channels: ?\[\n(.*?)\n\s*\] \}", block, re.S):
        chs = []
        for cm in re.finditer(r"\{ id:'([^']+)', name:'((?:[^'\\]|\\.)*)', desc:'((?:[^'\\]|\\.)*)', icon:'([^']*)', color:'([^']*)', iconBg:'([^']*)'(?:, logo:'([^']*)')?", gm.group(2)):
            chs.append(dict(id=cm.group(1), name=cm.group(2).replace("\\'", "'"), desc=cm.group(3).replace("\\'", "'"), icon=cm.group(4), color=cm.group(5), iconBg=cm.group(6), logo=cm.group(7)))
        groups.append(dict(label=gm.group(1), channels=chs))
    assert len(groups) == 8 and sum(len(g['channels']) for g in groups) == 39, [(g['label'], len(g['channels'])) for g in groups]
    return groups

DATA = {'ko': channels('index.html'), 'en': channels('en/index.html')}
for a, b in zip(DATA['ko'], DATA['en']):
    assert [c['id'] for c in a['channels']] == [c['id'] for c in b['channels']]

T = {
'ko': dict(back='← 전체 채널', tgbtn='텔레그램', home='홈', h1='{name} 실시간 무료 시청', crumb='{name} 온라인', live='실시간', meta3='24/7 실시간 방송',
    cta_aria='전체 채널 — 39개 채널 목록으로 돌아가기', cta='전체 39개 채널 — 다른 채널 선택', search='채널 검색...',
    banner='<b>텔레그램에서 시청하세요</b> — 39개 채널 전부를 하나의 앱으로, 무료', overlay='{name} — 눌러서 시청하기', fs='전체화면',
    pulse='텔레그램에서 채널 보기', status='▶ 버튼을 눌러 방송을 시작하세요', mob_title='텔레그램', mob_sub='새 채널 소식 · @Korea_TV_hub',
    card_live='실시간 · 24/7 실시간 방송', card_h='텔레그램에서 시청하세요', card_p='39개 채널 전부를 하나의 앱으로 — 무료. iOS, Android, 데스크톱 지원.',
    card_btn='@Korea_TV_hub 구독하기', about='{name} 채널 소개', faq='{name} 자주 묻는 질문', similar='비슷한 채널', popular='⭐ 인기 채널',
    foot_copy='© 2026 · 무료 한국 방송 온라인 시청', foot_links=[('/', '전체 채널'), ('/#faq', 'FAQ'), ('/privacy/', '개인정보처리방침')], foot_tg='텔레그램 구독',
    nostore='본 사이트는 영상을 저장하지 않습니다. 모든 방송은 제3자가 제공하며 인터넷상에 공개된 채널입니다.',
    js={'⏳ Обнаружено зависание кадра, переподключение...': '⏳ 화면 멈춤 감지, 재연결 중...', '⏳ Буферизация...': '⏳ 버퍼링 중...',
        '⏳ Восстановление воспроизведения...': '⏳ 재생 복구 중...', '⏳ Обнаружено зависание, переподключение...': '⏳ 멈춤 감지, 재연결 중...',
        '▶ Трансляция запущена': '▶ 방송 재생 중', '⏳ Восстановление после паузы...': '⏳ 일시정지 후 복구 중...',
        '⏳ Источник вещания временно недоступен, продолжаем попытки автоматически...': '⏳ 방송 소스가 일시적으로 응답하지 않습니다. 자동으로 계속 시도합니다...',
        '⏳ Переподключение к трансляции...': '⏳ 재연결 중...', "'⏳ Резервный сервер... ('": "'⏳ 다시 연결 중... ('",
        "'⏳ Переподключение ('": "'⏳ 재연결 ('", '⏳ Восстановление...': '⏳ 복구 중...', '⏳ Подключение...': '⏳ 연결 중...'}),
'en': dict(back='← All channels', tgbtn='Telegram', home='Home', h1='Watch {name} Live Online Free', crumb='{name} Live', live='LIVE', meta3='Live broadcast 24/7',
    cta_aria='All channels — back to the list of all 39 channels', cta='All 39 channels — pick another', search='Search channel...',
    banner='<b>Watch on Telegram</b> — all 39 channels in one app, free', overlay='{name} — click to watch', fs='Fullscreen',
    pulse='Watch channels in Telegram', status='Press ▶ to start the stream', mob_title='Telegram', mob_sub='New channels and updates · @Korea_TV_hub',
    card_live='LIVE · 24/7 broadcast', card_h='Watch on Telegram', card_p='All 39 channels in one app — free. On iOS, Android and Desktop.',
    card_btn='Subscribe to @Korea_TV_hub', about='About {name}', faq='{name} — FAQ', similar='Similar channels', popular='⭐ Popular channels',
    foot_copy='© 2026 · Free Korean TV Online', foot_links=[('/en/', 'All channels'), ('/en/#faq', 'FAQ'), ('/en/privacy/', 'Privacy')], foot_tg='Subscribe on Telegram',
    nostore='This site does not store any video content. All streams are provided by third parties and are publicly available on the internet.',
    js={'⏳ Обнаружено зависание кадра, переподключение...': '⏳ Frame stall detected, reconnecting...', '⏳ Буферизация...': '⏳ Buffering...',
        '⏳ Восстановление воспроизведения...': '⏳ Recovering playback...', '⏳ Обнаружено зависание, переподключение...': '⏳ Stall detected, reconnecting...',
        '▶ Трансляция запущена': '▶ Playing', '⏳ Восстановление после паузы...': '⏳ Recovering after pause...',
        '⏳ Источник вещания временно недоступен, продолжаем попытки автоматически...': '⏳ The source is temporarily unavailable, still retrying automatically...',
        '⏳ Переподключение к трансляции...': '⏳ Reconnecting...', "'⏳ Резервный сервер... ('": "'⏳ Reconnecting... ('",
        "'⏳ Переподключение ('": "'⏳ Reconnecting ('", '⏳ Восстановление...': '⏳ Recovering...', '⏳ Подключение...': '⏳ Connecting...'}),
}

def page_js(cid, lang):
    js = MAIN
    # прокси: korea-worker, без proxy.json
    js = re.sub(r"// Список прокси.*?var _proxyIdx = 0;\n// Горячая замена без передеплоя — грузим из /proxy.json\nfetch\('/proxy\.json'\).*?\}\)\.catch\(function\(\)\{\}\);\n",
                "// Прокси: korea-worker (гибридный режим v1.6.0); механизм ротации как у russian-tv.com, с одним адресом он повторяет его\n"
                "var PROXIES = ['https://korea-worker.dyaltd.workers.dev'];\nvar _proxyIdx = 0;\n", js, count=1, flags=re.S)
    assert "var PROXIES = ['https://korea-worker.dyaltd.workers.dev'];" in js
    js = rep(js, "const CH_ID = 'perviy';", "const CH_ID = '%s';" % cid)
    # программа передач (EPG) — только у russian-tv.com
    js, n = re.subn(r"\(function\(\) \{\n  var EPG_STR = .*?\n\}\)\(\);\n", '', js, count=1, flags=re.S); assert n == 1
    js = rep(js, "const TG_URL = 'https://t.me/RussiaTV_Hub_Live';", "const TG_URL = '%s';" % TG)
    # у Korea нет отдельного «нативного» источника
    js = rep(js, "    video.src = url + '&native=1';\n    try { window.rtvQuality && rtvQuality.attachNative(video, url + '&native=1'); } catch (e) {}",
                 "    video.src = url;\n    try { window.rtvQuality && rtvQuality.attachNative(video, url); } catch (e) {}")
    for a, b in T[lang]['js'].items():
        assert a in js, a
        js = js.replace(a, b)
    code = re.sub(r'//[^\n]*|/\*.*?\*/', '', js, flags=re.S)
    assert not re.search(r"['\"][^'\"\n]*[А-Яа-яЁё][^'\"\n]*['\"]", code), re.findall(r"['\"][^'\"\n]*[А-Яа-яЁё][^'\"\n]*['\"]", code)[:4]
    for bad in ('russian-tv', 'RussiaTV', 'epg', 'native=1', 'proxy.json', 'varenik-tab'):
        assert bad not in code, bad
    return js

TRACK = ("// Клик по ссылке на Telegram-канал — событие GA4 (как у russian-tv.com, без Яндекс.Метрики)\n(function(){\n"
         "  function tgTrack(e){\n    var a = e.target && e.target.closest ? e.target.closest('a[href*=\"t.me/Korea_TV_hub\"]') : null;\n    if(!a) return;\n"
         "    var label = a.className || 'tg-link';\n    try{ if(typeof gtag==='function') gtag('event','telegram_click',{event_category:'engagement',event_label:label,link_url:a.href}); }catch(err){}\n"
         "  }\n  document.addEventListener('click', tgTrack, true);\n})();\n")

def icon(c, cls):
    return '<div class="%s" style="background:%s;color:%s">%s</div>' % (cls, c['iconBg'], c['color'], H.escape(c['icon']))

def build(cid, lang):
    t = T[lang]
    groups = DATA[lang]
    pre = '' if lang == 'ko' else '/en'
    path = ('' if lang == 'ko' else 'en/') + slug(cid) + '/index.html'
    old = open(path, encoding='utf-8').read()
    gi = next(i for i, g in enumerate(groups) if any(c['id'] == cid for c in g['channels']))
    g = groups[gi]
    ch = next(c for c in g['channels'] if c['id'] == cid)
    name = ch['name']
    cat_name = strip_emoji(g['label'])
    cat_url = SITE + '/' + CAT_SLUGS[gi] + '/'

    # ── из старой страницы ──
    head = old[:old.find('</head>')]
    head = re.sub(r'\n\s*<style>@media\(max-width:1024px\)\{\.page-wrap\{grid-template-columns:minmax.*?</style>', '', head, flags=re.S)   # прошлый CSS2 — не дублировать при повторном запуске
    head = re.sub(r'<style>.*?</style>', lambda m: '<style>' + CSS + '</style>\n  <style>' + CSS2 + '</style>', head, count=1, flags=re.S)
    assert CSS in head
    if '<div class="desc-box">' in old:   # страница уже в формате russian-tv.com (или заготовка нового канала)
        desc_box = one(r'<div class="desc-box">(.*?)\n    </div>', old).group(1)
        paras_after = re.findall(r'<p>(.*?)</p>', desc_box)[1:]          # первый абзац — описание из данных главной
        faq_items = re.findall(r'<summary>(.*?) <span>▾</span></summary>\s*<p>(.*?)</p>', one(r'<div class="faq-box">(.*?)\n    </div>', old).group(1), re.S)
    else:                                  # исходный формат korea-tv.uk
        seo = one(r'<div class="seo-block">(.*?)<div class="card" style="margin-top:14px">\s*<h2>', old).group(1)
        paras_after = re.findall(r'<p>(.*?)</p>', seo.split('cat-tag-wrap', 1)[1])
        faq = one(r'<div class="card faq-box"[^>]*><h2>[^<]*</h2>(.*?)</div>\s*</div>\s*</div>\s*</div>\s*<footer>', old).group(1)
        faq_items = re.findall(r'<details><summary>(.*?)</summary><p>(.*?)</p></details>', faq, re.S)
    assert len(paras_after) >= 1, path
    assert len(faq_items) >= 3, (path, len(faq_items))
    # похожие — каналы той же категории по кольцу, начиная со следующего (как «Похожие каналы» у russian-tv.com)
    ids = [c['id'] for c in g['channels']]
    k = ids.index(cid)
    similar = [slug(x) for x in (ids[k + 1:] + ids[:k])]
    by_slug = {slug(c['id']): (c, strip_emoji(gg['label'])) for gg in groups for c in gg['channels']}

    # ── разметка по шаблону Russia ──
    sidebar = ''
    for gg in groups:
        sidebar += '      <div class="cat-label-s">%s</div>\n' % H.escape(strip_emoji(gg['label']))
        for c in gg['channels']:
            sidebar += ('<a href="%s/%s/" class="ch-item-s%s" data-name="%s" aria-label="%s">%s<div><div class="ch-name-s">%s</div><div class="ch-desc-s">%s</div></div><div class="live-dot-s"></div></a>\n'
                        % (pre, slug(c['id']), ' active' if c['id'] == cid else '', H.escape(c['name']), H.escape(c['name']), (('<div class="ch-icon-s ch-logo-s"><img src="%s" alt="%s" loading="lazy" width="30" height="30"></div>' % (c['logo'], H.escape(c['icon']))) if c.get('logo') else icon(c, 'ch-icon-s')), H.escape(c['name']), H.escape(c['desc'])))
    sim_html = ''.join('<a href="%s/%s/" class="sim-item">%s<div><div class="sim-name">%s</div><div class="sim-cat">%s</div></div><span class="sim-live">LIVE</span></a>\n'
                       % (pre, s, icon(by_slug[s][0], 'sim-icon'), H.escape(by_slug[s][0]['name']), H.escape(by_slug[s][1])) for s in similar[:4])
    pop_html = ''.join('      <a href="%s/%s/" class="pop-item">%s<span class="pop-name">%s</span><span class="pop-live">LIVE</span></a>\n'
                       % (pre, slug(p), icon(by_slug[slug(p)][0], 'pop-icon'), H.escape(by_slug[slug(p)][0]['name'])) for p in POPULAR)
    about_html = '\n'.join('    <p>%s</p>' % p for p in [H.escape(ch['desc'])] + paras_after)
    faq_html = '\n'.join('      <details>\n        <summary>%s <span>▾</span></summary>\n        <p>%s</p>\n      </details>' % (q, a) for q, a in faq_items)
    legal = one(r'(<div class="legal-note".*?</div>)', old if 'legal-note' in old else open(('' if lang == 'ko' else 'en/') + 'ebs1-live/index.html', encoding='utf-8').read()).group(1)
    other = (SITE + '/en/' if lang == 'ko' else SITE + '/') + slug(cid) + '/'
    me = SITE + pre + '/' + slug(cid) + '/'
    f = lambda k: t[k].format(name=H.escape(name))

    out = f'''{head}</head>
<body>

<header>
  <a href="{SITE}{pre}/" class="logo"><span class="logo-flag">🇰🇷</span><span class="logo-text"><span class="r">한</span><span class="b">국</span></span><span class="w">TV</span></a>
  <nav><a href="{SITE}{pre}/">{t['back']}</a></nav>
  <div class="h-right">
    <a href="{TG}" target="_blank" class="tg-btn">
      {SVG_TG}
      <span>{t['tgbtn']}</span>
    </a>
    <div class="lang-switch"><a href="{SITE}/{slug(cid)}/"{' class="active"' if lang == 'ko' else ''}>KO</a><a href="{SITE}/en/{slug(cid)}/"{' class="active"' if lang == 'en' else ''}>EN</a></div>
  </div>
</header>

<div class="breadcrumb">
  <a href="{SITE}{pre}/">{t['home']}</a><span>›</span>
  <a href="{cat_url}">{H.escape(cat_name)}</a><span>›</span>
  <span>{f('crumb')}</span>
</div>

<div class="page-title-wrap">
  <h1>{f('h1')}</h1>
  <div class="channel-meta">
    <span class="cat-badge">{H.escape(cat_name)}</span>
    <span class="live-badge"><span class="live-dot"></span>{t['live']}</span>
    <span>{t['meta3']}</span>
  </div>
</div>

<a href="{SITE}{pre}/#channels" class="all-channels-cta" aria-label="{t['cta_aria']}"><span class="all-channels-cta-icon">📺</span><span class="all-channels-cta-text">{t['cta']}</span><span class="all-channels-cta-arrow">→</span></a>

<div class="page-wrap">

  <aside class="left-sidebar">
    <div class="sidebar-search-wrap">
      <span class="s-icon">🔍</span>
      <input type="text" id="ch-search" placeholder="{t['search']}">
    </div>
    <div class="ch-list-scroll" id="ch-list">
{sidebar}    </div>
  </aside>

  <div class="main-col">
    <a href="{TG}" target="_blank" class="tg-banner-desk"><div class="tg-banner-desk-icon">{SVG_DESK}</div><div class="tg-banner-desk-text">{t['banner']}</div><span class="tg-banner-desk-arrow">→</span></a>

    <div class="player-wrap" id="player-wrap">
      <video id="video" playsinline webkit-playsinline poster="{SITE}/thumbnails/{slug(cid)}.jpg"></video>
      <div class="player-overlay" id="overlay">
        <div class="play-btn">▶</div>
        <div style="color:var(--muted);font-size:14px">{f('overlay')}</div>
      </div>
      <button class="fs-btn" id="fs-btn" title="{t['fs']}">⛶</button>
    </div>

    <a href="{TG}" target="_blank" rel="noopener" class="tg-pulse-banner"><div class="tg-pulse-icon">{SVG_PULSE}</div><div class="tg-pulse-text">{t['pulse']}</div><span class="tg-pulse-arrow">→</span></a>
    <div class="player-status" id="status">{t['status']}</div>

    <a href="{TG}" target="_blank" class="tg-mob-banner">
      <div class="tg-mob-banner-icon">
        {SVG_MOB}
      </div>
      <div class="tg-mob-banner-text">
        <div class="tg-mob-banner-title">{t['mob_title']}</div>
        <div class="tg-mob-banner-sub">{t['mob_sub']}</div>
      </div>
      {SVG_MOB_ARROW}
    </a>

    <div class="tg-card tg-card-mob">
      <div class="tg-card-live"><span class="tg-card-live-dot"></span>{t['card_live']}</div>
      <div style="width:52px;height:52px;background:#229ED9;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 10px">{SVG_CARD}</div>
      <h3>{t['card_h']}</h3>
      <p>{t['card_p']}</p>
      <a href="{TG}" target="_blank" class="tg-btn-card" style="gap:8px">{SVG_CARD_BTN} {t['card_btn']}</a>
      <div class="tg-sub">@Korea_TV_hub</div>
    </div>

    <div class="desc-box">
      <h2>{f('about')}</h2>
      <div class="cat-tag-wrap"><a href="{cat_url}" class="cat-tag">{H.escape(g['label'])}</a></div>
{about_html}
    </div>

    <div class="faq-box">
      <h2>{f('faq')}</h2>
{faq_html}
    </div>
  </div>

<div class="related-section">
    <div class="sim-box">
      <h3>{t['similar']}</h3>
{sim_html}    </div>

    <div class="pop-box">
      <div class="pop-title">{t['popular']}</div>
{pop_html}    </div>
</div>

<footer>
  <div class="footer-inner">
    <div>
      <div class="footer-logo">🇰🇷 <span style="color:#CD2E3A">한</span><span style="color:#1c66d4">국</span> <span style="color:#ffffff">TV</span></div>
      <div class="footer-copy" style="margin-top:4px">{t['foot_copy']}</div>
    </div>
    <div class="footer-links">
{''.join('      <a href="%s%s">%s</a>%s' % (SITE, u, n, chr(10)) for u, n in t['foot_links'])}    </div>
    <div class="footer-tg">
      <a href="{TG}" target="_blank">{SVG_FOOT} {t['foot_tg']}</a>
    </div>
  </div>
  <div style="text-align:center;margin-top:16px;font-size:11px;color:var(--muted2)">{t['nostore']}</div>
  {legal}
</footer>

<script>
{TRACK}</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/hls.js/1.5.15/hls.min.js"></script>
<script src="/assets/quality.js?v=1"></script>
<script defer src="/assets/site-ux.js?v=1"></script>
<script defer src="/assets/player-ui.js?v=2"></script>
<script defer src="/assets/cast.js?v=2"></script>
<script>{page_js(cid, lang)}</script>
</body>
</html>
'''
    assert me in head and other in head, path   # canonical/hreflang старой страницы на месте
    rest = re.sub(r'<script.*?</script>|<style.*?</style>|<svg.*?</svg>', '', out[out.find('<body'):], flags=re.S)
    assert not re.search(r'[А-Яа-яЁё]{3,}', rest), (path, re.findall(r'.{0,30}[А-Яа-яЁё]{3,}.{0,10}', rest)[:3])
    return path, out

n = 0
for lang in ('ko', 'en'):
    for gg in DATA[lang]:
        for c in gg['channels']:
            path, out = build(c['id'], lang)
            open(path, 'w', encoding='utf-8').write(out)
            n += 1
print('pages written:', n)
