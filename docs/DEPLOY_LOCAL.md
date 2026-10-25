# Локальный стенд (тесты на личном компе)

1. Python 3.14, Node 24.
2. `cd backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt`
3. Скопировать `.env.example` -> `backend/.env`, положить BOT_TOKEN локально.
4. `uvicorn app.main:app --reload --port 8000` (запуск из папки backend).
5. `cd frontend; npm install; npm run dev`.
6. Полный тест Mini App в Telegram — через туннель (ngrok/Tailscale) + setdomain у BotFather.
