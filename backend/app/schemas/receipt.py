"""Схемы приёмки и остатков. Все подписи на русском, ошибки тоже русские."""
from __future__ import annotations
import datetime as dt
from pydantic import BaseModel, Field

class NewItemIn(BaseModel):
    """Одна строка поставки. kind: detail (наша, нужен decimal) или standard (покупная)."""
    kind: str = Field(pattern="^(detail|standard)$")
    sku: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=300)
    decimal: str | None = Field(default=None, max_length=100)
    folder_id: int
    qty: int = Field(gt=0)
    supplier_article: str | None = Field(default=None, max_length=100)

class SupplyCreate(BaseModel):
    """Шапка поставки + строки. № счёта не уникален (повтор при доработке)."""
    supplier: str = Field(min_length=1, max_length=300)
    upd_no: str | None = Field(default=None, max_length=100)
    invoice_no: str | None = Field(default=None, max_length=100)
    supply_date: dt.date | None = None
    target: str = Field(default="stock", pattern="^(stock|project)$")
    project_folder_id: int | None = None
    items: list[NewItemIn] = Field(min_length=1)

class SupplyOut(BaseModel):
    id: int
    supplier: str
    upd_no: str | None
    invoice_no: str | None
    positions: int
    total_qty: int

class StockRow(BaseModel):
    """Строка остатков для таблицы (русские ключи отдаёт фронт)."""
    id: int
    sku: str
    name: str
    decimal: str | None
    folder: str
    qty: int
    threshold: int
    low: bool
