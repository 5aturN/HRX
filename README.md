# Склад Гидробот

![Логотип](docs/img/logo.png)

Telegram Mini App для склада. Приёмка, остатки, сборка по составу, заказы, брак и возвраты, R&D, отчёты в Excel.

## Запуск

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# .env.example скопировать в backend/.env, положить BOT_TOKEN (только локально, в git его нет)
python create_db.py
python seed.py
..\.venv\Scripts\python -m pytest tests -q
..\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000  # из папки backend!
```

Фронт: `cd frontend`, `npm install`, `npm run dev` (разработка) или `npm run build` (собранное в `dist` раздаёт бэк).
В телеге: светим бэк туннелем (ngrok) или доменом, адрес вставляем в BotFather. Подробности — в доках.

## Документация

Вся техдокументация — в [`docs/`](docs/README.md): обзор, база, бэк, фронт и дизайн, API, деплой, тесты, планы. Обновляю её вместе с кодом.

## Проверки

- Бэк: `pytest tests -q` (16 тестов).
- Фронт: `npx tsc --noEmit`, `npm run build`.
