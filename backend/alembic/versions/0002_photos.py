"""Фото позиций и аватары (только если колонок ещё нет — 0001 уже создаёт их из моделей)."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002_photos"
down_revision = "0001_init"
branch_labels = None
depends_on = None

def _cols(table: str) -> set:
    bind = op.get_bind()
    return {c["name"] for c in inspect(bind).get_columns(table)}

def upgrade():
    if "photo_path" not in _cols("items"):
        op.add_column("items", sa.Column("photo_path", sa.String(500), nullable=True))
    if "avatar_path" not in _cols("users"):
        op.add_column("users", sa.Column("avatar_path", sa.String(500), nullable=True))

def downgrade():
    if "photo_path" in _cols("items"):
        op.drop_column("items", "photo_path")
    if "avatar_path" in _cols("users"):
        op.drop_column("users", "avatar_path")
