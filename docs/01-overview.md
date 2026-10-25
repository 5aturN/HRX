# 01 — Обзор и запуск

## Что это

Склад производственного предприятия внутри Telegram. Приёмка, остатки, сборка по составу, заказы, брак и возвраты, R&D, отчёты в Excel, люди и права.

## Как устроено

- Остаток живёт в `items.qty` (общая масса). Поставки — только история приходов.
- Папки — где лежит. Сборки (BOM) — из чего состоит. Это разные вещи.
- Химия в составе — только пометка, в сборку не списывается. Тюбики считаются руками.
- Сборка без заказа — `order_id = NULL` (пункт «Просто на склад»).
- Два журнала: `stock_moves` (движения) и `audit_log` (действия людей).

## Запуск у себя

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# .env.example скопировать в backend/.env, положить BOT_TOKEN (только локально)
python create_db.py
python seed.py
..\.venv\Scripts\python -m pytest tests -q
..\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Фронт отдельно (для разработки):

```powershell
cd frontend
npm install
npm run dev   # http://localhost:5173
npm run build # собранное в dist, бэк его раздаёт
```

## Вход через Telegram

Каждый запрос несёт `X-Telegram-Init-Data`. Бэк проверяет подпись по BOT_TOKEN. Вне телеги работает `DEV_ALLOW_UNAUTH=1` (только для разработки).
