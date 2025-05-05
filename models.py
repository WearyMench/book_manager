from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, Index

db = SQLAlchemy()

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    published_date = db.Column(db.String(10), nullable=True)
    summary = db.Column(db.Text, nullable=True)

    # Add indexes for commonly searched fields
    __table_args__ = (
        Index('idx_book_title', 'title'),
        Index('idx_book_author', 'author'),
        Index('idx_book_published_date', 'published_date'),
    )

    @classmethod
    def search(cls, query):
        """Search books by title, author, or summary"""
        return cls.query.filter(
            or_(
                cls.title.ilike(f"%{query}%"),
                cls.author.ilike(f"%{query}%"),
                cls.summary.ilike(f"%{query}%")
            )
        )