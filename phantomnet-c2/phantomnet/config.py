import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with environment variable support"""

    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TESTING = False

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///phantom_c2.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0,
    }
    
    # Cloud SQL specific configuration
    if 'cloudsql' in SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_ENGINE_OPTIONS.update({
            'pool_size': 5,
            'max_overflow': 2,
            'pool_timeout': 30,
            'pool_recycle': 1800,
        })

    # Server configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8443))
    SSL_CERT_PATH = os.getenv('SSL_CERT_PATH')
    SSL_KEY_PATH = os.getenv('SSL_KEY_PATH')
    SSL_CONTEXT = 'adhoc' if not SSL_CERT_PATH else (SSL_CERT_PATH, SSL_KEY_PATH)

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.getenv('SESSION_TIMEOUT', 86400)))
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'phantom.log')

    # API Keys (set via environment variables)
    SHODAN_API_KEY = os.getenv('SHODAN_API_KEY', '')
    CENSYS_API_ID = os.getenv('CENSYS_API_ID', '')
    CENSYS_API_SECRET = os.getenv('CENSYS_API_SECRET', '')
    VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY', '')
    ABUSEIPDB_API_KEY = os.getenv('ABUSEIPDB_API_KEY', '')
    OTX_API_KEY = os.getenv('OTX_API_KEY', '')

    # C2 Server configuration
    C2_SERVER_IP = os.getenv('C2_SERVER_IP', '127.0.0.1')
    C2_SERVER_PORT = os.getenv('C2_SERVER_PORT', '8443')

    # DuckDNS configuration
    DUCKDNS_DOMAIN = os.getenv('DUCKDNS_DOMAIN', '')
    DUCKDNS_TOKEN = os.getenv('DUCKDNS_TOKEN', '')

    # Background task intervals
    BACKGROUND_TASK_INTERVAL = int(os.getenv('BACKGROUND_TASK_INTERVAL', 300))
    BOT_INACTIVE_TIMEOUT = int(os.getenv('BOT_INACTIVE_TIMEOUT', 7200))
    DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', 30))

    # Payload generation
    MSFVENOM_PATH = os.getenv('MSFVENOM_PATH', '/usr/bin/msfvenom')

    # Security settings
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    LOCKOUT_DURATION = int(os.getenv('LOCKOUT_DURATION', 900))
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 8))

    # Rate limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 3600))

    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///phantom_c2_dev.db')
    LOG_LEVEL = 'DEBUG'
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class by name"""
    return config.get(config_name or 'default', config['default'])