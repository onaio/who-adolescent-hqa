"""reporting periods table

Revision ID: 240a53c8b88e
Revises: 168bf2f5034d
Create Date: 2014-03-10 11:41:47.060028

"""

# revision identifiers, used by Alembic.
revision = '240a53c8b88e'
down_revision = '168bf2f5034d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reporting_periods',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reporting_periods')
    ### end Alembic commands ###
