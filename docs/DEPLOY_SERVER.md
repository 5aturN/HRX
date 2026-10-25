# Рабочий сервер (Windows Server)

Caddy :443 (Let's Encrypt, публичный домен) -> 127.0.0.1:8000 (uvicorn как сервис через NSSM).
SQLite WAL. Порт 8000 наружу не открывать. Самоподписанный не использовать.
Контейнеров в репо нет (Dockerfile/compose/Caddyfile/CI отсутствуют) — ставим вручную: Caddy + NSSM, без compose.
На сервере: `alembic upgrade head` (0001..0005_low_notified) + `seed_catalog.py`; проверка `GET /api/ready` (200 — база жива).
Бэкап: скрипта нет — ручная копия `hrx.db*` + `uploads/` раз в день (каталог `BACKUP_DIR` создаёт lifespan).
