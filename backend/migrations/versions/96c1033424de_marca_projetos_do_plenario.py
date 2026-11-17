"""marca projetos do plenario

Revision ID: 96c1033424de
Revises: 2b29b25c976e
Create Date: 2026-11-11 19:58:42.417985

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96c1033424de'
down_revision = '2b29b25c976e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('projetos_lei', schema=None) as batch_op:
        batch_op.add_column(sa.Column('no_plenario', sa.Boolean(), server_default=sa.text('0'), nullable=False))



def downgrade():
    with op.batch_alter_table('projetos_lei', schema=None) as batch_op:
        batch_op.drop_column('no_plenario')

