"""Скелет моделей шага 0. Полные таблицы — в шаге 1 (БД + Alembic + seed).

Сущности (зафиксированы):
folders, items(kind=detail|standard|subassembly|product), bom_items, bom_chemistry,
drawings, supplies, supply_items, supply_docs, stock_moves, audit_log,
users, user_roles, customers, orders, order_items, ocr_jobs.
Заделы: qr_id/qr_payload nullable (QR отложены).
"""
