"""add book indexes

Revision ID: add_book_indexes
Revises: 37bc8a3bfe99
Create Date: 2024-02-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_book_indexes'
down_revision = '37bc8a3bfe99'
branch_labels = None
depends_on = None

def upgrade():
    # Create indexes for commonly searched fields
    op.create_index('idx_book_title', 'book', ['title'])
    op.create_index('idx_book_author', 'book', ['author'])
    op.create_index('idx_book_published_date', 'book', ['published_date'])

def downgrade():
    # Remove indexes
    op.drop_index('idx_book_title', table_name='book')
    op.drop_index('idx_book_author', table_name='book')
    op.drop_index('idx_book_published_date', table_name='book')