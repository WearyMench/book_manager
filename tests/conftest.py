import pytest
from app import app as flask_app
from models import db, Book

@pytest.fixture
def app():
    flask_app.config.from_object('config.TestingConfig')
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def sample_book():
    book = Book(
        title="Test Book",
        author="Test Author",
        published_date="2024-01-01",
        summary="Test Summary"
    )
    db.session.add(book)
    db.session.commit()
    return book