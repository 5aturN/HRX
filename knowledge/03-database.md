# 03 — База данных

SQLite в WAL (`PRAGMA journal_mode=WAL, foreign_keys=ON` при коннекте). Асинхронный доступ через SQLAlchemy 2. Модели — `backend/app/models/tables.py` (источник правды), миграции — `backend/alembic/versions/`.
Создать с нуля: `python create_db.py` (create_all). Правильно: `alembic upgrade head`. Сиды: `seed.py` (папки, А/Б/В, BOM, заказ), `seed_catalog.py` (12 эталонов).

## folders — дерево

| Поле | Тип | Что |
|---|---|---|
| id | int pk | — |
| name | str(200) | «Метизы», «Проект Альфа» |
| parent_id | fk folders | NULL только у корня; удаление RESTRICT |
| ftype | str | root, serial, serial_product, consumable, consumable_type, rnd, rnd_project |
| created_at | datetime | — |
Уникальность: (parent_id, name). Корень один: «Склад». R&D проекты — ftype=rnd_project, их находит выдача и приёмка в проект.

## items — все позиции

| Поле | Тип | Что |
|---|---|---|
| id, sku (unique!), name | int, str(100), str(300) | sku глобально уникален |
| decimal | str(100)? | только у detail, обязателен при приёмке детали |
| folder_id | fk | строго одна папка |
| kind | detail, standard, subassembly, product | — |
| qty | int ≥ 0 | ОСТАТОК, общая масса |
| unit | str | «шт» по умолчанию |
| threshold, notify_enabled, low_notified | int, bool, bool | порог + галочка напоминать + флаг «уже писали» (приёмка сбрасывает) |
| supplier_article | str? | артикул поставщика |
| std_code | str(50)? | код каталога (DIN912...), индекс |
| photo_path | str? | своё фото (`uploads/items/{id}.jpg`) |
| is_uncountable | bool | задел (химия без счёта) |
| qr_id, qr_payload | str?, text? | ЗАДЕЛЫ под QR, не используются |
Индексы: folder_id, kind. Если своего фото нет, а std_code есть — отдаём фото эталона (фолбэк в `routers/photos.py`).

## bom_items — состав

parent_id → child_id, qty > 0, version (default 1). Уникальность (parent, child). parent != child. Каскад: удалил parent — строки сыплются, child удалять при связях нельзя (RESTRICT).
Любая глубина. Кольца ловит `_expand` в сервисе сборки (множество seen). На движении пишется версия состава.

## bom_chemistry — химия-пометка

parent_id + chemical_id (уникальны в паре) + note («обезжирить перед склейкой»). Без количества. В списание не идёт, только показывается с фото банки.

## drawings — чертежи

item_id (каскад) + file_path (`uploads/`) + version + created_at. Пока только структура: загрузки чертежей в API нет (см. главу 10).

## supplies — шапка поставки

supplier (обязательно), upd_no?, invoice_no? (НЕ уникален!), supply_date, target (stock|project), project_folder_id? (только rnd_project), created_by?, created_at.
Индексы: supplier, upd_no, supply_date. Одна поставка = один заказ = много строк.

## supply_items — строки поставки

supply_id (каскад) + item_id (RESTRICT) + qty. История приходов. Индексы по обеим колонкам.

## supply_docs — файлы поставки

supply_id (каскад) + dtype (upd|invoice|transport|other) + file_path. Хранение: `uploads/supplies/{supply_id}/{dtype}_{имя}`. Лимит 10 МБ (настройка MAX_UPLOAD_MB).

## ocr_jobs — задел OCR

supply_id (каскад) + status (default pending) + payload? (json с будущими полями: поставщик, УПД, дата, позиции) + created_at. Движка нет.

## stock_moves — движения (журнал 1)

item_id (RESTRICT) + mtype + qty + reason? + project_folder_id? + order_id? (NULL = на склад) + bom_version? + user_id? + created_at.
Типы: prihod (Приход), sborka (Сборка), brak (Брак), vozvrat (Возврат), vydacha_rd (Выдача в проект), sborka_podsborki (Сборка подсборки), oprihod_podsborki (Оприходование). Русские имена — в `services/reports.py` (MTYPE_RU).
Индексы: (item_id, created_at), created_at, order_id. Лимит выборки в отчётах — 5000/1000.

## audit_log — действия людей (журнал 2)

user_id? + action (priemka, sborka, brak, vozvrat, vydacha_rd, doc_upload, photo, catalog_add, porog, project_add, user_activate, user_block, order_add, order_status) + details? + created_at.
Индексы: created_at, user_id. Смотрит только админ.

## users, user_roles — люди

users: id, tg_id (unique, BigInteger), username?, first_name?, last_name?, position?, status (pending|active|blocked), avatar_path? (`uploads/avatars/{id}.jpg`), created_at.
user_roles: user_id (каскад) + role (worker|purchaser|admin), уникальность (user_id, role). Мультрироли. Тестовые tg 1, 2 в уведомлениях пропускаются.

## customers, orders, order_items — заказы

customers: name, contact?. orders: customer_id (RESTRICT) + status (new|work|done|shipped) + note? + created_by? + created_at. order_items: order_id (каскад) + product_id (только product|subassembly) + need_qty > 0 + done_qty ≥ 0, уникальность (order, product). Резерва нет, только прогресс.

## std_catalog — эталоны

std_code (unique, верхний регистр) + title + descr? + photo_path? (`uploads/catalog/{CODE}.jpg`). 12 сидов: DIN912, DIN933, DIN934, DIN125, DIN127, ISO7380, ISO4762, DIN7991, DIN965, DIN7981, GOST14771, LOCTITE243. Подробно — глава 06.

## favorites — избранное

user_id (каскад) + item_id (каскад), уникальность (user_id, item_id). У каждого своё.

## Миграции

| Ревизия | Что |
|---|---|
| 0001_init | всё из моделей (create_all) |
| 0002_photos | items.photo_path, users.avatar_path |
| 0003_catalog | std_catalog + items.std_code + индекс |
| 0004_favs | favorites |
| 0005_low_notified | items.low_notified (антиспам уведомлений) |
env.py — настоящий async (без fileConfig). Команда: `alembic upgrade head` из папки backend. Новая миграция: поменять models → `alembic revision --autogenerate -m "..."` → проверить → upgrade. Файл базы (`hrx.db*`) и `uploads/` в гите нет.

## Связи одной картинкой

```
folders ──< items ──< bom_items (parent/child), bom_chemistry
              ├── supply_items ── supplies ── supply_docs, ocr_jobs
              ├── stock_moves ── orders ── order_items; stock_moves.project → folders
              ├── drawings, favorites; items.std_code → std_catalog
users ── user_roles, stock_moves, audit_log, supplies, orders
```

