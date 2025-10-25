from flask import Flask 
from flask_cors import CORS
from .resources import users_bp
from .views.home import bp 


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)    
    
    # app.register_blueprint(users_bp, prefix="/api")
    app.register_blueprint(bp)    
    
    return app
    
    