# korea-tv.uk — сайт Korea TV

Статический сайт: 40 корейских каналов в прямом эфире, корейская (`/`) и английская (`/en/`) версии.
GitHub Pages из ветки `main`, домен в `CNAME`, DNS — Cloudflare (только DNS, без прокси). Сборки нет: что в репозитории, то и на сайте (~1 мин после push).

Потоки, мини-апп и бот — в репозитории [`varenik-ai/south-korea-tv-hub`](https://github.com/varenik-ai/south-korea-tv-hub)
(там же `ETALON.md`, `DEPLOY.md`, `BOT.md` и **`ADD_CHANNEL.md` — как добавить или убрать канал**, включая шаги для этого сайта).

Вёрстка и плеер — порт russian-tv.com (`varenik-ai/russian-tv-site@3df9191`). Рекламы, Яндекс.Метрики и Clarity нет.

## Страницы
| Путь | Что | Сколько |
|---|---|---|
| `index.html`, `en/index.html` | главные: плеер, боковой список, плитки, вкладки по группам, популярные, FAQ | 2 |
| `<slug>/`, `en/<slug>/` | страницы каналов (`ebs1-live`, `tvchosun-live`, …): плеер, список каналов, описание, FAQ, похожие каналы | 40 + 40 |
| `korean-*-channels/`, `korean-public-broadcasting/` | категории (ko): карточки каналов группы, SEO-текст, FAQ | 8 |
| `korean-tv-in-<страна>/` | страницы по странам (en): США, Япония, Китай, Канада, Австралия | 5 |
| `blog/`, `en/blog/` | статьи (по 3) + списки | 8 |
| `privacy/`, `en/privacy/` | политика: GA4, Google Cast, localStorage, раздел для правообладателей `#rightsholders`, контакт dyaltd@gmail.com | 2 |
| `404.html` | страница «не найдено» с категориями и популярными каналами | 1 |
| `natv-live/`, `sbs-live/`, `goodtv-live/`, `obs-gyeonggi-live/`, `mbc-chungbuk-live/`, `korean-terrestrial-channels/` (+ `en/`) | заглушки убранных каналов: `noindex`, canonical и переход на главную через 3 с. Не удалять — на них есть внешние ссылки | — |

Восемь групп и slug их категорий (порядок важен для генераторов): 국제 `korean-international-channels`, 종합편성 `korean-general-channels`,
EBS `korean-educational-channels`, 공영·정부 `korean-public-broadcasting`, 지역 `korean-regional-channels`,
종교 `korean-religious-channels`, 경제·쇼핑 `korean-business-shopping-channels`, 음악·라디오 `korean-music-radio-channels`.

## Источник данных о каналах
`CHANNEL_GROUPS` в `index.html` (ko) и `en/index.html` (en) — главный список для сайта. Из него генераторы строят боковой список,
похожие каналы, категории и страницы стран. Поля: `id`, `name`, `desc`, `icon`, `color`, `iconBg`, `logo` (если есть), `tags`.
Потоки: `https://korea-worker.dyaltd.workers.dev/stream?channel=<id>` (и `/stream-q` для выбора качества на iPhone).

## Скрипты плеера (`assets/`)
Адаптированные копии из russian-tv.com; что изменено — в шапке каждого файла. Подключение на главных и страницах каналов:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/hls.js/1.5.15/hls.min.js"></script>
<script src="/assets/quality.js?v=1"></script>
<script defer src="/assets/site-ux.js?v=1"></script>     <!-- только страницы каналов -->
<script defer src="/assets/player-ui.js?v=2"></script>
<script defer src="/assets/cast.js?v=2"></script>
```
| Файл | Что делает |
|---|---|
| `quality.js` | меню качества (`rtvQuality.attach(hls, video)`); на «Авто» не переключает уровень повторно — иначе медленные источники не стартуют |
| `player-ui.js` | единая панель плеера: звук, LIVE, качество, кинотеатр, PiP, полный экран, ошибка с «повторить» и похожими каналами |
| `cast.js` | AirPlay (Safari) и Google Cast (Chrome/Edge); Cast скрыт у каналов из `NO_CAST` — тех, что в воркере не в `DIRECT` (10 шт.) |
| `site-ux.js` | на страницах каналов при ширине ≤1024 px — вкладки категорий и лента каналов вместо бокового списка |
| `logos/` | логотипы каналов (PNG до 240×120). **Их же использует мини-апп** — не удалять и не переименовывать |

hls.js закреплён на `1.5.15` (как в мини-аппе). Изменил скрипт — подними `?v=` во всех страницах (и в `tools/gen_channels.py`), иначе браузеры возьмут старый из кеша.
На страницах каналов скрипты опираются на глобальные `CH_ID`, `CH_NAME`, `createHls()` и `hls`: их имена не менять.

## Генераторы (`tools/`)
Страницы каналов, категорий и стран собираются скриптами — вручную их не правят (правка пропадёт при следующей генерации).
| Скрипт | Что | Запуск |
|---|---|---|
| `gen_channels.py` | все страницы каналов ko+en на шаблоне страницы канала russian-tv.com. Из старой страницы берёт `<head>`, описание (`desc-box`) и FAQ, остальное из `CHANNEL_GROUPS` | `python3 -I tools/gen_channels.py <perviy-kanal-live.html> .` |
| `gen_cat_geo.py` | 8 категорий и 5 страниц стран (шаблоны `novosti/` и `russkie-kanaly-v-ssha/`) | `python3 -I tools/gen_cat_geo.py <novosti.html> <russkie-kanaly-v-ssha.html> .` |
| `make_thumbnails.py` | превью канала 1280×720 → `thumbnails/<slug>.jpg` (OG-картинка и картинка для Cast) | `python3 -I tools/make_thumbnails.py thumbnails <slug> <ICON> "<Name>" '#цвет'` |
| `normalize_logos.py` | логотипы → `assets/logos/` (обрезка полей, 240×120, PNG) | `python3 -I tools/normalize_logos.py <папка> assets/logos` |

Шаблоны russian-tv.com скачать из `varenik-ai/russian-tv-site@3df9191` в папку вне репозитория.
Генераторы идемпотентны: повторный запуск без изменения данных ничего не меняет. Каждая замена проверяется `assert`: при
несовпадении скрипт останавливается, а не портит страницы. Число каналов в текстах генераторы считают из `CHANNEL_GROUPS`; число групп (8) зашито в проверках.
Превью и логотипы требуют Pillow; шрифты превью — системные macOS.

## SEO
- У каждой страницы canonical и пара hreflang ko↔en (+ `x-default` → ko), JSON-LD (`WebSite`, `WebPage`, `VideoObject`/`BroadcastEvent`, `FAQPage`, `BreadcrumbList`)
- `sitemap.xml`: 105 адресов с `xhtml:link` hreflang и `lastmod`, без `changefreq`/`priority`; `robots.txt` указывает на него
- Подтверждения владения: `google90bb75ff5ce1a7ee.html` (Search Console), `BingSiteAuth.xml` (Bing), `167724622c7c85d7f0e443d9c7e5cd55.txt` (ключ IndexNow). Не удалять
- Аналитика: GA4 `G-X503KNBLXB` на всех страницах; событие `telegram_click`

## Проверка перед push
```bash
python3 -m http.server 8765
```
Открыть `http://localhost:8765/`, `/en/`, пару страниц каналов (DIRECT и через прокси, например `ebs1-live` и `tvchosun-live`), категорию:
канал играет, звук, меню качества, полный экран, логотипы, консоль без ошибок; ширина 375 px без горизонтальной прокрутки.
Отладка Cast: `?castdebug=1`.
