"""empty message

Revision ID: 5447e0973b83
Revises: cc9102b340b7
Create Date: 2024-04-15 12:07:35.233026

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5447e0973b83'
down_revision = 'cc9102b340b7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('baiducookie', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('download', sa.String(length=50), nullable=True))

    with op.batch_alter_table('userinfbybaidu', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('userinfbybaidu', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('download')

    with op.batch_alter_table('baiducookie', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###
