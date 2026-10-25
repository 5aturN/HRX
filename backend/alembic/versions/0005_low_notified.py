"""Флаг low_notified (идемпотентно)."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0005_low_notified"
down_revision = "0004_favs"
branch_labels = None
depends_on = None

def upgrade():
    cols = {c["name"] for c in inspect(op.get_bind()).get_columns("items")}
    if "low_notified" not in cols:
        op.add_column("items", sa.Column("low_notified", sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade():
    cols = {c["name"] for c in inspect(op.get_bind()).get_columns("items")}
    if "low_notified" in cols:
        op.drop_column("items", "low_notified")
