# 05 — API

Заголовок везде: `X-Telegram-Init-Data`. Ошибки русским текстом.

| Метод и путь | Что делает |
|---|---|
| `GET /api/health` | Живой или нет. |
| `POST /api/supplies` | Приёмка (шапка + строки). |
| `GET /api/supplies` | Список поставок. |
| `POST /api/supplies/{id}/docs?dtype=` | Файл до 10 МБ (`upd \| invoice \| transport \| other`). |
| `GET /api/supplies/{id}/docs` | Документы поставки. |
| `GET /api/docs/{id}/download` | Скачать файл. |
| `GET /api/stock?q=&folder_id=&low_only=` | Остатки. |
| `GET /api/products`, `GET /api/products/{id}/bom` | Что собираем и состав. |
| `POST /api/assemble/check`, `POST /api/assemble` | Проверка и сборка (`qty`, `order_id=null` — на склад). |
| `POST /api/scrap`, `/api/unscrap` | Брак (причина обязательна) и возврат. |
| `GET /api/projects`, `POST /api/projects` | Проекты (создаёт админ). |
| `POST /api/to-project`, `/api/chem-out` | Выдача в проект, списание тюбика. |
| `POST /api/items/{id}/threshold` | Порог и галочка (админ). |
| `GET /api/moves?date_from=&date_to=&mtype=` | Движения. |
| `GET /api/audit` | Журнал действий (админ). |
| `GET /api/report/excel?date_from=&date_to=` | Excel: Остатки + Движения. |
| `GET /api/users`, `POST /api/users/{id}/activate`, `POST /api/users/{id}/block` | Люди (админ). |
| `GET /api/orders`, `POST /api/orders` | Заказы. |

Фото и кабинет: `POST /api/items/{id}/photo`, `GET /api/items/{id}/photo`, `POST /api/me/avatar`, `GET /api/users/{id}/avatar`, `GET /api/me`, `GET /api/folders/tree`, `GET /api/stats`.
