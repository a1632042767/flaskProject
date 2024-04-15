"""empty message

Revision ID: 3b797f1efdd9
Revises: e9f43f9847de
Create Date: 2024-04-15 22:27:24.353992

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3b797f1efdd9'
down_revision = 'e9f43f9847de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('baiducookie', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('userinfobybaidu', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('userinfobydouding', schema=None) as batch_op:
        batch_op.alter_column('cookies',
               existing_type=mysql.TEXT(),
               nullable=True)
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('userinfobydouding', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('cookies',
               existing_type=mysql.TEXT(),
               nullable=False)

    with op.batch_alter_table('userinfobybaidu', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('baiducookie', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###