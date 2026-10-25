"""Сиды каталога: ходовые DIN/ISO/ГОСТ с названиями. Фото добавите руками через админку."""
import asyncio
import logging
from app.core.db import SessionLocal
import app.models  # noqa
from sqlalchemy import select
from app.models.tables import StdCatalog

BASE = [
    ("DIN912", "Винт с цилиндрической головкой (внутр. шестигранник)", "Ходовой винт под ключ-шестигранник"),
    ("DIN933", "Болт с шестигранной головкой (полная резьба)", "Ходовой болт"),
    ("DIN934", "Гайка шестигранная", "Ходовая гайка"),
    ("DIN125", "Шайба плоская", "Ходовая шайба"),
    ("DIN127", "Шайба пружинная (гровер)", "От самоотвинчивания"),
    ("ISO7380", "Винт с полукруглой головкой (TORX/шестигранник)", "Красивый, на видные места"),
    ("ISO4762", "Винт с цилиндрической головкой (аналог DIN912)", "То же, что DIN912"),
    ("DIN7991", "Винт с потайной головкой", "Впотай"),
    ("DIN965", "Винт с потайной головкой (крест)", "Впотай под крест"),
    ("DIN7981", "Саморез с полукруглой головкой", "По металлу"),
    ("GOST14771", "Электрод сварочный", "Для сварки"),
    ("LOCTITE243", "Фиксатор резьбы средний (синий)", "Капля на резьбу"),
]

async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    async with SessionLocal() as s:
        n = 0
        for code, title, descr in BASE:
            old = (await s.execute(select(StdCatalog).where(StdCatalog.std_code == code))).scalar_one_or_none()
            if old is None:
                s.add(StdCatalog(std_code=code, title=title, descr=descr))
                n += 1
        await s.commit()
        print(f"Каталог: добавлено {n}, всего {len(BASE)}")

if __name__ == "__main__":
    asyncio.run(main())
