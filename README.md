# Территория праздника — сайт

Магазин готовых квестов для печати: https://territoriaprazdnika.ru

**Полная карта проекта (сервер, домен, как обновлять, что делать если что-то сломалось): [INSTRUKCIYA.md](INSTRUKCIYA.md)**

## Как устроено

- `src/data/products.json` — все товары: названия, цены, описания, ссылки на оплату (`pay_url`).
- `src/blog/*.md` — статьи блога (Markdown с шапкой `title`, `description`, `date`, `category`).
- `src/static/` — стили, скрипт подбора квеста, картинки.
- `build.py` — собирает сайт в папку `public/`. Её и выкладываем на хостинг.

## Сборка

```
pip install markdown
python3 build.py             # public/  — для хостинга
python3 build.py --preview   # preview/ — открыть локально без сервера
```

## Добавить квест

1. Добавить запись в `src/data/products.json`.
2. Картинки положить в `src/static/img/<slug>/`.
3. Запустить `python3 build.py` и закоммитить.
