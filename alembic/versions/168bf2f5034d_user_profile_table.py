"""user profile table

Revision ID: 168bf2f5034d
Revises: 4b7b8ed19a69
Create Date: 2014-03-05 12:06:26.766482

"""

# revision identifiers, used by Alembic.
revision = '168bf2f5034d'
down_revision = '4b7b8ed19a69'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_profiles',
    sa.Column('user_id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('pwd', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('username')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_profiles')
    ### end Alembic commands ###
