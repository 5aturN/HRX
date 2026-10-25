# 02 — База данных

SQLite в режиме WAL, доступ через async SQLAlchemy. Файл базы и загрузки в git не попадают.

## Таблицы

| Таблица | Что лежит |
|---|---|
| `folders` | Дерево: корень, серийная, расходники по типам, R&D и проекты. |
| `items` | Все позиции: `detail` (наша, децимальный обязателен), `standard` (покупная), `subassembly`, `product`. Остаток — `qty`. |
| `bom_items` | Состав: `parent → child, qty, version`. Любая глубина, кольцо запрещено. |
| `bom_chemistry` | Химия-пометка без количества. |
| `drawings` | Сборочные PDF с версиями (файлы в `uploads/`). |
| `supplies` | Шапка поставки: поставщик, УПД, счёт (не уникален — повтор при доработке), дата, склад или проект. |
| `supply_items` | Строки поставки — история приходов. |
| `supply_docs` | Файлы: `upd | invoice | transport | other`, до 10 МБ. |
| `ocr_jobs` | Задел под распознавание УПД (`pending`). |
| `stock_moves` | Движения: приход, сборка, брак, возврат, выдача в проект. |
| `audit_log` | Действия людей: приёмки, сборки, пороги, люди, заказы. |
| `users`, `user_roles` | Люди и мультрироли: `worker`, `purchaser`, `admin`. |
| `customers`, `orders`, `order_items` | Покупатели, заказы (надо/готово), прогресс. |

## Правила

- `items.sku` уникален глобально. Повторная приёмка того же артикула — плюс к остатку, дублей нет.
- Списание всегда из общей массы, без выбора партии.
- При правке состава старые сборки не пересчитываются: на движении пишется `bom_version`.
- Порог: `items.threshold + notify_enabled`. Письма закупщикам + копия админу.
- QR — только поля-заделы (`qr_id`, `qr_payload`), в учёте не участвуют.

## Схема связей

```
folders (1) ──< items >── bom_items (parent/child)
                ├── supply_items ── supplies ── supply_docs
                ├── stock_moves ── orders ── order_items
                └── drawings, bom_chemistry
users ── user_roles, stock_moves, audit_log
```

Фото: `items.photo_path`, `users.avatar_path` (миграция `0002_photos`). Файлы в `uploads/items/` и `uploads/avatars/`, в git не попадают.
