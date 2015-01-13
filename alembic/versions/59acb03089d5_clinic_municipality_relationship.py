"""Clinic municipality relationship

Revision ID: 59acb03089d5
Revises: 193bc40f1fae
Create Date: 2015-01-08 16:02:04.364603

"""

# revision identifiers, used by Alembic.
revision = '59acb03089d5'
down_revision = '193bc40f1fae'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'clinics', sa.Column('municipality_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('clinics', 'municipality_id')
    ### end Alembic commands ###
