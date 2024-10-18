from flask import request
from flask_restx import Resource, Namespace, reqparse
from . import db
from .models import Client

client_ns = Namespace('clients', description='Client related operations')

client_parser = reqparse.RequestParser()
client_parser.add_argument('name', type=str, required=True, help='Name of the client')
client_parser.add_argument('email', type=str, required=True, help='Email of the client')
client_parser.add_argument('phone_number', type=str, required=True, help='Phone number of the client')
client_parser.add_argument('address', type=str, help='Address of the client')

@client_ns.route('/')
class ClientListResource(Resource):
    def get(self):
        """Retrieve a list of clients."""
        clients = Client.query.all()
        return [client.to_dict() for client in clients], 200

    def post(self):
        """Create a new client."""
        data = client_parser.parse_args()
        new_client = Client(
            name=data['name'],
            email=data['email'],
            phone_number=data['phone_number'],
            address=data.get('address')
        )
        db.session.add(new_client)
        db.session.commit()
        return new_client.to_dict(), 201

@client_ns.route('/<int:client_id>')
class ClientResource(Resource):
    def get(self, client_id):
        """Retrieve a client by ID."""
        client = Client.query.get_or_404(client_id)
        return client.to_dict(), 200

    def put(self, client_id):
        """Update a client by ID."""
        client = Client.query.get_or_404(client_id)
        data = client_parser.parse_args()
        client.name = data['name']
        client.email = data['email']
        client.phone_number = data['phone_number']
        client.address = data.get('address')
        db.session.commit()
        return client.to_dict(), 200

    def delete(self, client_id):
        """Delete a client by ID."""
        client = Client.query.get_or_404(client_id)
        db.session.delete(client)
        db.session.commit()
        return '', 204
