"""Фото позиций и аватары."""
from alembic import op
import sqlalchemy as sa

revision = "0002_photos"
down_revision = "0001_init"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("items", sa.Column("photo_path", sa.String(500), nullable=True))
    op.add_column("users", sa.Column("avatar_path", sa.String(500), nullable=True))

def downgrade():
    op.drop_column("items", "photo_path")
    op.drop_column("users", "avatar_path")
