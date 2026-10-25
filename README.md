# HRXWarehouse — склад производственного предприятия (Telegram Mini App)

Монорепо: FastAPI (Python 3.14) + SQLite (WAL, async SQLAlchemy) + React + TS (Vite) + Telegram Mini App.

## Статус
Сейчас: скелет. Дальше:
1. БД + Alembic + seed
2. Приёмка + документы УПД + остатки
3. Сборки/подсборки + умная сборка + пороги
4. R&D пулы + брак/возврат
5. Журналы + Excel + визуальные отчёты + админка (user/worker, purchaser, admin, мультрироли)

## Как устроено
- QR-коды отложены, в схеме только заделы (`qr_id`, `qr_payload` nullable). Сканер в будущем — `@yudiel/react-qr-scanner`, точка расширения `ScanButton -> onScan()`.
- Приёмка ручная: шапка поставки общая (поставщик, № УПД, дата — № счёта НЕ уникален), строки с выбором `деталь | покупнина`. Децимальный только у деталей.
- Документы поставки: `upd | invoice | transport | other`, УПД необязательна для закрытия приёмки (может прийти по ЭДО позже), скачивание нужно, 10 МБ/файл, хранение в `uploads/` вне гита.
- Списание всегда из суммарного остатка `items.qty`, партии — только история приходов. Брак/возврат — любое кол-во из общей массы.
- Сборки: единый `items(kind=detail|standard|subassembly|product) + bom_items(parent,child,qty)` любой глубины + `bom_chemistry(parent, chemical, note)` без количества + `drawings(item, pdf, version)`. Циклы запрещены. Подсборки stockable (собираются отдельной кнопкой: списать наполнение, +1 к остатку). Умная сборка вариант Б: не собираем автоматом, предлагаем дособрать недостающее. Множественная сборка разрешена (N шт), частичная запрещена (пока).
- R&D: своя папка = свой пул заказных деталей + списание общих стандартов (все `/Расходники/*`) с меткой `project_id`. Химия — только пометка в составе, учёт — ручное списание тюбиков, порог по шт.
- Пороги: `items.threshold + notify_enabled`, уведомления всем закупщикам + дубль админу через Bot API.
- Роли: `worker (=user, вся цепочка), purchaser (остатки/отчёты+уведомления), admin (всё)`, мультрироли через `user_roles`. Регистрация: юзер сам вводит ФИО/должность, админ проверяет и активирует.
- Артикул `sku` глобально уникален. Поиск по артикул/наименование/децимальный/поставщик/№ УПД.
- Два журнала: `stock_moves` (склад) + `audit_log` (админ-действия).
- Заказы: `customers/orders` — покупатель + позиции (изделие, надо_шт) + общий прогресс. Создавать может любой юзер. Сборка в рамках заказа списывает со склада и двигает прогресс.
- Отчёты: Excel (Остатки + Движения) + визуал в приложении, все шапки на русском, фильтры обязательны.
- Деплой: локально `DEV_ALLOW_UNAUTH=1 + uvicorn :8000 + npm run dev`, сервер — `Caddy 443 (LE) -> 127.0.0.1:8000 (NSSM)`. Самоподписанный не делаем.
- Токен бота только в локальном `.env`, никогда в git. `.env.example` — без секретов.
- Скачивание файлов из Mini App — по авторизованной ссылке.

## Структура
```
HRXWarehouse/
  backend/app/{core,models,schemas,routers,services} + alembic + requirements.txt + seed
  frontend/src/{pages,components,api} (Vite+React+TS)
  docs/ (ARCHITECTURE, API, DEPLOY_LOCAL, DEPLOY_SERVER)
  uploads/ (в .gitignore)
```

## Локальный запуск (будет дополнено в шаге 1)
```powershell
cd backend
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy ..\..\.env.example ..\.env  # положить BOT_TOKEN локально
uvicorn app.main:app --reload --port 8000
```
Frontend:
```powershell
cd frontend
npm install
npm run dev
```

## Git
`main` — стабильная. Фичи — короткими ветками. Push — через GitHub Desktop (PAT нет).
Remote: https://github.com/5aturN/HRX
