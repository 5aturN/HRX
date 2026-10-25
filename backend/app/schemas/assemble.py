"""Схемы сборки: что хотим собрать и чего не хватает."""
from __future__ import annotations
from pydantic import BaseModel, Field

class MissingRow(BaseModel):
    """Одна недостающая позиция: что, сколько надо, сколько есть."""
    item_id: int
    sku: str
    name: str
    need: int
    have: int
    build_subassembly_id: int | None = None
    build_subassembly_name: str | None = None

class AssembleCheck(BaseModel):
    """Проверка перед сборкой: можно или нет, и чего не хватает."""
    can: bool
    missing: list[MissingRow] = []
    need_subassemblies: list[MissingRow] = []

class AssembleDo(BaseModel):
    """Команда собрать: что, сколько, в какой заказ (null = просто на склад)."""
    product_id: int
    qty: int = Field(gt=0, le=100)
    order_id: int | None = None
