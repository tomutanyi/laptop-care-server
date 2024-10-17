from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db  # assuming your models are defined in models.py
from resources import ItemResource
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Set up API routes
api = Api(app)
api.add_resource(ItemResource, '/item/<int:item_id>', '/item')

# Do not use db.create_all(); use migrations instead
if __name__ == '__main__':
    app.run(debug=True)
