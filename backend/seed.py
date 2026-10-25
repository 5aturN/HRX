"""Seed шага 1 (рус.): папки, Изделия А/Б/В + подсборки С1/С2, детали, стандарты, расходники, R&D, заказ-пример, юзеры-плейсхолдеры. Остатки по 20, пороги на расходниках 20."""
import asyncio
import logging
from app.core.db import SessionLocal, engine, Base
import app.models  # noqa: F401
from app.models.tables import Customer, Folder, Item, BomItem, BomChemistry, Order, OrderItem, User, UserRole, StockMove

log = logging.getLogger("hrx.seed")

async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    async with SessionLocal() as s:
        from sqlalchemy import select, func
        n = await s.scalar(select(func.count()).select_from(Folder))
        if n and n > 0:
            log.info("Seed пропущен: папок уже %s", n)
            return
        # --- Папки ---
        root = Folder(name="Склад", parent_id=None, ftype="root")
        s.add(root); await s.flush()
        serial = Folder(name="Серийная продукция", parent_id=root.id, ftype="serial")
        consum = Folder(name="Расходники", parent_id=root.id, ftype="consumable")
        rnd = Folder(name="R&D проекты", parent_id=root.id, ftype="rnd")
        s.add_all([serial, consum, rnd]); await s.flush()
        fA = Folder(name="Изделие А", parent_id=serial.id, ftype="serial_product")
        fB = Folder(name="Изделие Б", parent_id=serial.id, ftype="serial_product")
        fV = Folder(name="Изделие В", parent_id=serial.id, ftype="serial_product")
        fMet = Folder(name="Метизы", parent_id=consum.id, ftype="consumable_type")
        fChem = Folder(name="Химия", parent_id=consum.id, ftype="consumable_type")
        fGlue = Folder(name="Клеи", parent_id=consum.id, ftype="consumable_type")
        fOther = Folder(name="Прочее", parent_id=consum.id, ftype="consumable_type")
        fP1 = Folder(name="Проект Альфа", parent_id=rnd.id, ftype="rnd_project")
        s.add_all([fA, fB, fV, fMet, fChem, fGlue, fOther, fP1]); await s.flush()
        log.info("Папок создано: 12")

        def it(sku, name, folder, kind, qty=20, **kw):
            return Item(sku=sku, name=name, folder_id=folder, kind=kind, qty=qty, **kw)

        items = []
        # Изделия и подсборки
        pA = it("A-000", "Изделие А", fA.id, "product", qty=0)
        pB = it("B-000", "Изделие Б", fB.id, "product", qty=0)
        pV = it("V-000", "Изделие В", fV.id, "product", qty=0)
        sA1 = it("A-C1", "Подсборка А-С1", fA.id, "subassembly")
        sA2 = it("A-C2", "Подсборка А-С2", fA.id, "subassembly")
        sB1 = it("B-C1", "Подсборка Б-С1", fB.id, "subassembly")
        items += [pA, pB, pV, sA1, sA2, sB1]
        # Детали А (наши, с децимальными)
        dA1 = it("A-001", "Корпус А", fA.id, "detail", decimal="ХРВ.001")
        dA2 = it("A-002", "Крышка А", fA.id, "detail", decimal="ХРВ.002")
        dA3 = it("A-003", "Вал А", fA.id, "detail", decimal="ХРВ.003")
        dB1 = it("B-001", "Рама Б", fB.id, "detail", decimal="ХРВ.101")
        dB2 = it("B-002", "Плита Б", fB.id, "detail", decimal="ХРВ.102")
        dV1 = it("V-001", "Основание В", fV.id, "detail", decimal="ХРВ.201")
        dV2 = it("V-002", "Захват В", fV.id, "detail", decimal="ХРВ.202")
        items += [dA1, dA2, dA3, dB1, dB2, dV1, dV2]
        # Стандарты (покупные)
        st1 = it("M4x16", "Винт М4х16", fMet.id, "standard", supplier_article="DIN933-M4x16")
        st2 = it("M4-G", "Гайка М4", fMet.id, "standard", supplier_article="DIN934-M4")
        st3 = it("PODSH-8", "Подшипник 8мм", fOther.id, "standard")
        items += [st1, st2, st3]
        # Химия/клеи (учитываются тюбиками, в сборку не списываются)
        ch1 = it("CH-OBEZ", "Обезжириватель (баллон)", fChem.id, "standard", threshold=20)
        ch2 = it("GLUE-E", "Клей эпоксидный (тюбик)", fGlue.id, "standard", threshold=20)
        ch3 = it("CH-SMAZ", "Смазка (тюбик)", fChem.id, "standard", threshold=20)
        items += [ch1, ch2, ch3]
        # R&D детали проекта Альфа
        r1 = it("RD-A1", "Плата Альфа (заказная)", fP1.id, "detail", decimal="РНД.001")
        r2 = it("RD-A2", "Корпус Альфа (заказной)", fP1.id, "detail", decimal="РНД.002")
        items += [r1, r2]
        for x in items:
            if x.kind == "standard":
                x.threshold = x.threshold or 20
            s.add(x)
        await s.flush()
        by = {x.sku: x for x in items}
        log.info("Позиций создано: %s", len(items))
        # --- BOM ---
        bom = [
            (sA1, dA1, 1), (sA1, st1, 4),
            (sA2, dA2, 1), (sA2, dA3, 2), (sA2, st2, 4),
            (pA, sA1, 1), (pA, sA2, 1), (pA, st3, 2),
            (sB1, dB1, 1), (sB1, st1, 6),
            (pB, sB1, 1), (pB, dB2, 2),
            (pV, dV1, 1), (pV, dV2, 2), (pV, st1, 8),
        ]
        for par, ch, q in bom:
            s.add(BomItem(parent_id=par.id, child_id=ch.id, qty=q, version=1))
        s.add(BomChemistry(parent_id=pA.id, chemical_id=ch1.id, note="Обезжирить перед склейкой"))
        s.add(BomChemistry(parent_id=pA.id, chemical_id=ch2.id, note="Клей эпоксидный"))
        log.info("BOM строк: %s + химия 2", len(bom))
        # --- Пользователи-плейсхолдеры ---
        admin = User(tg_id=1, username="admin", first_name="Админ", last_name="Админов", position="Администратор", status="active")
        purch = User(tg_id=2, username="purchaser", first_name="Закуп", last_name="Закупщиков", position="Менеджер по закупкам", status="active")
        s.add_all([admin, purch]); await s.flush()
        s.add_all([UserRole(user_id=admin.id, role="admin"), UserRole(user_id=purch.id, role="purchaser")])
        # --- Заказ-пример ---
        cust = Customer(name="Тестовый покупатель", contact="test@example.com")
        s.add(cust); await s.flush()
        order = Order(customer_id=cust.id, status="work", note="3 манипулятора (А) + 2 захвата (В)", created_by=admin.id)
        s.add(order); await s.flush()
        s.add_all([OrderItem(order_id=order.id, product_id=pA.id, need_qty=3), OrderItem(order_id=order.id, product_id=pV.id, need_qty=2)])
        await s.commit()
        log.info("Seed готов: заказ-пример (3xА + 2xВ), юзеры admin/purchaser")

if __name__ == "__main__":
    asyncio.run(main())
