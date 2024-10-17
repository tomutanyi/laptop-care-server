from flask_restful import Resource, reqparse
from models import Item, db

class ItemResource(Resource):
    def get(self, item_id):
        item = Item.query.get_or_404(item_id)
        return {'id': item.id, 'name': item.name, 'description': item.description}

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('description', required=False)
        data = parser.parse_args()

        new_item = Item(name=data['name'], description=data['description'])
        db.session.add(new_item)
        db.session.commit()
        return {'message': 'Item created', 'item': new_item.id}, 201
