from .handler import *

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    
    app = Flask(__name__)
    app.config.from_object(Config)

    from .models import User, Portfolio, Transaction, Order, Agent, Ticket

    db.init_app(app)
    with app.app_context():
        db.create_all()

    login_manager.init_app(app)

    from .views import main
    from .login import bp as login_router
    from .registration import bp as register_router
    from .agent_views import bp as agent_router

    app.register_blueprint(main)
    app.register_blueprint(login_router, url_prefix='/login')
    app.register_blueprint(register_router, url_prefix='/register')
    app.register_blueprint(agent_router, url_prefix='/agent')

    return app
