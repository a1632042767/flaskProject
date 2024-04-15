"""empty message

Revision ID: e27a4ebe4beb
Revises: 5447e0973b83
Create Date: 2024-04-15 12:08:09.924878

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e27a4ebe4beb'
down_revision = '5447e0973b83'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('baiducookie', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('downloadpath', sa.String(length=50), nullable=True))
        batch_op.drop_column('download')

    with op.batch_alter_table('userinfbybaidu', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('userinfbybaidu', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('download', mysql.VARCHAR(length=50), nullable=True))
        batch_op.drop_column('downloadpath')

    with op.batch_alter_table('baiducookie', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###
