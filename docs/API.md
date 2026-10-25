# API

Заголовок везде: `X-Telegram-Init-Data`. Ошибки русским текстом.

- `GET /api/health` — живой или нет.
- `POST /api/supplies` — приёмка. Повтор sku = плюс к остатку.
- `GET /api/supplies` — список поставок.
- `POST /api/supplies/{id}/docs?dtype=upd|invoice|transport|other` — файл до 10 МБ.
- `GET /api/supplies/{id}/docs`, `GET /api/docs/{id}/download` — список и скачивание.
- `GET /api/stock?q=&folder_id=&low_only=` — остатки.
- `GET /api/products`, `GET /api/products/{id}/bom` — что собираем и состав.
- `POST /api/assemble/check`, `POST /api/assemble` — проверка и сборка (qty, order_id=null значит на склад).
- `POST /api/scrap`, `/api/unscrap` — брак (причина обязательна) и возврат.
- `GET /api/projects`, `POST /api/projects` (admin) — проекты.
- `POST /api/to-project`, `/api/chem-out` — выдача в проект и списание тюбика.
- `POST /api/items/{id}/threshold` (admin) — порог и галочка.
- `GET /api/moves?date_from=&date_to=&mtype=` — движения.
- `GET /api/audit` (admin) — журнал действий.
- `GET /api/report/excel?date_from=&date_to=` — Excel (Остатки + Движения).
- `GET /api/users`, `POST /api/users/{id}/activate`, `POST /api/users/{id}/block` (admin) — люди.
- `GET /api/orders`, `POST /api/orders` — заказы.
