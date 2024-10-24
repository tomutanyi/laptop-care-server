"""creates devices table

Revision ID: 4e6f27c53697
Revises: 2d95b8c0cc2e
Create Date: 2024-10-18 21:01:06.172357

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e6f27c53697'
down_revision = '2d95b8c0cc2e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('devices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('device_serial_number', sa.String(length=50), nullable=False),
    sa.Column('device_model', sa.String(length=100), nullable=False),
    sa.Column('brand', sa.String(length=100), nullable=False),
    sa.Column('hdd_or_ssd', sa.Text(), nullable=True),
    sa.Column('hdd_or_ssd_serial_number', sa.String(length=50), nullable=True),
    sa.Column('memory', sa.String(length=50), nullable=True),
    sa.Column('memory_serial_number', sa.String(length=50), nullable=True),
    sa.Column('battery', sa.String(length=50), nullable=True),
    sa.Column('battery_serial_number', sa.String(length=50), nullable=True),
    sa.Column('adapter', sa.String(length=50), nullable=True),
    sa.Column('adapter_serial_number', sa.String(length=50), nullable=True),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('warranty_status', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('device_serial_number')
    )
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=121),
               type_=sa.String(length=255),
               existing_nullable=False)
        batch_op.drop_constraint('clients_email_key', type_='unique')
        batch_op.create_index(batch_op.f('ix_clients_email'), ['email'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_clients_email'))
        batch_op.create_unique_constraint('clients_email_key', ['email'])
        batch_op.alter_column('email',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=121),
               existing_nullable=False)

    op.drop_table('devices')
    # ### end Alembic commands ###
