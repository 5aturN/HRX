"""Флаг low_notified: о низком остатке уже писали (защита от спама)."""
from alembic import op
import sqlalchemy as sa

revision = "0005_low_notified"
down_revision = "0004_favs"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("items", sa.Column("low_notified", sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade():
    op.drop_column("items", "low_notified")
