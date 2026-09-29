#!/usr/bin/env python3
"""Сборка сайта «Территория праздника».

Запуск:  python3 build.py            -> папка public/ (для хостинга, чистые адреса)
         python3 build.py --preview  -> папка preview/ (ссылки ведут на index.html,
                                        чтобы сайт открывался без сервера)

Данные: src/data/products.json, статьи блога: src/blog/*.md
"""
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
SRC = ROOT / "src"
PREVIEW = "--preview" in sys.argv
OUT = ROOT / ("preview" if PREVIEW else "public")
SITE_URL = "https://territoriaprazdnika.ru"
SITE_NAME = "Территория праздника"
EMAIL = "svetlichok777@gmail.com"
MAIL = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'

PRODUCTS = json.loads((SRC / "data" / "products.json").read_text(encoding="utf-8"))

e = html.escape


# ---------- пути ----------
def link(depth, target):
    """Ссылка на страницу сайта из страницы с глубиной depth.
    target: '' (главная), 'kvesty/', 'kvesty/slug/', 'img/x.jpg', 'kvesty/#picker'"""
    up = "../" * depth
    anchor = ""
    if "#" in target:
        target, anchor = target.split("#", 1)
        anchor = "#" + anchor
    if PREVIEW and (target == "" or target.endswith("/")):
        target += "index.html"
    return (up + target + anchor) or "./"


def fmt_price(p):
    return f"{p:,}".replace(",", " ") + " ₽"


def plural_q(n):
    m10, m100 = n % 10, n % 100
    if m10 == 1 and m100 != 11:
        return "задание"
    if 2 <= m10 <= 4 and not 12 <= m100 <= 14:
        return "задания"
    return "заданий"


# ---------- общие куски ----------
LOGO = """<svg width="40" height="40" viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="20" fill="#5A2D8A"/><rect x="11" y="18" width="18" height="13" rx="1.5" fill="#FFF6E8"/><rect x="9.5" y="14" width="21" height="5" rx="1.5" fill="#FFF6E8"/><rect x="18.3" y="14" width="3.4" height="17" fill="#F57F5F"/><path d="M20 14c-2.5-4.5-7-4-6-1.2.7 1.8 6 1.2 6 1.2s5.3.6 6-1.2c1-2.8-3.5-3.3-6 1.2z" fill="none" stroke="#F57F5F" stroke-width="1.8" stroke-linejoin="round"/><path d="M30 8l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z" fill="#F6C544"/></svg>"""

CHEVRON = '<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 7l5 5 5-5"/></svg>'


def head(depth, title, desc, path, og_image=None, extra=""):
    canonical = SITE_URL + "/" + path
    og_img = SITE_URL + "/" + (og_image or "img/og.jpg")
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta property="og:locale" content="ru_RU">
<link rel="icon" href="{link(depth, 'favicon.svg')}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&family=Unbounded:wght@700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{link(depth, 'css/site.css')}">
{extra}</head>
<body>
<a class="skip" href="#main">Перейти к содержанию</a>
"""


def header(depth, current=""):
    def a(target, text, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{link(depth, target)}"{cur}>{text}</a>'
    return f"""<header class="site-header">
<div class="wrap">
<a class="logo" href="{link(depth, '')}">{LOGO}<span>Территория<br>праздника</span></a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav" aria-label="Меню"><svg width="22" height="22" viewBox="0 0 22 22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M3 6h16M3 11h16M3 16h16"/></svg></button>
<nav id="nav" class="nav" aria-label="Главное меню">
{a('kvesty/#picker', 'Подобрать квест', 'picker')}
{a('kvesty/', 'Все квесты', 'catalog')}
{a('#how', 'Как это работает', 'how')}
{a('blog/', 'Блог', 'blog')}
</nav>
</div>
</header>
<main id="main">
"""


def footer(depth):
    year = date.today().year
    return f"""</main>
<footer class="site-footer">
<div class="bunting" aria-hidden="true"></div>
<div class="wrap">
<div>
<strong>Территория праздника</strong>
<span>Готовые квесты и сценарии праздников для печати</span>
<small>© {year} Территория праздника</small>
</div>
<nav aria-label="Нижнее меню">
<a href="{link(depth, 'kvesty/')}">Все квесты</a>
<a href="{link(depth, 'blog/')}">Блог</a>
<a href="{link(depth, 'oplata-i-poluchenie/')}">Оплата и получение</a>
<a href="{link(depth, 'oferta/')}">Оферта</a>
<a href="{link(depth, 'politika-konfidencialnosti/')}">Политика конфиденциальности</a>
<a href="{link(depth, 'kontakty/')}">Контакты</a>
</nav>
</div>
</footer>
<script src="{link(depth, 'js/site.js')}" defer></script>
</body>
</html>
"""


# ---------- карточки ----------
def cover(p, depth, big=False, title_in_cover=False):
    style = f'background:{p["cover_bg"]};color:{p["cover_ink"]}'
    if p.get("image"):
        return f"""<div class="cover" style="{style}"><img src="{link(depth, p['image'])}" alt="Обложка квеста «{e(p['short'])}»" loading="lazy" width="600" height="750"><span class="badge">{e(p['badge'])}</span></div>"""
    title = f'<div class="big">{e(p["short"])}</div>' if (big or title_in_cover) else ""
    return f"""<div class="cover" style="{style}" role="img" aria-label="Обложка «{e(p['short'])}»"><span class="badge">{e(p['badge'])}</span><span class="stamp" aria-hidden="true">{e(p['stamp'])}</span>{title}<span class="series">{e(p['series'])}</span></div>"""


def card(p, depth):
    href = link(depth, f"kvesty/{p['slug']}/")
    data = " ".join(f'data-{k}="{" ".join(p["f_" + k])}"' for k in ("age", "occ", "place", "group"))
    meta = f"{p['ages']} · {p['place']} · {p['players']}"
    return f"""<a class="card-q" href="{href}" data-quest {data}>
{cover(p, depth, title_in_cover=True)}
<div class="card-body">
<h3>{e(p['title'])}</h3>
<div class="meta">{e(meta)}</div>
<p>{e(p['desc'])}</p>
<div class="card-foot"><span class="price-tag">{fmt_price(p['price'])}</span><span class="btn btn-sm">Подробнее</span></div>
</div>
</a>"""


def select(name, label, options):
    opts = "".join(f'<option value="{v}">{t}</option>' for v, t in options)
    return f"""<div class="field"><label for="f-{name}">{label}</label><div class="select"><select id="f-{name}" name="{name}">{opts}</select>{CHEVRON}</div></div>"""


def picker(depth, heading_tag="h2", heading="Подберём квест под ваш праздник"):
    cards = "\n".join(card(p, depth) for p in PRODUCTS)
    return f"""<section class="section picker confetti" id="picker" aria-labelledby="picker-title">
<div class="wrap">
<div class="section-head">
<div><{heading_tag} id="picker-title">{heading}</{heading_tag}><p>Выберите параметры — подходящие квесты останутся ниже.</p></div>
</div>
<form id="picker-form" class="filters" aria-label="Подбор квеста" onsubmit="return false">
{select('age', 'Возраст', [('any', 'Любой'), ('k35', '3–4 года'), ('k57', '5–7 лет'), ('k810', '8–10 лет'), ('adult', 'Взрослые')])}
{select('occ', 'Повод', [('any', 'Любой повод'), ('bday', 'День рождения'), ('ny', 'Новый год'), ('gift', 'Вручить подарок'), ('sad', 'Утренник в детском саду')])}
{select('place', 'Где проводим', [('any', 'Где угодно'), ('home', 'Дома'), ('sad', 'В детском саду')])}
{select('group', 'Сколько детей', [('any', 'Неважно'), ('one', 'Один ребёнок'), ('many', 'Компания до 8'), ('group', 'Группа детского сада')])}
</form>
<div class="results-bar"><strong id="picker-count" aria-live="polite">Все квесты</strong><button type="button" class="link-btn" data-reset>Сбросить фильтры</button></div>
<div class="grid">
{cards}
</div>
<div class="empty" id="picker-empty" hidden>
<h3>Такого квеста пока нет</h3>
<p>Попробуйте изменить один из параметров. Новые квесты появляются каждую неделю.</p>
<button type="button" class="btn" data-reset>Показать все квесты</button>
</div>
</div>
</section>
"""


ICONS = {
    "cake": '<svg viewBox="0 0 52 52" fill="none" stroke="#2A1F3D" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 44h36M11 44V28h30v16"/><path d="M11 34c4 3 7 3 10 0s7-3 10 0 7 3 10 0"/><path d="M18 28v-7M26 28v-7M34 28v-7"/><path d="M18 17c-1.5-2 0-4 0-5 1.5 1 3 3 0 5zM26 17c-1.5-2 0-4 0-5 1.5 1 3 3 0 5zM34 17c-1.5-2 0-4 0-5 1.5 1 3 3 0 5z" fill="#F57F5F" stroke="none"/></svg>',
    "tree": '<svg viewBox="0 0 52 52" fill="none" stroke="#2A1F3D" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M26 6l8 12h-4l8 11h-5l9 11H10l9-11h-5l8-11h-4z"/><path d="M26 40v7"/><circle cx="22" cy="24" r="1.8" fill="#F57F5F" stroke="none"/><circle cx="31" cy="31" r="1.8" fill="#F6C544" stroke="none"/><circle cx="21" cy="35" r="1.8" fill="#3DB5A6" stroke="none"/><path d="M26 2l1.2 2.6L30 5l-2.2 1.8.6 2.8L26 8.2l-2.4 1.4.6-2.8L22 5l2.8-.4z" fill="#F6C544" stroke="none"/></svg>',
    "gift": '<svg viewBox="0 0 52 52" fill="none" stroke="#2A1F3D" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="22" width="34" height="22" rx="2"/><rect x="6" y="15" width="40" height="8" rx="2" fill="#F57F5F"/><path d="M26 15v29"/><path d="M26 15c-3-7-11-7-10-3 1 3 10 3 10 3s9 0 10-3c1-4-7-4-10 3z"/></svg>',
    "bell": '<svg viewBox="0 0 52 52" fill="none" stroke="#2A1F3D" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 36c3-3 3-8 3-13a9 9 0 0118 0c0 5 0 10 3 13z" fill="#F6C544"/><path d="M11 36h30"/><path d="M22 40a4 4 0 008 0"/><path d="M26 8v6"/><path d="M8 18l4 2M44 18l-4 2"/></svg>',
}

OCCASIONS = f"""<section class="section" aria-labelledby="occ-title">
<div class="wrap">
<div class="section-head"><div><h2 id="occ-title">Какой у вас праздник?</h2><p>Выберите повод — покажем подходящие квесты.</p></div></div>
<div class="occasions">
<a class="occ occ-bday" href="{{KV}}?povod=bday#picker">{ICONS['cake']}<strong>День рождения</strong><span>Квест для именинника и его друзей</span><span class="go">Выбрать →</span></a>
<a class="occ occ-ny" href="{{KV}}?povod=ny#picker">{ICONS['tree']}<strong>Новый год</strong><span>Подарки от Деда Мороза по подсказкам</span><span class="go">Выбрать →</span></a>
<a class="occ occ-gift" href="{{KV}}?povod=gift#picker">{ICONS['gift']}<strong>Вручить подарок</strong><span>Сюрприз, который нужно найти</span><span class="go">Выбрать →</span></a>
<a class="occ occ-sad" href="{{KV}}?povod=sad#picker">{ICONS['bell']}<strong>Детский сад</strong><span>Сценарий утренника для воспитателей</span><span class="go">Выбрать →</span></a>
</div>
</div>
</section>
"""

STEPS = """<section class="section" id="how" aria-labelledby="how-title">
<div class="wrap">
<div class="section-head"><h2 id="how-title">Как проходит праздник</h2></div>
<ol class="steps">
<li><div class="num"><span>01</span></div><strong>Получите файл</strong><p>Ссылка на PDF приходит на почту сразу после оплаты.</p></li>
<li><div class="num"><span>02</span></div><strong>Распечатайте</strong><p>Подойдёт обычный домашний принтер, даже чёрно-белый.</p></li>
<li><div class="num"><span>03</span></div><strong>Спрячьте карточки</strong><p>По готовой таблице: что куда положить. Подготовка — около 15 минут.</p></li>
<li><div class="num"><span>04</span></div><strong>Вручите первое письмо</strong><p>Дальше дети идут по подсказкам, а вы наблюдаете и помогаете.</p></li>
</ol>
</div>
</section>
"""

INSIDE = """<section class="section" style="padding-top:0" aria-labelledby="inside-title">
<div class="wrap">
<div class="inside confetti">
<div style="display:flex;flex-direction:column;gap:20px">
<h2 id="inside-title">Что внутри каждого квеста</h2>
<p class="lead">Всё, чтобы провести игру без импровизации в последний момент.</p>
</div>
<ul>
<li><strong>Письмо-завязка</strong><span>От героя истории — с него начинается игра</span></li>
<li><strong>Карточки-задания</strong><span>Загадки, шифры и задания на внимательность</span></li>
<li><strong>Таблица тайников</strong><span>Какую карточку куда спрятать</span></li>
<li><strong>Ответы и подсказки</strong><span>Если ребёнок застрял</span></li>
<li><strong>Инструкция взрослому</strong><span>Что подготовить и как начать</span></li>
<li><strong>Диплом</strong><span>Награда в конце игры</span></li>
</ul>
</div>
</div>
</section>
"""

FAQ_ITEMS = [
    ("Нужен ли цветной принтер?", "Нет. Все задания решаются и в чёрно-белой печати: ответы не зависят от цвета."),
    ("Как я получу файл?", "Сразу после оплаты на вашу почту придёт письмо со ссылкой на PDF. Если письма нет, проверьте папку «Спам» или напишите нам."),
    ("Что, если дома нет нужного тайника?", "В каждом квесте есть запасной вариант: «станция» — лист с названием предмета на коробке. Можно и вовсе не прятать карточки, а выдавать их по очереди за столом."),
    ("Можно играть компанией?", "Да. В описании каждого квеста указано, на сколько детей он рассчитан. В инструкции есть советы, как дать роль каждому."),
    ("Сколько времени занимает подготовка?", "Около 15–20 минут: распечатать, разрезать по пунктиру и разложить карточки по таблице."),
    ("Можно ли использовать квест несколько раз?", "Да, файл остаётся у вас. Распечатайте его снова для другого праздника. Передавать и перепродавать файл нельзя."),
]


def faq(items=FAQ_ITEMS):
    body = "\n".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in items)
    return f"""<section class="section" style="padding-top:0" aria-labelledby="faq-title">
<div class="wrap faq">
<h2 id="faq-title">Частые вопросы</h2>
<div>{body}</div>
</div>
</section>
"""


def faq_jsonld(items=FAQ_ITEMS):
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>\n"


# ---------- страницы ----------
def write(path, content):
    f = OUT / path / "index.html" if not path.endswith(".html") else OUT / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")


def home():
    d = 0
    hero_p = PRODUCTS[0]
    hero_img = link(d, hero_p["image"]) if hero_p.get("image") else ""
    out = head(d, "Территория праздника — готовые квесты для детей дома, распечатать PDF",
               "Готовые квесты для детей и сценарии праздников: день рождения, Новый год, поиск подарка, утренник в детском саду. Скачайте PDF, распечатайте и проведите праздник за 15 минут подготовки.",
               "", extra=faq_jsonld())
    out += header(d)
    art = {x["slug"]: link(d, x["image"]) for x in PRODUCTS if x.get("image")}
    out += f"""<section class="hero confetti">
<div class="wrap">
<div class="hero-text">
<span class="pill">Готовые квесты — распечатай и играй</span>
<h1>Праздник-приключение <span class="accent">без долгой подготовки</span></h1>
<p class="lead">Письмо от героя, карточки с заданиями, ответы и схема тайников — в одном файле. Вы раскладываете подсказки, а дети отправляются за подарком.</p>
<div class="hero-actions"><a class="btn" href="{link(d, '#picker')}">Подобрать квест</a><a class="btn btn-ghost" href="#how">Как это устроено</a></div>
<ul class="hero-facts"><li>Файл сразу после оплаты</li><li>Печать на обычном принтере</li><li>Ответы для взрослого</li></ul>
</div>
<div class="fan" aria-hidden="true">
<figure class="f1"><img src="{art['piratskiy-klad']}" alt="" width="600" height="750"></figure>
<figure class="f3"><img src="{art['gde-ded-moroz-spryatal-podarok']}" alt="" width="600" height="750"></figure>
<figure class="f2"><img src="{art['lisenok-iskrik']}" alt="" width="600" height="750"></figure>
<div class="sticker"><small>квесты</small><b>от 390 ₽</b></div>
</div>
</div>
</section>
<div class="bunting" aria-hidden="true"></div>
"""
    out += OCCASIONS.replace("{KV}", link(d, "kvesty/"))
    out += picker(d)
    out += STEPS + INSIDE + faq()
    out += footer(d)
    write("", out)


def catalog():
    d = 1
    out = head(d, "Все квесты для детей и сценарии праздников — Территория праздника",
               "Каталог готовых квестов для печати: день рождения, Новый год, поиск подарка, утренник в детском саду. Подберите квест по возрасту и поводу.",
               "kvesty/")
    out += header(d, "catalog")
    out += picker(d, "h1", "Все квесты и сценарии")
    out += STEPS
    out += footer(d)
    write("kvesty", out)


def product_page(p):
    d = 2
    path = f"kvesty/{p['slug']}/"
    og = p["image"] if p.get("image") else None
    ld = {
        "@context": "https://schema.org", "@type": "Product", "name": p["title"],
        "description": p["seo_desc"], "brand": {"@type": "Brand", "name": SITE_NAME},
        "offers": {"@type": "Offer", "price": str(p["price"]), "priceCurrency": "RUB",
                   "availability": "https://schema.org/InStock", "url": SITE_URL + "/" + path},
    }
    if p.get("image"):
        ld["image"] = SITE_URL + "/" + p["image"]
    extra = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>\n"
    out = head(d, p["seo_title"], p["seo_desc"], path, og_image=og, extra=extra)
    out += header(d)

    if p.get("pay_url"):
        buy = f'<a class="btn" href="{e(p["pay_url"])}">Купить за {fmt_price(p["price"])}</a>'
    else:
        buy = f'<a class="btn" aria-disabled="true" role="link">Оплата скоро</a>'
    kind = "Сценарий" if "sad" in p["f_place"] else "Квест"
    tasks_label = "Игры" if "sad" in p["f_place"] else "Заданий"
    facts = [("Возраст", p["ages"]), ("Участники", p["players"]), (tasks_label, str(p["tasks"])),
             ("Страниц в PDF", str(p["pages"])), ("Игра", p["play_time"]), ("Подготовка", p["prep_time"])]
    facts_html = "".join(f"<li><span>{e(k)}</span><strong>{e(v)}</strong></li>" for k, v in facts)
    story = "".join(f"<p>{e(s)}</p>" for s in p["story"])
    inside = "".join(f"<li><strong>{e(a)}</strong><span>{e(b)}</span></li>" for a, b in p["inside"])
    good = "".join(f"<li>{e(g)}</li>" for g in p["good_for"])
    note = f'<p class="notice">{e(p["note"])}</p>' if p.get("note") else ""
    previews = ""
    if p.get("previews"):
        figs = "".join(f'<figure><img src="{link(d, src)}" alt="Страница квеста «{e(p["short"])}», образец" loading="lazy" width="700" height="990"></figure>' for src in p["previews"])
        previews = f"""<section class="section" style="padding-top:0" aria-labelledby="pv-title"><div class="wrap">
<div class="section-head"><h2 id="pv-title">Как выглядят страницы</h2></div>
<div class="previews">{figs}</div>
</div></section>"""
    others = [o for o in PRODUCTS if o["slug"] != p["slug"]][:3]
    others_html = "\n".join(card(o, d) for o in others)

    out += f"""<div class="wrap">
<nav class="crumbs" aria-label="Навигация"><a href="{link(d, '')}">Главная</a> / <a href="{link(d, 'kvesty/')}">Все квесты</a> / {e(p['short'])}</nav>
<div class="product">
{cover(p, d, big=True)}
<div class="buy">
<span class="pill">{e(p['badge'])}</span>
<h1>{e(p['title'])}</h1>
<p class="lead">{e(p['lead'])}</p>
<ul class="facts">{facts_html}</ul>
<div class="buy-box"><span class="price">{fmt_price(p['price'])}</span>{buy}</div>
<p class="buy-note">PDF-файл придёт на почту сразу после оплаты. Печать на обычном принтере А4.</p>
</div>
</div>
</div>
<section class="section" style="padding-top:0"><div class="wrap two-col">
<div class="story"><h2>Как проходит {"праздник" if kind == "Сценарий" else "квест"}</h2>{story}</div>
<div class="story"><h2>Кому подойдёт</h2><ul class="checklist">{good}</ul>{note}</div>
</div></section>
{previews}
<section class="section" style="padding-top:0"><div class="wrap"><div class="inside confetti">
<div style="display:flex;flex-direction:column;gap:20px"><h2>Что в комплекте</h2><p class="lead">{kind} в одном PDF-файле. Можно распечатать сколько угодно раз для своих праздников.</p></div>
<ul>{inside}</ul>
</div></div></section>
"""
    out += faq()
    out += f"""<section class="section" style="padding-top:0"><div class="wrap">
<div class="section-head"><h2>Другие квесты</h2><a href="{link(d, 'kvesty/')}">Смотреть все</a></div>
<div class="grid">{others_html}</div>
</div></section>
"""
    out += footer(d)
    write(path.rstrip("/"), out)


# ---------- блог ----------
def load_posts():
    posts = []
    for f in sorted((SRC / "blog").glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        meta, body = {}, raw
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        if m:
            for line in m.group(1).splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
            body = m.group(2)
        if meta.get("draft") == "true":
            continue
        meta["slug"] = meta.get("slug") or f.stem
        meta["html"] = markdown.markdown(body, extensions=["extra"])
        posts.append(meta)
    posts.sort(key=lambda x: x.get("date", ""), reverse=True)
    return posts


def blog(posts):
    d = 1
    out = head(d, "Блог: идеи для детских праздников и квестов — Территория праздника",
               "Статьи о том, как провести квест дома, где спрятать подсказки, как необычно подарить подарок и устроить праздник без аниматора.",
               "blog/")
    out += header(d, "blog")
    if posts:
        items = "\n".join(f"""<a class="card-q" href="{link(d, 'blog/' + p['slug'] + '/')}"><div class="card-body"><span class="meta">{e(p.get('category', 'Идеи'))}</span><h3>{e(p['title'])}</h3><p>{e(p.get('description', ''))}</p><div class="card-foot"><span class="btn btn-sm">Читать</span></div></div></a>""" for p in posts)
    else:
        items = '<div class="empty"><h3>Первые статьи скоро появятся</h3><p>Пока загляните в каталог — там уже есть готовые квесты.</p><a class="btn" href="' + link(d, 'kvesty/') + '">Смотреть квесты</a></div>'
    out += f"""<section class="section"><div class="wrap">
<div class="section-head"><div><h1>Идеи для праздника</h1><p>Сценарии, тайники, игры и подарки — всё для домашнего праздника.</p></div></div>
<div class="grid">{items}</div>
</div></section>"""
    out += footer(d)
    write("blog", out)

    for p in posts:
        dd = 2
        path = f"blog/{p['slug']}/"
        out = head(dd, p["title"] + " — Территория праздника", p.get("description", ""), path)
        out += header(dd, "blog")
        out += f"""<div class="wrap"><article class="page">
<nav class="crumbs" aria-label="Навигация"><a href="{link(dd, '')}">Главная</a> / <a href="{link(dd, 'blog/')}">Блог</a></nav>
<h1>{e(p['title'])}</h1>
{p['html']}
</article></div>"""
        out += footer(dd)
        write(path.rstrip("/"), out)


# ---------- служебные страницы ----------
def text_page(path, title, desc, body):
    d = path.count("/") + 1
    out = head(d, title + " — Территория праздника", desc, path + "/")
    out += header(d)
    out += f'<div class="wrap"><article class="page"><h1>{e(title)}</h1>\n{body}\n</article></div>'
    out += footer(d)
    write(path, out)


def service_pages():
    todo = lambda t: f'<span class="todo">[{t}]</span>'
    text_page("oplata-i-poluchenie", "Оплата и получение",
              "Как оплатить и получить PDF-файл квеста.",
              f"""<p>Все товары магазина — электронные файлы в формате PDF. Физические товары мы не отправляем.</p>
<h2>Как оплатить</h2>
<p>Нажмите «Купить» на странице квеста. Откроется защищённая страница оплаты сервиса Продамус. Можно оплатить банковской картой или через СБП.</p>
<h2>Как получить файл</h2>
<p>Сразу после оплаты на почту, указанную при покупке, придёт письмо со ссылкой на PDF. Обычно это занимает 1–2 минуты. Если письма нет, проверьте папку «Спам».</p>
<h2>Если что-то пошло не так</h2>
<p>Напишите нам на {MAIL} и укажите почту, на которую оформляли заказ. Мы ответим и отправим файл вручную.</p>""")
    text_page("oferta", "Публичная оферта", "Договор-оферта на продажу электронных файлов.",
              f"<p>Текст оферты готовится и появится до начала продаж. {todo('ДЕНЬ 4 ПЛАНА: вставить оферту')}</p>")
    text_page("politika-konfidencialnosti", "Политика конфиденциальности", "Как мы обрабатываем персональные данные.",
              f"<p>Текст политики готовится и появится до начала продаж. {todo('ДЕНЬ 4 ПЛАНА: вставить политику')}</p>")
    text_page("kontakty", "Контакты", "Как связаться с магазином «Территория праздника».",
              f"""<p>Почта для вопросов о заказах: {MAIL}</p>
<p>Продавец: {todo('ФИО, статус: самозанятая / ИП')}, ИНН {todo('ИНН')}</p>
<p>Отвечаем в течение дня.</p>""")
    text_page("spasibo", "Спасибо за покупку!", "Заказ оплачен.",
              f"""<p>Оплата прошла. Письмо со ссылкой на PDF уже летит на вашу почту — обычно это 1–2 минуты.</p>
<p>Не видите письма? Проверьте папку «Спам». Если его нет и там, напишите на {MAIL}.</p>
<p><a class="btn" href="{link(1, 'kvesty/')}">Смотреть другие квесты</a></p>""")

    # 404
    d = 0
    out = head(d, "Страница не найдена — Территория праздника", "Такой страницы нет.", "404.html")
    out += header(d)
    out += f'<div class="wrap"><article class="page"><h1>Такой страницы нет</h1><p>Возможно, квест переехал. Загляните в каталог.</p><p style="margin-top:20px"><a class="btn" href="{link(d, "kvesty/")}">Все квесты</a></p></article></div>'
    out += footer(d)
    # 404 открывается по любому адресу — ссылки делаем от корня
    out = out.replace('href="kvesty/', 'href="/kvesty/').replace('href="css/', 'href="/css/').replace('src="js/', 'src="/js/').replace('href="blog/', 'href="/blog/').replace('href="favicon', 'href="/favicon')
    write("404.html", out)


def seo_files(posts):
    urls = ["", "kvesty/"] + [f"kvesty/{p['slug']}/" for p in PRODUCTS] + ["blog/"] + [f"blog/{p['slug']}/" for p in posts] + \
           ["oplata-i-poluchenie/", "oferta/", "politika-konfidencialnosti/", "kontakty/"]
    today = date.today().isoformat()
    body = "\n".join(f"<url><loc>{SITE_URL}/{u}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nDisallow: /spasibo/\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    (OUT / "favicon.svg").write_text(LOGO.replace(' aria-hidden="true"', ' xmlns="http://www.w3.org/2000/svg"'), encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "static", OUT)
    posts = load_posts()
    home()
    catalog()
    for p in PRODUCTS:
        product_page(p)
    blog(posts)
    service_pages()
    seo_files(posts)
    print(f"Готово: {OUT} ({len(PRODUCTS)} товаров, {len(posts)} статей)")


if __name__ == "__main__":
    main()
