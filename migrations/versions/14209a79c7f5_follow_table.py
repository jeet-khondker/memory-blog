"""Follow Table

Revision ID: 14209a79c7f5
Revises: 0df76665473d
Create Date: 2020-04-16 20:06:33.895874

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14209a79c7f5'
down_revision = '0df76665473d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('MEMORYBLOG_ASSOCIATION_FOLLOW',
    sa.Column('follower_id', sa.Integer(), nullable=False),
    sa.Column('followed_id', sa.Integer(), nullable=False),
    sa.Column('follow_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['MEMORYBLOG_MASTER_USER.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['MEMORYBLOG_MASTER_USER.id'], ),
    sa.PrimaryKeyConstraint('follower_id', 'followed_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('MEMORYBLOG_ASSOCIATION_FOLLOW')
    # ### end Alembic commands ###