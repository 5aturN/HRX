# 08 — Деплой и работа

## Локалка (разработка)

Нужно: Python 3.14, Node 24, Git.

```powershell
cd D:\РАБОТА\HRX\HRXWarehouse\backend
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# .env.example → backend/.env, положить BOT_TOKEN, DEV_ALLOW_UNAUTH=1
python create_db.py; python seed.py; python seed_catalog.py
..\.venv\Scripts\python -m pytest tests -q   # 29/29 в 9 файлах
..\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000  # ИЗ ПАПКИ backend!
```
Фронт: `cd frontend`, `npm.cmd install`, `npm.cmd run dev` (5173) или `npm.cmd run build` (dist для бэка).
ВАЖНО: бэк запускать из папки backend (путь к dist относительный). Порт занят (10048) — старый процесс висит: `Stop-Process -Id <pid> -Force` (узнать: `Get-NetTCPConnection -LocalPort 8000`).
npm через `npm.cmd`: обычный `npm` (ps1) режется ExecutionPolicy. Лечится разово: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` (админ).

## Туннель (как работает сейчас)

Телега не видит localhost — нужен публичный HTTPS. Сейчас: свежий ngrok 3.39 (`D:\РАБОТА\HRX\HRXWarehouse\.tools\ngrok.exe http 8000`, winget даёт древний 3.3 — не брать). Адрес `*.ngrok-free.app` → BotFather `/myapps` → URL. Проверка: `/api/health` → ok, `/api/ready` → ok (200) или 503 при мёртвой базе, `/` → склад. loca.lt просит пароль, ngrok — страницу Visit Site (разово).
История: cloudflared QUIC резался провайдером → `--protocol http2` помог → потом control stream отвалился → ушли на ngrok. Акк ngrok требует агент ≥3.20. Адрес меняется при перезапуске — обновлять в BotFather.

## Сервер (переезд с туннеля)

Windows Server: Python 3.14, Node 24 (только для сборки), Caddy (авто-HTTPS LE) → 127.0.0.1:8000 (uvicorn через NSSM). SQLite WAL. Наружу только 443, 8000 не открывать. Нужны домен + белый IP. Самоподписанные нельзя. Токен — в `.env` на сервере. Миграции + сид каталога при переезде.

## Прод-чеклист

- [ ] Боевой BOT_TOKEN в `.env`, DEV_ALLOW_UNAUTH=0. Старый засвеченный отозван (`/revoke` в BotFather).
- [ ] `alembic upgrade head` + `seed_catalog.py` + фото эталонов залиты.
- [ ] `pytest` 29/29 в 9 файлах, `tsc` чистый, `dist` собран.
- [ ] Контейнеров нет (проверено: Dockerfile.backend/frontend, docker-compose.yml, Caddyfile, CI, backup.py в репо отсутствуют) — деплой без контейнеров: uvicorn через NSSM + Caddy вручную; бэкап — ручная копия `hrx.db` + `uploads/` (каталог `BACKUP_DIR` создаёт lifespan, скрипта нет); `.env.example` минимальный (BOT_TOKEN, DATABASE_URL, DEV_ALLOW_UNAUTH, UPLOAD_DIR, MAX_UPLOAD_MB), остальное — дефолты `config.py`.
- [ ] Дыры из главы 07 закрыты (минимум: pending читать запретить, Excel без токена в URL).
- [ ] Бэкап hrx.db раз в день + копия uploads.
- [ ] Caddy + домен, проверка из Телеги с двух телефонов (Android/iOS).

## Грабли (все, на которые наступали)

1. «Фронт не собран» — бэк запущен не из backend. 2. Порт 8000 занят — висит старый python. 3. `npm` не запускается — брать `npm.cmd`. 4. tsc сыплет .js — `noEmit: true` уже стоит. 5. Плагин реакта vs Vite: свежий plugin-react 6 хочет Vite 8, у нас Vite 6 → plugin-react 4.7. 6. winget ngrok древний → качать с сайта. 7. Токен в .env.example — вычищен, но отозвать. 8. `tail` нет в Windows — `Select-Object -Last`. 9. `cat <<EOF` нет — писать файлы через node. 10. apply_patch в этой среде не работает — файлы пишем скриптами/командами.

