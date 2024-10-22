from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .models import User, Device, Log_sensors, Log_devices, Sensor

    db.init_app(app)
    with app.app_context():
        db.create_all()

    login_manager.init_app(app)

    from .views import main
    app.register_blueprint(main)

    return app
