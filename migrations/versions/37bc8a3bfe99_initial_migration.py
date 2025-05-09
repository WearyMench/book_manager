"""Initial migration

Revision ID: 37bc8a3bfe99
Revises: 
Create Date: 2025-05-05 12:36:49.040282

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37bc8a3bfe99'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('book',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('author', sa.String(length=100), nullable=False),
    sa.Column('published_date', sa.String(length=10), nullable=True),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.create_index('idx_book_author', ['author'], unique=False)
        batch_op.create_index('idx_book_published_date', ['published_date'], unique=False)
        batch_op.create_index('idx_book_title', ['title'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('book', schema=None) as batch_op:
        batch_op.drop_index('idx_book_title')
        batch_op.drop_index('idx_book_published_date')
        batch_op.drop_index('idx_book_author')

    op.drop_table('book')
    # ### end Alembic commands ###
