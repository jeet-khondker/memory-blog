"""Posts Table

Revision ID: 259fb3608d1a
Revises: 45e3bceff535
Create Date: 2020-05-18 09:46:04.316101

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '259fb3608d1a'
down_revision = '45e3bceff535'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('MEMORYBLOG_TRANSACTION_POST', sa.Column('post_photo', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('MEMORYBLOG_TRANSACTION_POST', 'post_photo')
    # ### end Alembic commands ###
