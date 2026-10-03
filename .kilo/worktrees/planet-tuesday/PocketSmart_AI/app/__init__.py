from flask import Flask
from app.config import config
from app.database import db
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

def create_app(config_name="default"):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Register blueprints
    from app.routes.pages import pages_bp
    from app.routes.auth import auth_bp
    from app.routes.recommendations import recommendations_bp
    
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(recommendations_bp, url_prefix='/planner')
    
    return app
