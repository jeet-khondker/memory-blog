"""Posts Table

Revision ID: ee693e4009d4
Revises: e1b473e9ca3f
Create Date: 2020-06-11 10:00:00.749224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee693e4009d4'
down_revision = 'e1b473e9ca3f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('MEMORYBLOG_TRANSACTION_POST', sa.Column('post_photo', sa.String(length=20), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('MEMORYBLOG_TRANSACTION_POST', 'post_photo')
    # ### end Alembic commands ###
