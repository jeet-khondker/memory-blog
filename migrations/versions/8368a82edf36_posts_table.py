"""Posts Table

Revision ID: 8368a82edf36
Revises: 21c0ab7b178f
Create Date: 2020-04-07 19:29:46.181638

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8368a82edf36'
down_revision = '21c0ab7b178f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('MEMORYBLOG_TRANSACTION_POST', 'created_datetime',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.drop_index('ix_MEMORYBLOG_TRANSACTION_POST_created_datetime', table_name='MEMORYBLOG_TRANSACTION_POST')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_MEMORYBLOG_TRANSACTION_POST_created_datetime', 'MEMORYBLOG_TRANSACTION_POST', ['created_datetime'], unique=False)
    op.alter_column('MEMORYBLOG_TRANSACTION_POST', 'created_datetime',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    # ### end Alembic commands ###
