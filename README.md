# Book Manager API

A Flask-based RESTful API for managing books with features like input validation, rate limiting, logging, and API documentation.

## Features

- RESTful API endpoints for CRUD operations on books
- Input validation using Marshmallow
- Rate limiting to prevent abuse
- Swagger/OpenAPI documentation
- Error handling
- CORS support
- Unit tests

## Installation

### Option 1: Local Installation

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
- `FLASK_ENV`: Application environment (development)
- `SECRET_KEY`: Flask secret key
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: PostgreSQL database name
- `SQLALCHEMY_DATABASE_URI`: Database connection string

### Option 2: Docker Installation

1. Make sure you have Docker and Docker Compose installed
2. Clone the repository
3. Build and run the containers:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:5000`

## Database Migrations

Initialize the database:
```bash
flask db upgrade
```

Create a new migration after model changes:
```bash
flask db migrate -m "Migration description"
flask db upgrade
```

## Running the Application

### Local Development

Development mode:
```bash
flask run
```

Production mode:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

Start the application:
```bash
docker-compose up
```

Run in detached mode:
```bash
docker-compose up -d
```

Stop the application:
```bash
docker-compose down
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