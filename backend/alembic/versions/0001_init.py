"""База целиком из моделей (стартовая)."""
from alembic import op
import sqlalchemy as sa
from app.core.db import Base
import app.models  # noqa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

def downgrade():
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
