# 02 — Архитектура

## Монорепо

```
HRXWarehouse/
├── backend/               # FastAPI + SQLite
│   ├── app/
│   │   ├── core/          # config (.env), db (WAL), security (initData), limits (лимиты), logging
│   │   ├── models/        # tables.py (18 таблиц), __init__.py (экспорт)
│   │   ├── schemas/       # pydantic: receipt, assemble, moves
│   │   ├── services/      # receipt, assemble, moves+уведомления, reports
│   │   ├── routers/       # deps, receipt, assemble, moves, admin, photos, folders, stats, catalog, favorites, extra
│   │   └── main.py        # приложение + раздача frontend/dist
│   ├── alembic/ + versions/ # 0001_init, 0002_photos, 0003_catalog, 0004_favs, 0005_low_notified
│   ├── tests/             # 9 файлов, 29 тестов
│   ├── create_db.py seed.py seed_catalog.py
│   └── requirements.txt   # fastapi, uvicorn, sqlalchemy, aiosqlite, alembic, pydantic, qrcode, openpyxl, httpx, pytest, Pillow
├── frontend/              # React 18 + TS + Vite 6
│   ├── public/logo.png    # логотип с gidrobot.ru
│   └── src/               # App, theme, api/client, components (StdPicker, FavStar), pages (12 штук)
├── knowledge/           # ЭТА ПАПКА: база знаний для LLM, в git не пушится
├── docs/                # короткие рабочие доки (тоже в репо)
├── uploads/             # документы и фото, только локально
└── README.md .env.example .gitignore
```

## Потоки данных

```
Телефон (Telegram WebView)
  │  initData в заголовке X-Telegram-Init-Data
  ▼
HTTPS (ngrok сейчас / Caddy потом) → Uvicorn :8000
  │  RateLimit → deps (кто ты, твои роли) → router → service
  ▼
SQLite (WAL) ←→ SQLAlchemy async. Фото/доки — файлы в uploads/, в базе только пути.
  │  Порог упал → Bot API → закупщикам + админу в личку
```

Фронт собранный (`dist`) раздаётся тем же бэком с `/` — одно origin, CORS не нужен. API — относительные `/api/...`.
Телеге нужен публичный HTTPS: localhost она не видит. Сейчас — ngrok-туннель, адрес в BotFather (`/myapps` → URL).

## Решения и почему так

| Решение | Почему | Чем рискуем |
|---|---|---|
| Остаток одним числом, без партий | по деталям всё равно непонятно как давно заказали; проще и честно | не узнаем возраст остатка |
| Папки ≠ составы | где лежит и из чего состоит — разные вещи, иначе рекурсия | надо держать оба дерева в голове |
| Единый items + kind | деталь/стандарт/подсборка/изделие в одной таблице, BOM любой глубины | нужна защита от колец (есть) |
| Умная сборка Б (предлагать, не собирать) | избегаем «сборки на бумаге»: пока физически не собрано — не списываем | лишний тап на дособор |
| Частичная сборка запрещена | иначе учёт расползётся | вернёмся позже (см. главу 10) |
| Химия-пометка | жидкость не посчитать, только «используется» | тюбики считаем руками |
| Два журнала | движения (склад) и аудит (люди) — разные вопросы, разные таблицы | — |
| Порог в items, кому слать — по ролям | один источник правды вместо двух таблиц порогов | — |
| Мультрироли | worker+purchaser у одного человека — бывает | матрица шире |
| Счёт не уникален | повтор при доработке с тем же счётом | нельзя искать поставку только по счёту |
| QR отложены | решили сначала наладить ручной учёт | поля-заделы уже есть |
| SQLite WAL | 200 позиций, один сервер — хватает за глаза | при росте — PostgreSQL (см. главу 10) |
| DEV выключен в репо | прод закрыт по умолчанию, локалка открывается своим .env | новички спотыкаются (описано в 08) |
| knowledge/ вне гита | секреты и внутренняя кухня не должны утекать | доки могут разъехаться с кодом — обновляем вместе |

## Стек подробно

Бэк: Python 3.14, FastAPI 0.162, SQLAlchemy 2.1 (async), aiosqlite, Alembic 1.20, Pydantic 2 + pydantic-settings, python-multipart (файлы), qrcode (задел), openpyxl (Excel), httpx (Bot API + тесты), Pillow (ресайз фото), pytest + pytest-asyncio.
Фронт: React 18.3, TypeScript 5.5, Vite 6.4, @vitejs/plugin-react 4.7. Telegram WebApp SDK через CDN (`telegram-web-app.js`), сканер в будущем — `@yudiel/react-qr-scanner` (не ставим пока).
Инфра сейчас: uvicorn на 127.0.0.1:8000 (запуск СТРОГО из папки backend, иначе dist не найдётся), ngrok 3.39 (свежий бинарь в `.tools/`, winget даёт древний 3.3), BotFather URL.
Инфра потом: Caddy 443 (LE) → 127.0.0.1:8000 через NSSM, белый IP, домен. Самоподписанные телега не ест.

## История по коммитам (коротко)

- Скелет → шаг 1 база+сиды → шаг 2 приёмка+остатки → шаг 3 сборка → шаг 4 движения+пороги → шаг 5 отчёты+админка.
- Фикс запуска фронта (плагин реакта). Туннель: cloudflared QUIC не прошёл → http2 → ngrok (старый бинарь → свежий).
- Редизайн в стиле телеги + фотки + каталог + избранное + виджеты → прод-версия (чёлка, безопасность, лимиты).
- Полная история: `git log --oneline` в репо, всё по-русски.

