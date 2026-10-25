"""Роут приёмки, документов и остатков."""
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.db import get_session
from app.models.tables import AuditLog, Folder, Item, Supply, SupplyDoc, SupplyItem
from app.routers.deps import current_user, need_roles
from app.schemas.receipt import StockRow, SupplyCreate, SupplyOut
from app.services.receipt import create_supply

log = logging.getLogger("hrx.routers.receipt")
router = APIRouter(prefix="/api", tags=["склад"])
ALLOWED_DOCS = {"upd", "invoice", "transport", "other"}

@router.post("/supplies", response_model=SupplyOut, dependencies=[Depends(need_roles("worker"))])
async def add_supply(data: SupplyCreate, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Принять поставку: шапка + строки, приход в остатки."""
    try:
        supply = await create_supply(session, data, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    positions = len(data.items)
    return SupplyOut(id=supply.id, supplier=supply.supplier, upd_no=supply.upd_no,
                      invoice_no=supply.invoice_no, positions=positions, total_qty=sum(i.qty for i in data.items))

@router.get("/supplies")
async def list_supplies(session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Список поставок, свежие сверху."""
    rows = (await session.execute(select(Supply).order_by(Supply.id.desc()).limit(200))).scalars().all()
    out = []
    for s in rows:
        n = await session.scalar(select(func.count()).select_from(SupplyItem).where(SupplyItem.supply_id == s.id)) or 0
        q = await session.scalar(select(func.coalesce(func.sum(SupplyItem.qty), 0)).where(SupplyItem.supply_id == s.id)) or 0
        out.append({"id": s.id, "supplier": s.supplier, "upd_no": s.upd_no, "invoice_no": s.invoice_no,
                    "date": s.supply_date.isoformat() if s.supply_date else None, "positions": n, "total_qty": q})
    return out

@router.post("/supplies/{supply_id}/docs", dependencies=[Depends(need_roles("worker"))])
async def upload_doc(supply_id: int, dtype: str = Query(default="upd"), file: UploadFile = File(...),
                     session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Прикрепить документ к поставке (УПД, счёт, транспорт). До 10 МБ."""
    if dtype not in ALLOWED_DOCS:
        raise HTTPException(status_code=400, detail="Тип документа: upd, invoice, transport, other")
    supply = await session.get(Supply, supply_id)
    if supply is None:
        raise HTTPException(status_code=404, detail="Поставка не найдена")
    data = await file.read()
    limit = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(data) > limit:
        raise HTTPException(status_code=400, detail=f"Файл больше {settings.MAX_UPLOAD_MB} МБ")
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Пустой файл")
    updir = Path(settings.UPLOAD_DIR) / "supplies" / str(supply_id)
    updir.mkdir(parents=True, exist_ok=True)
    safe = "".join(c for c in (file.filename or "doc") if c.isalnum() or c in "._- ").strip() or "doc"
    dest = updir / f"{dtype}_{safe}"
    dest.write_bytes(data)
    doc = SupplyDoc(supply_id=supply_id, dtype=dtype, file_path=str(dest))
    session.add(doc)
    session.add(AuditLog(user_id=user.id, action="doc_upload", details=f"Поставка №{supply_id}: {dtype} {safe}"))
    await session.commit()
    log.info("Документ к поставке №%s: %s (%s байт)", supply_id, safe, len(data))
    return {"id": doc.id, "dtype": dtype, "name": safe}

@router.get("/supplies/{supply_id}/docs")
async def list_docs(supply_id: int, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Документы поставки."""
    docs = (await session.execute(select(SupplyDoc).where(SupplyDoc.supply_id == supply_id))).scalars().all()
    return [{"id": d.id, "dtype": d.dtype, "path": d.file_path} for d in docs]

@router.get("/docs/{doc_id}/download")
async def download_doc(doc_id: int, session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Скачать документ (только для своих)."""
    doc = await session.get(SupplyDoc, doc_id)
    if doc is None or not Path(doc.file_path).exists():
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(doc.file_path, filename=Path(doc.file_path).name)

@router.get("/stock", response_model=list[StockRow])
async def stock(q: str = Query(default=""), folder_id: int | None = None, low_only: bool = False,
                session: AsyncSession = Depends(get_session), user=Depends(current_user)):
    """Остатки с поиском по артикулу, названию, децимальному. Русские поля отдаёт фронт."""
    stmt = select(Item, Folder.name).join(Folder, Folder.id == Item.folder_id)
    if folder_id:
        stmt = stmt.where(Item.folder_id == folder_id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Item.sku.ilike(like), Item.name.ilike(like),
                              Item.decimal.ilike(like), Item.supplier_article.ilike(like)))
    stmt = stmt.order_by(Item.name).limit(500)
    rows = (await session.execute(stmt)).all()
    out = []
    for item, folder in rows:
        low = item.notify_enabled and item.qty <= item.threshold
        if low_only and not low:
            continue
        out.append(StockRow(id=item.id, sku=item.sku, name=item.name, decimal=item.decimal,
                            folder=folder, qty=item.qty, threshold=item.threshold, low=low))
    return out
