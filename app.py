from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restx import Api, Resource, fields, reqparse
from flask_migrate import Migrate
from flask_caching import Cache
from config import Config
from models import db, Book
from schemas import BookSchema
from errors import ValidationError, handle_validation_error, handle_http_error, handle_generic_error
from logging_config import setup_logger
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize caching
cache = Cache(app)

# Initialize API documentation
api = Api(app, version='1.0', title='Book Manager API',
          description='A simple book management API')

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Setup logging
logger = setup_logger()

# Error handlers
app.register_error_handler(ValidationError, handle_validation_error)
app.register_error_handler(HTTPException, handle_http_error)
app.register_error_handler(Exception, handle_generic_error)

# Initialize schemas
book_schema = BookSchema()
books_schema = BookSchema(many=True)

# Request parsers
pagination_parser = reqparse.RequestParser()
pagination_parser.add_argument('page', type=int, default=1, help='Page number')
pagination_parser.add_argument('per_page', type=int, default=10, help='Items per page')
pagination_parser.add_argument('sort', type=str, choices=('title', 'author', 'published_date'), help='Sort field')
pagination_parser.add_argument('order', type=str, choices=('asc', 'desc'), default='asc', help='Sort order')
pagination_parser.add_argument('q', type=str, help='Search query')

# API Models for documentation
book_model = api.model('Book', {
    'title': fields.String(required=True, description='Book title'),
    'author': fields.String(required=True, description='Book author'),
    'published_date': fields.String(description='Publication date (YYYY-MM-DD)'),
    'summary': fields.String(description='Book summary')
})

pagination_response = api.model('PaginatedResponse', {
    'status': fields.String(description='Response status'),
    'data': fields.List(fields.Nested(book_model)),
    'page': fields.Integer(description='Current page number'),
    'per_page': fields.Integer(description='Items per page'),
    'total_pages': fields.Integer(description='Total number of pages'),
    'total_items': fields.Integer(description='Total number of items')
})

# Add new API model for bulk operations
bulk_books_model = api.model('BulkBooks', {
    'books': fields.List(fields.Nested(book_model), required=True, description='List of books')
})

def create_tables():
    with app.app_context():
        db.create_all()

# API Routes
@api.route('/books')
class BookList(Resource):
    @api.doc('list_books')
    @api.expect(pagination_parser)
    @api.response(200, 'Success', pagination_response)
    @limiter.limit("100/hour")
    @cache.cached(timeout=300, query_string=True)  # Cache for 5 minutes, include query params in cache key
    def get(self):
        """List all books with pagination and search"""
        try:
            logger.info("Fetching books with pagination")
            args = pagination_parser.parse_args()
            page = args['page']
            per_page = args['per_page']
            sort_field = args['sort']
            order = args['order']
            search_query = args['q']

            # Start with base query
            query = Book.query

            # Apply search if specified
            if search_query:
                query = Book.search(search_query)

            # Apply sorting if specified
            if sort_field:
                sort_column = getattr(Book, sort_field)
                if order == 'desc':
                    sort_column = sort_column.desc()
                query = query.order_by(sort_column)

            # Apply pagination
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            return {
                "status": "success",
                "data": books_schema.dump(pagination.items),
                "page": page,
                "per_page": per_page,
                "total_pages": pagination.pages,
                "total_items": pagination.total,
                "search_query": search_query if search_query else None
            }, 200
        except Exception as e:
            logger.error(f"Error fetching books: {str(e)}")
            raise ValidationError(str(e))

    @api.doc('create_book')
    @api.expect(book_model)
    @limiter.limit("20/hour")
    def post(self):
        """Create a new book"""
        try:
            data = request.get_json()
            logger.info(f"Creating new book with data: {data}")
            
            errors = book_schema.validate(data)
            if errors:
                logger.warning(f"Validation error in book creation: {errors}")
                raise ValidationError(str(errors))
                
            new_book = Book(
                title=data['title'],
                author=data['author'],
                published_date=data.get('published_date'),
                summary=data.get('summary')
            )
            db.session.add(new_book)
            db.session.commit()
            
            logger.info(f"Successfully created book with ID: {new_book.id}")
            return {
                "status": "success",
                "message": "Book created successfully",
                "data": book_schema.dump(new_book)
            }, 201
        except Exception as e:
            logger.error(f"Error creating book: {str(e)}")
            db.session.rollback()
            raise ValidationError(str(e))

@api.route('/books/<int:book_id>')
@api.param('book_id', 'The book identifier')
class BookResource(Resource):
    @api.doc('update_book')
    @api.expect(book_model)
    @limiter.limit("20/hour")
    def put(self, book_id):
        """Update a book"""
        try:
            logger.info(f"Updating book with ID: {book_id}")
            book = Book.query.get_or_404(book_id)
            data = request.get_json()
            
            errors = book_schema.validate(data)
            if errors:
                logger.warning(f"Validation error in book update: {errors}")
                raise ValidationError(str(errors))
                
            book.title = data.get('title', book.title)
            book.author = data.get('author', book.author)
            book.published_date = data.get('published_date', book.published_date)
            book.summary = data.get('summary', book.summary)
            
            db.session.commit()
            # Invalidate cache entries after modification
            cache.delete(f'book{book_id}')
            cache.delete('books')  # Invalidate the cached list
            logger.info(f"Successfully updated book with ID: {book_id}")
            return {
                "status": "success",
                "message": "Book updated successfully",
                "data": book_schema.dump(book)
            }, 200
        except Exception as e:
            logger.error(f"Error updating book: {str(e)}")
            db.session.rollback()
            raise ValidationError(str(e))

    @api.doc('delete_book')
    @limiter.limit("20/hour")
    def delete(self, book_id):
        """Delete a book"""
        try:
            logger.info(f"Deleting book with ID: {book_id}")
            book = Book.query.get_or_404(book_id)
            db.session.delete(book)
            db.session.commit()
            # Invalidate cache entries after modification
            cache.delete(f'book{book_id}')
            cache.delete('books')  # Invalidate the cached list
            logger.info(f"Successfully deleted book with ID: {book_id}")
            return {
                "status": "success",
                "message": "Book deleted successfully"
            }, 200
        except Exception as e:
            logger.error(f"Error deleting book: {str(e)}")
            db.session.rollback()
            raise ValidationError(str(e))

    @api.doc('get_book')
    @api.response(200, 'Success', book_model)
    @cache.cached(timeout=300, key_prefix='book')  # Cache individual book responses
    def get(self, book_id):
        """Get a book by ID"""
        try:
            logger.info(f"Fetching book with ID: {book_id}")
            book = Book.query.get_or_404(book_id)
            return {
                "status": "success",
                "data": book_schema.dump(book)
            }, 200
        except Exception as e:
            logger.error(f"Error fetching book: {str(e)}")
            raise ValidationError(str(e))

# Add new route for bulk operations
@api.route('/books/bulk')
class BulkBookOperations(Resource):
    @api.doc('bulk_create_books')
    @api.expect(bulk_books_model)
    @limiter.limit("10/hour")
    def post(self):
        """Create multiple books in a single request"""
        try:
            data = request.get_json()
            logger.info(f"Creating {len(data['books'])} books in bulk")
            
            books_data = data['books']
            errors = []
            new_books = []
            
            for idx, book_data in enumerate(books_data):
                book_errors = book_schema.validate(book_data)
                if (book_errors):
                    errors.append({
                        'index': idx,
                        'errors': book_errors
                    })
                else:
                    new_book = Book(
                        title=book_data['title'],
                        author=book_data['author'],
                        published_date=book_data.get('published_date'),
                        summary=book_data.get('summary')
                    )
                    new_books.append(new_book)
            
            if errors:
                logger.warning(f"Validation errors in bulk creation: {errors}")
                return {
                    "status": "error",
                    "message": "Validation errors occurred",
                    "errors": errors
                }, 400
                
            db.session.bulk_save_objects(new_books)
            db.session.commit()
            
            logger.info(f"Successfully created {len(new_books)} books in bulk")
            return {
                "status": "success",
                "message": f"Successfully created {len(new_books)} books",
                "data": books_schema.dump(new_books)
            }, 201
            
        except Exception as e:
            logger.error(f"Error in bulk book creation: {str(e)}")
            db.session.rollback()
            raise ValidationError(str(e))

    @api.doc('bulk_delete_books')
    @limiter.limit("10/hour")
    def delete(self):
        """Delete multiple books in a single request"""
        try:
            data = request.get_json()
            book_ids = data.get('ids', [])
            
            if not book_ids:
                raise ValidationError("No book IDs provided")
                
            logger.info(f"Deleting books with IDs: {book_ids}")
            
            deleted_count = Book.query.filter(Book.id.in_(book_ids)).delete(synchronize_session=False)
            db.session.commit()
            
            logger.info(f"Successfully deleted {deleted_count} books")
            return {
                "status": "success",
                "message": f"Successfully deleted {deleted_count} books"
            }, 200
            
        except Exception as e:
            logger.error(f"Error in bulk book deletion: {str(e)}")
            db.session.rollback()
            raise ValidationError(str(e))

@api.route('/')
class Home(Resource):
    @api.doc('home')
    def get(self):
        """Home endpoint"""
        logger.info("Home endpoint accessed")
        return {
            "status": "success",
            "message": "Welcome to the Book Manager API",
            "version": "1.0"
        }

if __name__ == '__main__':
    app.run(debug=True)