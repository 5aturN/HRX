"""Каталог стандартов (идемпотентно: на пустой базе 0001 уже всё создал)."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0003_catalog"
down_revision = "0002_photos"
branch_labels = None
depends_on = None

def _tables() -> set:
    return set(inspect(op.get_bind()).get_table_names())

def _cols(t: str) -> set:
    return {c["name"] for c in inspect(op.get_bind()).get_columns(t)}

def upgrade():
    if "std_catalog" not in _tables():
        op.create_table("std_catalog",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("std_code", sa.String(50), nullable=False, unique=True),
            sa.Column("title", sa.String(300), nullable=False),
            sa.Column("descr", sa.String(500), nullable=True),
            sa.Column("photo_path", sa.String(500), nullable=True),
        )
    if "std_code" not in _cols("items"):
        op.add_column("items", sa.Column("std_code", sa.String(50), nullable=True))
    try:
        op.create_index("ix_item_std", "items", ["std_code"])
    except Exception:
        pass

def downgrade():
    try:
        op.drop_index("ix_item_std", table_name="items")
    except Exception:
        pass
    if "std_code" in _cols("items"):
        op.drop_column("items", "std_code")
    if "std_catalog" in _tables():
        op.drop_table("std_catalog")
