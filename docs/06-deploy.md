# 06 — Деплой

## Тест через туннель (сейчас так и работает)

Телега не умеет в `localhost`, ей нужен публичный HTTPS. Поэтому бэк с собранным фронтом светим наружу.

```powershell
cd backend
..\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000  # запускать из папки backend!
D:\РАБОТА\HRX\HRXWarehouse\.tools\ngrok.exe http 8000
```

Адрес `https://....ngrok-free.app` вставить в BotFather: `/myapps` → app → Edit → URL. Адрес меняется при перезапуске — обновлять там же.
Проверка: `/api/health` → `ok:true`, `/` → склад. QUIC у части провайдеров режется — у cloudflared тогда `--protocol http2`, либо ngrok.

## Рабочий сервер (когда переезжаем с туннеля)

- Windows Server, Python 3.14, Node 24.
- Caddy на 443 с авто-HTTPS от Let's Encrypt → `127.0.0.1:8000` (uvicorn как сервис через NSSM).
- SQLite в WAL. Порт 8000 наружу не открывать, только 443. Нужны публичный домен и белый IP.
- Самоподписанные сертификаты не подойдут — телега их не ест.
- Токен бота — только в локальном `.env` на сервере, в git его нет.

## Прод-чеклист

- [ ] BOT_TOKEN боевой в `.env` на сервере, DEV_ALLOW_UNAUTH=0 (в репо DEV выключен по умолчанию, локалка включается своим `.env`).
- [ ] `alembic upgrade head`, `seed_catalog.py`.
- [ ] Caddy 443 → 127.0.0.1:8000, белый IP, домен. Самоподписанные нельзя.
- [ ] Токен из переписки отозван через BotFather.
- [ ] `pytest` 29/29 в 9 файлах, `tsc` чистый, `dist` собран.
- [ ] `alembic upgrade head` (0001..0005_low_notified) + `seed_catalog.py` + фото эталонов.
- [ ] Контейнеров в репо нет (Dockerfile.backend/frontend, compose, Caddyfile, CI, backup.py отсутствуют): деплой без контейнеров — uvicorn через NSSM + Caddy вручную; бэкап — ручная копия `hrx.db` + `uploads/` (`BACKUP_DIR` создаёт lifespan, скрипта нет).
