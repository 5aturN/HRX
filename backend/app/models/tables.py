"""Модели БД HRXWarehouse (шаг 1). Комментарии на русском. SQLite + async SQLAlchemy.

Как устроено (подробности в README):
- Остаток — items.qty (общая масса). supplies/supply_items — только история приходов.
- QR — только заделы (qr_id/qr_payload nullable), в MVP не используются.
- BOM единый: items(kind) + bom_items(parent,child,qty,version) + bom_chemistry(пометка).
- Два журнала: stock_moves (склад) + audit_log (админ-действия).
- Роли worker/purchaser/admin через user_roles (мультрироли).
- sku глобально уникален; invoice_no НЕ уникален (повтор при доработке).
- stock_moves.order_id NULL = сборка "просто на склад" (теневой заказ).
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _now() -> dt.datetime:
    """Текущее время (наивное, для SQLite)."""
    return dt.datetime.now()


class Folder(Base):
    """Папка дерева хранения. ftype: root|serial|serial_product|consumable|consumable_type|rnd|rnd_project."""
    __tablename__ = "folders"
    __table_args__ = (
        UniqueConstraint("parent_id", "name", name="uq_folder_parent_name"),
        CheckConstraint("ftype IN ('root','serial','serial_product','consumable','consumable_type','rnd','rnd_project')", name="ck_folder_ftype"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("folders.id", ondelete="RESTRICT"), nullable=True)
    ftype: Mapped[str] = mapped_column(String(32), nullable=False, default="consumable_type")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, nullable=False)


class Item(Base):
    """Позиция справочника: detail|standard|subassembly|product. Остаток — qty (общая масса)."""
    __tablename__ = "items"
    __table_args__ = (
        UniqueConstraint("sku", name="uq_item_sku"),
        CheckConstraint("kind IN ('detail','standard','subassembly','product')", name="ck_item_kind"),
        CheckConstraint("qty >= 0", name="ck_item_qty_nonneg"),
        Index("ix_item_folder", "folder_id"),
        Index("ix_item_kind", "kind"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    decimal: Mapped[str | None] = mapped_column(String(100), nullable=True)
    folder_id: Mapped[int] = mapped_column(ForeignKey("folders.id", ondelete="RESTRICT"), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unit: Mapped[str] = mapped_column(String(16), default="шт", nullable=False)
    threshold: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notify_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    low_notified: Mapped[bool] = mapped_column(default=False, nullable=False)
    supplier_article: Mapped[str | None] = mapped_column(String(100), nullable=True)
    std_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_uncountable: Mapped[bool] = mapped_column(default=False, nullable=False)
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    qr_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    qr_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, nullable=False)


class BomItem(Base):
    """Строка состава: parent собирается из child в кол-ве qty. version фиксируется на сборке."""
    __tablename__ = "bom_items"
    __table_args__ = (
        UniqueConstraint("parent_id", "child_id", name="uq_bom_parent_child"),
        CheckConstraint("qty > 0", name="ck_bom_qty_pos"),
        CheckConstraint("parent_id != child_id", name="ck_bom_no_self"),
        Index("ix_bom_parent", "parent_id"),
        Index("ix_bom_child", "child_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    child_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="RESTRICT"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, nullable=False)


class BomChemistry(Base):
    """Химия-пометка в составе (без количества): parent использует chemical."""
    __tablename__ = "bom_chemistry"
    __table_args__ = (
        UniqueConstraint("parent_id", "chemical_id", name="uq_bomchem_parent_chem"),
        Index("ix_bomchem_parent", "parent_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    chemical_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="RESTRICT"), nullable=False)
    note: Mapped[str | None] = mapped_column(String(300), nullable=True)


class Drawing(Base):
    """Сборочный чертёж PDF, версионированный (файл лежит в uploads/)."""
    __tablename__ = "drawings"
    __table_args__ = (Index("ix_drawing_item", "item_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, nullable=False)


class Supply(Base):
    """Шапка поставки (заказ): поставщик, УПД, счёт (НЕ уникален — повтор при доработке), дата."""
    __tablename__ = "supplies"
    __table_args__ = (
        Index("ix_supply_supplier", "supplier"),
        Index("ix_supply_upd", "upd_no"),
        Index("ix_supply_date", "supply_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier: Mapped[str] = mapped_column(String(300), nullable=False)
    upd_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    invoice_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    supply_date: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, nullable=False)
    target: Mapped[str] = mapped_column(String(16), default="stock", nullable=False)
    project_folder_id: Mapped[int | None] = mapped_column(ForeignKey("folders.id", ondelete="SET NULL"), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, nullable=False)


class SupplyItem(Base):
    """Строка поставки: item в кол-ве qty (история прихода, остаток живёт в items.qty)."""
    __tablename__ = "supply_items"
    __table_args__ = (Index("ix_supplyitem_supply", "supply_id"), Index("ix_supplyitem_item", "item_id"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supply_id: Mapped[int] = mapped_column(ForeignKey("supplies.id", ondelete="CASCADE"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="RESTRICT"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)


class SupplyDoc(Base):
    """Документ поставки: upd|invoice|transport|other. Файл — в uploads/ (10 МБ)."""
    __tablename__ = "supply_docs"
    __table_args__ = (
        CheckConstraint("dtype IN ('upd','invoice','transport','other')", name="ck_supplydoc_dtype"),
        Index("ix_supplydoc_supply", "supply_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supply_id: Mapped[int] = mapped_column(ForeignKey("supplies.id", ondelete="CASCADE"), nullable=False)
    dtype: Mapped[str] = mapped_column(String(16), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, nullable=False)


class OcrJob(Base):
    """Задел OCR УПД: поля будущего автозаполнения (поставщик, УПД, дата, позиции)."""
    __tablename__ = "ocr_jobs"
    __table_args__ = (Index("ix_ocr_supply", "supply_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supply_id: Mapped[int] = mapped_column(ForeignKey("supplies.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, nullable=False)


class StockMove(Base):
    """Журнал складских движений: приход|сборка|брак|возврат|выдача_рд|сборка_подсборки|оприходование_подсборки."""
    __tablename__ = "stock_moves"
    __table_args__ = (
        CheckConstraint("mtype IN ('prihod','sborka','brak','vozvrat','vydacha_rd','sborka_podsborki','oprihod_podsborki')", name="ck_move_mtype"),
        Index("ix_move_item_date", "item_id", "created_at"),
        Index("ix_move_date", "created_at"),
        Index("ix_move_order", "order_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="RESTRICT"), nullable=False)
    mtype: Mapped[str] = mapped_column(String(24), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    project_folder_id: Mapped[int | None] = mapped_column(ForeignKey("folders.id", ondelete="SET NULL"), nullable=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    bom_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, nullable=False)


class AuditLog(Base):
    """Журнал административных действий: входы, папки, правки BOM, юзеры, пороги, заказы."""
    __tablename__ = "audit_log"
    __table_args__ = (Index("ix_audit_date", "created_at"), Index("ix_audit_user", "user_id"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, nullable=False)


class User(Base):
    """Пользователь Telegram. Статус: pending|active|blocked. ФИО/должность вводит сам."""
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("tg_id", name="uq_user_tg"),
        CheckConstraint("status IN ('pending','active','blocked')", name="ck_user_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    position: Mapped[str | None] = mapped_column(String(200), nullable=True)
    avatar_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, nullable=False)


class UserRole(Base):
    """Мультироль: worker|purchaser|admin (один юзер — несколько ролей)."""
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role", name="uq_user_role"),
        CheckConstraint("role IN ('worker','purchaser','admin')", name="ck_role_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)


class Customer(Base):
    """Покупатель."""
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    contact: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, nullable=False)


class Order(Base):
    """Заказ: покупатель + статус (new|work|done|shipped). Правится по ходу. Без резерва — только прогресс."""
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("status IN ('new','work','done','shipped')", name="ck_order_status"),
        Index("ix_order_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="new", nullable=False)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, nullable=False)


class OrderItem(Base):
    """Строка заказа: изделие + надо_шт + собрано_шт (прогресс)."""
    __tablename__ = "order_items"
    __table_args__ = (
        UniqueConstraint("order_id", "product_id", name="uq_order_product"),
        CheckConstraint("need_qty > 0", name="ck_orderitem_need_pos"),
        CheckConstraint("done_qty >= 0", name="ck_orderitem_done_nonneg"),
        Index("ix_orderitem_order", "order_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="RESTRICT"), nullable=False)
    need_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    done_qty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class StdCatalog(Base):
    """Эталон стандарта: код (DIN912), название, описание, фото. Фото одно на всех, кто выбрал этот код."""
    __tablename__ = "std_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    std_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    descr: Mapped[str | None] = mapped_column(String(500), nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)


class Favorite(Base):
    """Избранное: своё у каждого пользователя (user_id + item_id уникальны)."""
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "item_id", name="uq_fav_user_item"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
