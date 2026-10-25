"""Избранное (идемпотентно)."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0004_favs"
down_revision = "0003_catalog"
branch_labels = None
depends_on = None

def upgrade():
    if "favorites" not in set(inspect(op.get_bind()).get_table_names()):
        op.create_table("favorites",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("item_id", sa.Integer, sa.ForeignKey("items.id", ondelete="CASCADE"), nullable=False),
            sa.UniqueConstraint("user_id", "item_id", name="uq_fav_user_item"),
        )

def downgrade():
    if "favorites" in set(inspect(op.get_bind()).get_table_names()):
        op.drop_table("favorites")
