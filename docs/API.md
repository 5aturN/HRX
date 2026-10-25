# API

Заголовок везде: `X-Telegram-Init-Data`. Ошибки русским текстом.

- `GET /api/health` — живой или нет.
- `POST /api/supplies` — приёмка. Тело: шапка (поставщик, УПД, счёт, дата, stock|project) + строки (detail|standard, sku, название, децимальный для деталей, папка, кол-во). Повтор sku = плюс к остатку.
- `GET /api/supplies` — список поставок, свежие сверху.
- `POST /api/supplies/{id}/docs?dtype=upd|invoice|transport|other` — прикрепить файл (до 10 МБ).
- `GET /api/supplies/{id}/docs` — документы поставки.
- `GET /api/docs/{id}/download` — скачать файл.
- `GET /api/stock?q=...&folder_id=..&low_only=true` — остатки: артикул, название, децимальный, папка, остаток, порог, нехватка.
