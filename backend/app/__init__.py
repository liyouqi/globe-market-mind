from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL', 'postgresql://marketmind_user:marketmind_pass@postgres:5432/marketmind')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Register blueprints
        from app.api.data_bp import bp as data_bp
        from app.api.process_bp import bp as process_bp
        
        app.register_blueprint(data_bp)
        app.register_blueprint(process_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'OK'}, 200
    
    return app
