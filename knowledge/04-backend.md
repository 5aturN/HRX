# 04 — Бэкенд

FastAPI, всё асинхронное. Ошибки русским текстом (HTTPException с detail), логи INFO (операции) / ERROR (ошибки) через logging.
Точка входа `app/main.py`: приложение (docs_url=None — Swagger закрыт), lifespan (создаёт uploads/backups/logs, на выходе закрывает пул БД), RateLimit-middleware, 10 роутеров, `/api/health` + `/api/ready` (503 если база мертва), раздача `frontend/dist` с `/` (если dist нет — заглушка «не собран»).
Запуск СТРОГО из папки backend, иначе dist не найдётся (известные грабли, см. главу 08).

## core/

- `config.py`: Settings из `.env` (BOT_TOKEN, DATABASE_URL, DEV_ALLOW_UNAUTH=False по умолчанию!, UPLOAD_DIR, BACKUP_DIR, MAX_UPLOAD_MB=10, MAX_IMAGE_PIXELS=40 млн, RATE_LIMIT_PER_MIN=120, TELEGRAM_NOTIFY_TIMEOUT=10, LOG_LEVEL/LOG_DIR). В репо DEV выключен, локалка открывается своим `.env`.
- `db.py`: engine (SQLite локально / PostgreSQL в проде через asyncpg-пул) + SessionLocal + `get_session`, PRAGMA WAL + foreign_keys=ON + busy_timeout (SQLite) или statement_timeout 15с (PostgreSQL), `check_db` (для /api/ready), `dispose_engine` (закрытие пула), Base.
- `security.py`: `check_init_data` — подпись HMAC (WebAppData + токен), свежесть auth_date (не старше суток), DEV-режим только при флаге. Без токена — отказ.
- `limits.py`: RateLimit — не больше N/мин с IP на `/api/*` (429 + русская ошибка, health/ready вне лимита, чистка старых записей), заголовки nosniff/DENY/no-referrer/Permissions-Policy/COOP на все ответы.
- `logging_conf.py`: `setup_logging(level, log_dir)` — консоль + RotatingFileHandler (5 МБ × 5), формат «время | уровень | имя | сообщение».

## models/, schemas/

Модели — глава 03. Схемы pydantic: `receipt.py` (NewItemIn: kind/detail/standard, имя можно пустое — подставится из каталога, std_code; SupplyCreate: шапка + строки; StockRow: +has_photo +std_code), `assemble.py` (MissingRow с build_subassembly, AssembleCheck can/missing/need_subassemblies, AssembleDo product/qty≤100/order_id), `moves.py` (MoveDo item/qty/reason/project, ThresholdDo).

## services/receipt.py — приёмка

`create_supply(session, data, user_id)`: проверяет target/project, создаёт Supply, по строкам — ищет StdCatalog по std_code (верхний регистр), ищет Item по sku. Нет — создаёт (имя пустое → из каталога → иначе sku; фото из каталога если есть). Есть — приклеивает std_code/фото если не было. Проверяет kind (нельзя тот же артикул другим типом) и децимальный у деталей. Плюсует qty, пишет SupplyItem + StockMove (prihod/vydacha_rd) + AuditLog(priemka). Одна транзакция (commit в конце). Ошибки — ValueError с русским текстом.

## services/assemble.py — сборка

`_children`: строки состава. `_expand(item, qty, seen)`: рекурсия до листьев (detail/standard), кольцо → ValueError «Кольцо в составе». Химию только логирует (не списывает).
`check_assemble(product, qty)`: для каждого ребёнка — если подсборка и её не хватает: смотрим можно ли дособрать (листья), не хватает листьев → missing с build_subassembly; детали/стандарты — просто хватает/нет. Дубли складываем (max). Возвращает can + missing + need_subassemblies. Ничего не пишет.
`do_assemble(product, qty, order, user)`: сначала check (нельзя → ValueError со списком), заказ проверяем (нет/отгружен → отказ), версия = max строк. По строкам: не хватает (пока проверяли разобрали) → отказ; минусуем child, пишем StockMove (sborka/sborka_podsborki), плюсуем изделие (oprihod_podsborki), двигаем OrderItem, пишем AuditLog(sborka). Commit. Возвращаем low (что ниже порога — уведомления шлёт moves/шаг сборки, тут только список).

## services/moves.py — движения и уведомления

`_get`, `_low_list` (кто ниже порога). `notify_low(items, session)`: пусто → 0; нет токена → в лог; есть → всем purchaser/admin (кроме tg 1,2) шлём «Склад: ниже порога» (httpx, таймаут TELEGRAM_NOTIFY_TIMEOUT), при успехе ставим low_notified и коммитим. `_low_list` отбирает только тех, о ком ещё не писали. Приёмка сбрасывает флаг при пополнении.
`scrap`: причина обязательна, хватает → минус, StockMove(brak) + AuditLog, commit, notify. `unscrap`: плюс, vozvrat. `to_project`: проект должен быть rnd_project, хватает → минус + vydacha_rd с меткой. `chem_out`: минус + brak «Тюбик выброшен» + notify. Все ошибки — ValueError по-русски.

## services/reports.py — Excel

`build_excel(session, from, to)`: openpyxl. Лист «Остатки»: Артикул, Наименование, Децимальный, Папка, Остаток, Порог, Статус (Ниже порога/ОК), ширина 22. Лист «Движения»: Дата (дд.мм.гггг чч:мм), Тип (русский из MTYPE_RU), Артикул, Наименование, Кол-во, Причина, Инициатор, Заказ («на склад» если NULL). Фильтр по датам в питоне, лимит 5000. Возвращает байты.

## routers/ — все 43 эндпоинта

Заголовок везде `X-Telegram-Init-Data`. `deps.py`: `current_user` (проверка → найти/создать pending → blocked отказ), `user_roles`, `need_roles(*)` (admin везде).

`receipt.py` (склад): POST /api/supplies (worker) — приёмка; GET /api/supplies — 200 свежих с подсчётом позиций/штук; POST /api/supplies/{id}/docs?dtype= (worker) — файл, проверка типа/размера/пустоты, сейф-имя, AuditLog; GET .../docs — список; GET /api/docs/{id}/download — файл; GET /api/stock (q/folder_id/low_only, лимит 500) — поиск по sku/имени/децимальному/артикулу поставщика, low, has_photo/std_code.

`assemble.py` (сборка): GET /api/products — изделия+подсборки (+has_photo); GET /api/products/{id}/bom — состав (need/have/ok/has_photo) + химия (id/name/note/has_photo); POST /api/assemble/check — проверка; POST /api/assemble (worker) — сборка.

`moves.py` (движения): POST /api/scrap, /api/unscrap, GET /api/projects, POST /api/projects (admin, нужна корневая R&D), POST /api/to-project, POST /api/chem-out (всё worker), POST /api/items/{id}/threshold (admin).

`admin.py` (отчёты/люди/заказы): GET /api/moves (фильтры дата/тип, лимит 1000), GET /api/audit (admin, 1000), GET /api/report/excel (файл sklad.xlsx), GET /api/users (admin, +роли), POST /api/users/{id}/activate (admin: ФИО/должность/роли, status active, старые роли стираем), POST /api/users/{id}/block (admin), GET /api/orders (покупатель + строки), POST /api/orders (worker: покупатель, строки только изделия), POST /api/orders/{id}/status (worker: new/work/done/shipped).

`photos.py` (фото): POST /api/items/{id}/photo (worker, проверка пикселей MAX_IMAGE_PIXELS, ресайз 800 JPEG 82, старое затираем, ValueError → 400 с текстом), GET /api/items/{id}/photo (своё → эталонное → 404), POST /api/me/avatar (ресайз 256), GET /api/users/{id}/avatar, GET /api/me (профиль + роли + движения за неделю + has_avatar). `_save_img`: RGB, thumbnail, JPEG.

`folders.py`: GET /api/folders/tree — всё дерево с подсчётом позиций/штук снизу вверх, флаг фото, русские типы. `stats.py`: GET /api/stats — всего позиций/штук/ниже порога + топ-10. `catalog.py`: см. главу 06. `favorites.py`: GET /api/favorites (моё), POST /api/favorites/{id} (тумблер). `extra.py`: GET /api/recent (20 последних), GET /api/items/{id}/label (HTML-этикетка для печати, задел qr:id).

## Файлы и загрузки

`uploads/supplies/{id}/{dtype}_{имя}`, `uploads/items/{id}.jpg`, `uploads/avatars/{id}.jpg`, `uploads/catalog/{CODE}.jpg`. Всё вне гита. Скачивание — FileResponse по авторизованному запросу. Excel в `/api/report/excel` светит через `?init=` (костыль под window.open без заголовков — см. главу 07, надо бы улучшить).

