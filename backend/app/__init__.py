from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
import os
import atexit

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL', 'postgresql://marketmind_user:marketmind_pass@postgres:5432/marketmind')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
        'connect_args': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'
        }
    }
    app.config['db'] = db
    app.config['DAYS_TO_KEEP'] = int(os.getenv('DAYS_TO_KEEP', 90))
    
    db.init_app(app)
    
    # Initialize Swagger
    swagger = Swagger(app, template={
        'swagger': '2.0',
        'info': {
            'title': 'GlobeMarketMind API',
            'description': 'Global market sentiment analysis system',
            'version': '1.0.0'
        },
        'basePath': '/api'
    })
    
    with app.app_context():
        # Import models to register them with SQLAlchemy
        from app.models.market import MarketRegistry, DailyState, CorrelationEdge
        
        # Create tables
        db.create_all()
        
        # Register blueprints
        from app.api.data_bp import data_bp
        from app.api.process_bp import process_bp
        from app.api.history_bp import history_bp
        from app.api.scheduler_bp import scheduler_bp
        
        app.register_blueprint(data_bp)
        app.register_blueprint(process_bp)
        app.register_blueprint(history_bp)
        app.register_blueprint(scheduler_bp)
        
        # Initialize scheduler
        from app.services.scheduler import init_scheduler, shutdown_scheduler
        init_scheduler(app)
        
        # Register shutdown handler
        atexit.register(shutdown_scheduler)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return {'status': 'OK'}, 200
    
    return app
