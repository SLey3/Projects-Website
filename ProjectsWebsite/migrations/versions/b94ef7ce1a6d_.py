"""empty message

Revision ID: b94ef7ce1a6d
Revises: 
Create Date: 2021-07-14 10:13:09.924104

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b94ef7ce1a6d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('article',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('author', sa.String(length=100), nullable=True),
    sa.Column('create_date', sa.String(length=100), nullable=True),
    sa.Column('short_description', sa.String(length=150), nullable=True),
    sa.Column('title_img', sa.String(length=500), nullable=True),
    sa.Column('body', sa.String(length=900), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('blacklist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('person', sa.String(length=100), nullable=False),
    sa.Column('reason', sa.String(length=255), nullable=True),
    sa.Column('date', sa.String(length=30), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('person')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blacklist')
    op.drop_table('article')
    # ### end Alembic commands ###
