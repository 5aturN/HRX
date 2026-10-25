"""Схемы движений: брак, возврат, выдача в проект, пороги."""
from __future__ import annotations
from pydantic import BaseModel, Field

class MoveDo(BaseModel):
    """Брак/возврат/выдача: позиция, кол-во, причина, проект если надо."""
    item_id: int
    qty: int = Field(gt=0, le=100000)
    reason: str | None = Field(default=None, max_length=500)
    project_folder_id: int | None = None

class ThresholdDo(BaseModel):
    """Порог позиции: число и галочка напоминать."""
    threshold: int = Field(ge=0, le=1000000)
    notify_enabled: bool = True
