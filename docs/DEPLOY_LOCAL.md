# Запуск у себя

1. Python 3.14, Node 24.
2. `cd backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt`
3. `.env.example` скопировать в `backend/.env`, положить BOT_TOKEN (токен только локально, в git его нет).
4. `python create_db.py; python seed.py` — база и демо-данные.
5. `..\.venv\Scripts\python -m pytest tests -q` — должны быть все зелёные.
6. `..\.venv\Scripts\python -m uvicorn app.main:app --port 8000` (из папки backend).
7. Фронт: `cd frontend; npm install; npm run dev`.
8. Mini App в Telegram — через туннель (ngrok/Tailscale) + setdomain у BotFather.
