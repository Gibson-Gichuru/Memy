"""empty message

Revision ID: 39dc828b1617
Revises: 6cfa6afd25b2
Create Date: 2021-07-10 12:16:50.531616

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '39dc828b1617'
down_revision = '6cfa6afd25b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('files', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.add_column('files', sa.Column('post_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'files', 'posts', ['post_id'], ['id'])
    op.create_foreign_key(None, 'files', 'users', ['owner_id'], ['id'])
    op.drop_constraint('posts_ibfk_2', 'posts', type_='foreignkey')
    op.drop_column('posts', 'file_id')
    op.drop_constraint('users_ibfk_1', 'users', type_='foreignkey')
    op.drop_column('users', 'file_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('file_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('users_ibfk_1', 'users', 'files', ['file_id'], ['id'])
    op.add_column('posts', sa.Column('file_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('posts_ibfk_2', 'posts', 'files', ['file_id'], ['id'])
    op.drop_constraint(None, 'files', type_='foreignkey')
    op.drop_constraint(None, 'files', type_='foreignkey')
    op.drop_column('files', 'post_id')
    op.drop_column('files', 'owner_id')
    # ### end Alembic commands ###