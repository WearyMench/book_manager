# Book Manager API

A Flask-based RESTful API for managing books with features like input validation, rate limiting, logging, and API documentation.

## Features

- RESTful API endpoints for CRUD operations on books
- Input validation using Marshmallow
- Rate limiting to prevent abuse
- Comprehensive logging system
- Swagger/OpenAPI documentation
- Environment-specific configurations
- Error handling
- CORS support
- Unit tests

## Installation

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: .\env\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Create a .env file with your configuration:
```
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=sqlite:///books.db
FLASK_ENV=development
```

## Running the Application

Development mode:
```bash
flask run
```

Production mode:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Documentation

Once running, visit `http://localhost:5000/` to access the Swagger UI documentation.

## Testing

Run tests using pytest:
```bash
pytest
```

## API Endpoints

- GET /books - List all books
- POST /books - Create a new book
- PUT /books/{id} - Update a book
- DELETE /books/{id} - Delete a book

## Rate Limits

- List books: 100 requests per hour
- Create/Update/Delete: 20 requests per hour
- Overall: 200 requests per day

## Directory Structure

```
.
├── app.py              # Main application file
├── config.py           # Configuration settings
├── models.py           # Database models
├── schemas.py          # Validation schemas
├── errors.py          # Error handling
├── logging.py         # Logging configuration
├── tests/             # Test files
├── logs/              # Log files
└── requirements.txt   # Project dependencies
```