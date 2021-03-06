"""added user groups

Revision ID: 4a6f22c2db3c
Revises: 13458cc4ea0
Create Date: 2014-02-17 23:07:37.034688

"""

# revision identifiers, used by Alembic.
revision = '4a6f22c2db3c'
down_revision = '13458cc4ea0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_groups',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'ona_users', 'refresh_token')
    op.drop_table('user_groups')
    op.drop_table('groups')
    ### end Alembic commands ###
