"""empty message

Revision ID: 101a6f7ce91b
Revises: d507962ffda0
Create Date: 2018-11-12 15:09:53.651224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '101a6f7ce91b'
down_revision = 'd507962ffda0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('evaluate', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'evaluate')
    # ### end Alembic commands ###
