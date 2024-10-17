from flask import Flask
from flask_restful import Api
from models import db
from resources import ItemResource
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db.init_app(app)

# Set up API routes
api = Api(app)
api.add_resource(ItemResource, '/item/<int:item_id>', '/item')

# Create the tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
