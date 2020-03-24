"""Posts Transaction Table

Revision ID: 21c0ab7b178f
Revises: 86e8d995bbd4
Create Date: 2020-03-25 07:15:07.400047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21c0ab7b178f'
down_revision = '86e8d995bbd4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('MEMORYBLOG_TRANSACTION_POST',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('body', sa.String(length=150), nullable=True),
    sa.Column('created_datetime', sa.DateTime(), nullable=True),
    sa.Column('updated_datetime', sa.DateTime(), nullable=True),
    sa.Column('image', sa.String(length=20), nullable=True),
    sa.Column('video', sa.String(length=20), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['MEMORYBLOG_MASTER_USER.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_MEMORYBLOG_TRANSACTION_POST_created_datetime'), 'MEMORYBLOG_TRANSACTION_POST', ['created_datetime'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_MEMORYBLOG_TRANSACTION_POST_created_datetime'), table_name='MEMORYBLOG_TRANSACTION_POST')
    op.drop_table('MEMORYBLOG_TRANSACTION_POST')
    # ### end Alembic commands ###
