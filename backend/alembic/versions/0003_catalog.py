"""Каталог стандартов: эталонные фото и имена по DIN/ISO/ГОСТ."""
from alembic import op
import sqlalchemy as sa

revision = "0003_catalog"
down_revision = "0002_photos"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("std_catalog",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("std_code", sa.String(50), nullable=False, unique=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("descr", sa.String(500), nullable=True),
        sa.Column("photo_path", sa.String(500), nullable=True),
    )
    op.add_column("items", sa.Column("std_code", sa.String(50), nullable=True))
    op.create_index("ix_item_std", "items", ["std_code"])

def downgrade():
    op.drop_index("ix_item_std", table_name="items")
    op.drop_column("items", "std_code")
    op.drop_table("std_catalog")
