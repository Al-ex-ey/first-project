"""First migration

Revision ID: 27a5da488326
Revises: 
Create Date: 2024-06-18 23:14:38.073705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27a5da488326'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('arenda',
    sa.Column('ФИО арендатора', sa.String(length=100), nullable=True),
    sa.Column('contract', sa.String(length=100), nullable=True),
    sa.Column('debet', sa.Integer(), nullable=True),
    sa.Column('credit', sa.Integer(), nullable=True),
    sa.Column('insurance_fee', sa.Integer(), nullable=True),
    sa.Column('note', sa.String(length=400), nullable=True),
    sa.Column('business_type', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.Column('email2', sa.String(length=50), nullable=True),
    sa.Column('email3', sa.String(length=50), nullable=True),
    sa.Column('phone_nomber', sa.String(length=60), nullable=True),
    sa.Column('phone_nomber2', sa.String(length=60), nullable=True),
    sa.Column('phone_nomber3', sa.String(length=60), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('contract')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('arenda')
    # ### end Alembic commands ###
