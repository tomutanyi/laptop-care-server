from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_restx import Api
from .config import Config
from .models import Client, db


jwt = JWTManager()
bcrypt = Bcrypt()
api = Api()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    api.init_app(app)
    migrate.init_app(app, db)

    from .routes import client_ns
    api.add_namespace(client_ns)
    return app
