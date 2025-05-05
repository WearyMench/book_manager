from flask_restx import Namespace, Resource, fields, reqparse
from flask import request, current_app
from models import Book, db
from schemas import BookSchema
from errors import ValidationError
import logging

# Initialize API namespace
api = Namespace('v1', description='API v1 endpoints')

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

# API Models
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

bulk_books_model = api.model('BulkBooks', {
    'books': fields.List(fields.Nested(book_model), required=True, description='List of books')
})

# Routes
@api.route('/books')
class BookList(Resource):
    @api.doc('list_books')
    @api.expect(pagination_parser)
    @api.response(200, 'Success', pagination_response)
    @current_app.cache.cached(timeout=300, query_string=True)
    def get(self):
        """List all books with pagination and search"""
        try:
            logging.info("Fetching books with pagination")
            args = pagination_parser.parse_args()
            page = args['page']
            per_page = args['per_page']
            sort_field = args['sort']
            order = args['order']
            search_query = args['q']

            query = Book.query

            if search_query:
                query = Book.search(search_query)

            if sort_field:
                sort_column = getattr(Book, sort_field)
                if order == 'desc':
                    sort_column = sort_column.desc()
                query = query.order_by(sort_column)

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
            logging.error(f"Error fetching books: {str(e)}")
            raise ValidationError(str(e))

    @api.doc('create_book')
    @api.expect(book_model)
    def post(self):
        """Create a new book"""
        try:
            data = request.get_json()
            logging.info(f"Creating new book with data: {data}")
            
            errors = book_schema.validate(data)
            if errors:
                logging.warning(f"Validation error in book creation: {errors}")
                raise ValidationError(str(errors))
                
            new_book = Book(
                title=data['title'],
                author=data['author'],
                published_date=data.get('published_date'),
                summary=data.get('summary')
            )
            db.session.add(new_book)
            db.session.commit()

            # Invalidate cache
            current_app.cache.delete('books')
            
            logging.info(f"Successfully created book with ID: {new_book.id}")
            return {
                "status": "success",
                "message": "Book created successfully",
                "data": book_schema.dump(new_book)
            }, 201
        except Exception as e:
            logging.error(f"Error creating book: {str(e)}")
            db.session.rollback()
            raise ValidationError(str(e))

@api.route('/books/<int:book_id>')
@api.param('book_id', 'The book identifier')
class BookResource(Resource):
    @api.doc('get_book')
    @api.response(200, 'Success', book_model)
    @current_app.cache.cached(timeout=300, key_prefix='book')
    def get(self, book_id):
        """Get a book by ID"""
        try:
            logging.info(f"Fetching book with ID: {book_id}")
            book = Book.query.get_or_404(book_id)
            return {
                "status": "success",
                "data": book_schema.dump(book)
            }, 200
        except Exception as e:
            logging.error(f"Error fetching book: {str(e)}")
            raise ValidationError(str(e))

    @api.doc('update_book')
    @api.expect(book_model)
    def put(self, book_id):
        """Update a book"""
        try:
            logging.info(f"Updating book with ID: {book_id}")
            book = Book.query.get_or_404(book_id)
            data = request.get_json()
            
            errors = book_schema.validate(data)
            if errors:
                logging.warning(f"Validation error in book update: {errors}")
                raise ValidationError(str(errors))
                
            book.title = data.get('title', book.title)
            book.author = data.get('author', book.author)
            book.published_date = data.get('published_date', book.published_date)
            book.summary = data.get('summary', book.summary)
            
            db.session.commit()

            # Invalidate cache
            current_app.cache.delete(f'book{book_id}')
            current_app.cache.delete('books')

            logging.info(f"Successfully updated book with ID: {book_id}")
            return {
                "status": "success",
                "message": "Book updated successfully",
                "data": book_schema.dump(book)
            }, 200
        except Exception as e:
            logging.error(f"Error updating book: {str(e)}")
            db.session.rollback()
            raise ValidationError(str(e))

    @api.doc('delete_book')
    def delete(self, book_id):
        """Delete a book"""
        try:
            logging.info(f"Deleting book with ID: {book_id}")
            book = Book.query.get_or_404(book_id)
            db.session.delete(book)
            db.session.commit()

            # Invalidate cache
            current_app.cache.delete(f'book{book_id}')
            current_app.cache.delete('books')

            logging.info(f"Successfully deleted book with ID: {book_id}")
            return {
                "status": "success",
                "message": "Book deleted successfully"
            }, 200
        except Exception as e:
            logging.error(f"Error deleting book: {str(e)}")
            db.session.rollback()
            raise ValidationError(str(e))

@api.route('/books/bulk')
class BulkBookOperations(Resource):
    @api.doc('bulk_create_books')
    @api.expect(bulk_books_model)
    def post(self):
        """Create multiple books in a single request"""
        try:
            data = request.get_json()
            logging.info(f"Creating {len(data['books'])} books in bulk")
            
            books_data = data['books']
            errors = []
            new_books = []
            
            for idx, book_data in enumerate(books_data):
                book_errors = book_schema.validate(book_data)
                if book_errors:
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
                logging.warning(f"Validation errors in bulk creation: {errors}")
                return {
                    "status": "error",
                    "message": "Validation errors occurred",
                    "errors": errors
                }, 400
                
            db.session.bulk_save_objects(new_books)
            db.session.commit()

            # Invalidate cache
            current_app.cache.delete('books')
            
            logging.info(f"Successfully created {len(new_books)} books in bulk")
            return {
                "status": "success",
                "message": f"Successfully created {len(new_books)} books",
                "data": books_schema.dump(new_books)
            }, 201
            
        except Exception as e:
            logging.error(f"Error in bulk book creation: {str(e)}")
            db.session.rollback()
            raise ValidationError(str(e))

    @api.doc('bulk_delete_books')
    def delete(self):
        """Delete multiple books in a single request"""
        try:
            data = request.get_json()
            book_ids = data.get('ids', [])
            
            if not book_ids:
                raise ValidationError("No book IDs provided")
                
            logging.info(f"Deleting books with IDs: {book_ids}")
            
            deleted_count = Book.query.filter(Book.id.in_(book_ids)).delete(synchronize_session=False)
            db.session.commit()

            # Invalidate cache
            current_app.cache.delete('books')
            for book_id in book_ids:
                current_app.cache.delete(f'book{book_id}')
            
            logging.info(f"Successfully deleted {deleted_count} books")
            return {
                "status": "success",
                "message": f"Successfully deleted {deleted_count} books"
            }, 200
            
        except Exception as e:
            logging.error(f"Error in bulk book deletion: {str(e)}")
            db.session.rollback()
            raise ValidationError(str(e))