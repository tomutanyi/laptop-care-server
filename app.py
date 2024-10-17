from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Item  # Import your models directly
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Create the ItemResource class in app.py
class ItemResource(Resource):
    def get(self, item_id):
        item = Item.query.get_or_404(item_id)
        return {
            'id': item.id,
            'name': item.name,
            'second_name': item.second_name,  # Include second_name
            'description': item.description
        }

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('second_name', required=False)  # Add second_name argument
        parser.add_argument('description', required=False)
        data = parser.parse_args()

        new_item = Item(
            name=data['name'],
            second_name=data.get('second_name'),  # Use get to avoid KeyError
            description=data['description']
        )
        db.session.add(new_item)
        db.session.commit()
        return {'message': 'Item created', 'item_id': new_item.id}, 201

# Set up API routes
api = Api(app)
api.add_resource(ItemResource, '/item/<int:item_id>', '/item')

# Do not use db.create_all(); use migrations instead
if __name__ == '__main__':
    app.run(debug=True)
