from flask import jsonify
from werkzeug.exceptions import HTTPException

class ValidationError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

def handle_validation_error(e):
    return jsonify({"error": e.message}), e.status_code

def handle_http_error(e):
    return jsonify({"error": str(e)}), e.status_code

def handle_generic_error(e):
    return jsonify({"error": "An unexpected error occurred"}), 500