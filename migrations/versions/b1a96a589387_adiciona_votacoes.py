"""adiciona votacoes

Revision ID: b1a96a589387
Revises: 96c1033424de
Create Date: 2026-11-11 20:16:31.612943

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1a96a589387'
down_revision = '96c1033424de'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('votacoes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_original', sa.String(length=50), nullable=False),
    sa.Column('data', sa.Date(), nullable=False),
    sa.Column('horario', sa.Time(), nullable=True),
    sa.Column('objeto', sa.String(length=50), nullable=True),
    sa.Column('descricao', sa.Text(), nullable=False),
    sa.Column('aprovada', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_original')
    )
    with op.batch_alter_table('votacoes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_votacoes_data'), ['data'], unique=False)



def downgrade():
    with op.batch_alter_table('votacoes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_votacoes_data'))

    op.drop_table('votacoes')
