"""Add reporting_period form_xpath

Revision ID: 1963d6d14bfd
Revises: 1720bf033c80
Create Date: 2015-05-13 09:24:17.178894

"""

# revision identifiers, used by Alembic.
revision = '1963d6d14bfd'
down_revision = '1720bf033c80'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('reporting_periods', sa.Column(
        'form_xpath', sa.String(length=100), nullable=True))


def downgrade():
    op.drop_column('reporting_periods', 'form_xpath')
