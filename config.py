import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'prima-default-dev-secret-key-bps-banyuwangi')
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads', 'documents')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 32 * 1024 * 1024)) # 32 MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'pptx'}
    
    # Database configuration
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'prima_akip_banyuwangi')
    
    # Priority: explicit DATABASE_URL, else construct MySQL URL
    raw_db_url = os.environ.get('DATABASE_URL')
    if raw_db_url and raw_db_url.startswith('postgres://'):
        # Fix legacy postgres:// URI for SQLAlchemy compatibility
        raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)
        
    DEFAULT_MYSQL_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    SQLALCHEMY_DATABASE_URI = raw_db_url or DEFAULT_MYSQL_URI
    
    # SQLite fallback path (use system temp directory on Vercel/serverless)
    IS_VERCEL = bool(os.environ.get('VERCEL'))
    import tempfile
    if IS_VERCEL:
        sqlite_tmp_path = os.path.join(tempfile.gettempdir(), 'prima_akip.db').replace('\\', '/')
        SQLITE_URI = f"sqlite:///{sqlite_tmp_path}"
        UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(tempfile.gettempdir(), 'uploads'))
    else:
        SQLITE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'prima_akip.db')}"
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads', 'documents')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    }
    
    ITEMS_PER_PAGE = 10

class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

