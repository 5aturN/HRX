#!/usr/bin/env python3
"""Ежедневный бэкап HRXWarehouse: база данных + каталог uploads.

Что делает:
  1. SQLite (DATABASE_URL начинается с sqlite) — безопасная копия через
     sqlite3 backup API (корректно даже при включённом WAL).
     PostgreSQL — выгрузка через pg_dump (должен стоять в PATH).
  2. Каталог uploads — в tar.gz архив.
  3. Оставляет по 7 самых свежих копий каждого типа, старые удаляет.

Настройки — переменными окружения (см. .env.example в корне):
  DATABASE_URL, UPLOAD_DIR, BACKUP_DIR.

Запуск вручную:
  python backend/scripts/backup.py
По расписанию (раз в день в 03:00):
  0 3 * * * /путь/к/python /путь/к/HRXWarehouse/backend/scripts/backup.py
В контейнере бэкапы лежат в томе backups (BACKUP_DIR=/srv/backups).
"""

from __future__ import annotations

import os
import shutil
import sqlite3
import subprocess
import tarfile
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

# Сколько свежих копий каждого типа хранить.
KEEP_COPIES = 7


def _env(name: str, default: str) -> str:
    """Переменная окружения или значение по умолчанию."""
    return os.environ.get(name, default)


def _stamp() -> str:
    """Метка времени для имён файлов: 20260131-030000."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def _prune(backup_dir: Path, prefix: str, keep: int = KEEP_COPIES) -> None:
    """Удаляет старые копии с префиксом, оставляет `keep` самых свежих."""
    copies = sorted(backup_dir.glob(prefix + "*"))
    if len(copies) > keep:
        for old in copies[:-keep]:
            old.unlink()
            print(f"Удалён старый бэкап: {old.name}")


def backup_sqlite(db_path: Path, backup_dir: Path) -> Path:
    """Безопасная копия SQLite (работает и с WAL-режимом)."""
    out = backup_dir / f"hrx-db-{_stamp()}.db"
    src = sqlite3.connect(db_path)
    try:
        dst = sqlite3.connect(out)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()
    print(f"SQLite скопирована: {out.name}")
    return out


def backup_postgres(db_url: str, backup_dir: Path) -> Path:
    """Выгрузка PostgreSQL через pg_dump в кастомном формате (-F c)."""
    if shutil.which("pg_dump") is None:
        raise RuntimeError("pg_dump не найден в PATH — поставьте postgresql-client")
    # postgresql+asyncpg://user:pass@host:port/db -> части для pg_dump.
    # Пароль передаём через PGPASSWORD, а не в аргументах (не светится в ps).
    u = urlparse(db_url)
    out = backup_dir / f"hrx-db-{_stamp()}.dump"
    cmd = [
        "pg_dump",
        "-h", u.hostname or "localhost",
        "-p", str(u.port or 5432),
        "-U", unquote(u.username or "postgres"),
        "-d", unquote((u.path or "/hrx").lstrip("/")),
        "-F", "c",
        "-f", str(out),
    ]
    env = {**os.environ, "PGPASSWORD": unquote(u.password or "")}
    subprocess.run(cmd, env=env, check=True)
    print(f"PostgreSQL выгружен: {out.name}")
    return out


def backup_uploads(upload_dir: Path, backup_dir: Path) -> Path | None:
    """Архив каталога uploads. Нет каталога — пропускаем без ошибки."""
    if not upload_dir.is_dir():
        print(f"Каталог uploads не найден ({upload_dir}) — пропускаем")
        return None
    out = backup_dir / f"hrx-uploads-{_stamp()}.tar.gz"
    with tarfile.open(out, "w:gz") as tar:
        tar.add(upload_dir, arcname="uploads")
    print(f"Uploads заархивированы: {out.name}")
    return out


def main() -> int:
    backup_dir = Path(_env("BACKUP_DIR", "./backups"))
    upload_dir = Path(_env("UPLOAD_DIR", "./uploads"))
    db_url = _env("DATABASE_URL", "sqlite+aiosqlite:///./hrx.db")
    backup_dir.mkdir(parents=True, exist_ok=True)

    try:
        if db_url.startswith("sqlite"):
            # Отрезаем схему: sqlite+aiosqlite:///./hrx.db -> ./hrx.db.
            # Ведущий слэш один — относительный путь, двойной — абсолютный.
            raw = db_url.split("://", 1)[1]
            if raw.startswith("//"):
                db_path = Path("/" + raw.lstrip("/"))
            else:
                db_path = Path(raw.lstrip("/"))
            if not db_path.is_file():
                # Ищем рядом: запуск возможен и из корня, и из папки backend.
                here = Path(__file__).resolve().parents[1]
                for cand in (Path.cwd() / db_path, here / db_path, here / db_path.name):
                    if cand.is_file():
                        db_path = cand
                        break
            if not db_path.is_file():
                print(f"Файл БД не найден: {db_path}")
                return 1
            backup_sqlite(db_path, backup_dir)
        else:
            backup_postgres(db_url, backup_dir)
        backup_uploads(upload_dir, backup_dir)
    except (OSError, RuntimeError, sqlite3.Error, subprocess.SubprocessError, tarfile.TarError) as exc:
        print(f"ОШИБКА бэкапа: {exc}")
        return 1

    _prune(backup_dir, "hrx-db-")
    _prune(backup_dir, "hrx-uploads-")
    print(f"Готово. Бэкапы в {backup_dir.resolve()}, хранится по {KEEP_COPIES} свежих копий.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
