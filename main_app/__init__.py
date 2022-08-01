from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import config

database = SQLAlchemy()
app = Flask(__name__)
login_manager = LoginManager()
login_manager.login_view = "auth_bp.login"
login_manager.login_message = "Vous devez vous authentifier pour utiliser ce service"


def create_app(config_name):
    app.config.from_object(config[config_name])
    login_manager.init_app(app)
    database.init_app(app)
    from main_app.employee import employee_bp
    app.register_blueprint(employee_bp)
    from main_app.admin import admin_bp
    app.register_blueprint(admin_bp)
    from main_app.auth import auth_bp
    app.register_blueprint(auth_bp)
    return app



