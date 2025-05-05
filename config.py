import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Rate limiting storage
    RATELIMIT_STORAGE_URL = "memory://"
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    # API Documentation
    SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTX_MASK_SWAGGER = False
    # Cache configuration
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')  # Use Redis in production
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_KEY_PREFIX = 'book_manager_'

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///dev.db')
    # More permissive CORS in development
    CORS_HEADERS = 'Content-Type'
    # Use simple cache in development
    CACHE_TYPE = 'simple'

class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    # Disable CSRF protection in testing
    WTF_CSRF_ENABLED = False
    # Disable caching in testing
    CACHE_TYPE = 'null'

class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    # Stricter CORS in production
    CORS_HEADERS = 'Content-Type'
    CORS_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')
    # Use Redis cache in production if configured
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    CACHE_REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    CACHE_REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    CACHE_REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Set the active configuration
Config = config[os.getenv('FLASK_ENV', 'default')]