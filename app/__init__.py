from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_restx import Api
from flask_cors import CORS
from .config import Config
from .models import Client, db
from .email_service import email_service

jwt = JWTManager()
bcrypt = Bcrypt()
migrate = Migrate()
api = Api(title='Laptop Care API', version='1.0', description='A laptop repair management API')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    api.init_app(app)
    migrate.init_app(app, db)

    # Start email service
    email_service.start_email_service()

    # Apply CORS to the app
    CORS(app, origins=["http://localhost:3000", "https://laptop-care-client.vercel.app"], supports_credentials=True)

    from .routes import client_ns, device_ns, users_ns, jobcards_ns
    api.add_namespace(client_ns)
    api.add_namespace(device_ns)
    api.add_namespace(users_ns)
    api.add_namespace(jobcards_ns)

    return app

app = create_app()
