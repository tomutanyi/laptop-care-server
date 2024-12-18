"""made cost nullable

Revision ID: ab9637ff838f
Revises: 3b7c5bd46805
Create Date: 2024-11-16 15:50:07.220128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab9637ff838f'
down_revision = '3b7c5bd46805'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('jobcards', schema=None) as batch_op:
        batch_op.alter_column('cost',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('jobcards', schema=None) as batch_op:
        batch_op.alter_column('cost',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
