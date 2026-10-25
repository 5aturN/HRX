# Склад Гидробот

![Логотип](docs/img/logo.png)

Telegram Mini App для склада производственного предприятия. Один репозиторий, один адрес: бэкенд на FastAPI раздаёт собранный фронтенд.

Приёмка, остатки, умная сборка по составу, заказы, брак и возвраты, выдача в R&D, пороги с уведомлениями без спама, отчёты в Excel, каталог DIN/ISO/ГОСТ с фото, избранное у каждого своё.

## Быстрый старт (локально)

Нужно: Python 3.14, Node 24, Git.

```powershell
cd backend
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# .env.example скопировать в backend/.env (или в корень .env), положить BOT_TOKEN
python create_db.py; python seed.py
..\.venv\Scripts\python -m pytest tests -q   # 29 тестов в 9 файлах
..\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000  # запускать из папки backend!
```

Фронтенд:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev      # разработка на :5173
npm.cmd run build    # собранное в dist раздаёт бэкенд
```

Проверки живости: `/api/health` — процесс жив, `/api/ready` — жива и база (200) либо 503.

## Прод через Docker Compose

```powershell
cp .env.example .env   # заполнить BOT_TOKEN и POSTGRES_PASSWORD
docker compose up --build
curl http://localhost:8000/api/ready
```

Состав: `api` (FastAPI + uvicorn, миграции `alembic upgrade head` при старте) и `db` (PostgreSQL 16). Файлы, бэкапы и логи живут в именованных томах. Поверх — `Caddyfile` с авто-HTTPS. Ночной бэкап: `python backend/scripts/backup.py` (база + uploads, хранит 7 копий).

## Проверки

| Что | Как |
|---|---|
| Бэкенд | `python -m pytest backend/tests -q` — 29 прошли |
| Линтер | `python -m ruff check backend/app backend/tests` |
| Аудит | `python -m pip_audit` — уязвимостей нет |
| Фронтенд | `npm run build` (внутри `tsc` + `vite build`) |
| CI | `.github/workflows/ci.yml` — тесты, линт, сборка |

## Документация

Коротко — в [`docs/`](docs/README.md): обзор, база, бэкенд, фронт, API, деплой, тесты, дорожная карта. Подробно, рядом с кодом — в `knowledge/` (главы 00–10).

## Лицензия

MIT, см. [LICENSE](LICENSE).
