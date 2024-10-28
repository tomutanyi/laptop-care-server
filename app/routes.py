from flask_restx import Resource, Namespace, reqparse
from flask_jwt_extended import create_access_token
from . import db
from .models import Client, Device, Users, Jobcards
from datetime import timedelta


client_ns = Namespace('clients', description='Client related operations')
device_ns = Namespace('devices', description='Device related operations')
users_ns = Namespace('users', description='Users related operations')
jobcards_ns = Namespace('jobcards', description='Jobcards related operations')


client_parser = reqparse.RequestParser()
client_parser.add_argument('name', type=str, required=True, help='Name of the client')
client_parser.add_argument('email', type=str, required=True, help='Email of the client')
client_parser.add_argument('phone_number', type=str, required=True, help='Phone number of the client')
client_parser.add_argument('address', type=str, help='Address of the client')

device_parser = reqparse.RequestParser()
device_parser.add_argument('device_serial_number', type=str, required=True, help='Device serial number')
device_parser.add_argument('device_model', type=str, required=True, help='Device model')
device_parser.add_argument('brand', type=str, required=True, help='Brand of the device')
device_parser.add_argument('hdd_or_ssd', type=str, help='Type of storage (HDD or SSD)')
device_parser.add_argument('hdd_or_ssd_serial_number', type=str, help='HDD or SSD serial number')
device_parser.add_argument('memory', type=str, help='Memory information')
device_parser.add_argument('memory_serial_number', type=str, help='Memory serial number')
device_parser.add_argument('battery', type=str, help='Battery information')
device_parser.add_argument('battery_serial_number', type=str, help='Battery serial number')
device_parser.add_argument('adapter', type=str, help='Adapter information')
device_parser.add_argument('adapter_serial_number', type=str, help='Adapter serial number')
device_parser.add_argument('client_id', type=int, required=True, help='Client ID associated with the device')
device_parser.add_argument('warranty_status', type=bool, default=False, help='Warranty status of the device')

users_parser = reqparse.RequestParser()
users_parser.add_argument('username', type=str, required=True, help='Username for authentication')
users_parser.add_argument('password', type=str, required=True, help='Password for authentication')
users_parser.add_argument('email', type=str, required=True, help='Email of the User')
users_parser.add_argument('role', type=str, required=True, help='Role of the User (admin or user)')


login_parser = reqparse.RequestParser()
login_parser.add_argument('username', type=str, required=True, help='Username for login')
login_parser.add_argument('password', type=str, required=True, help='Password for login')

jobcards_parser = reqparse.RequestParser()
jobcards_parser.add_argument('device_id', type=int, required=True, help='Device ID associated with the jobcard')
jobcards_parser.add_argument('problem_description', type=str, required=True, help='Job description for the jobcard')
jobcards_parser.add_argument('status', type=str, required=True, help='Status of the jobcard')



# Client routes
@client_ns.route('', endpoint='clients')
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

@client_ns.route('/<int:client_id>', endpoint='clients/<int:client_id>')
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


# Device routes
@device_ns.route('', endpoint='devices')
class DeviceListResource(Resource):
    def get(self):
        """Retrieve a list of devices."""
        devices = Device.query.all()
        return [device.to_dict() for device in devices], 200

    def post(self):
        """Create a new device."""
        data = device_parser.parse_args()
        new_device = Device(
            device_serial_number=data['device_serial_number'],
            device_model=data['device_model'],
            brand=data['brand'],
            hdd_or_ssd=data.get('hdd_or_ssd'),
            hdd_or_ssd_serial_number=data.get('hdd_or_ssd_serial_number'),
            memory=data.get('memory'),
            memory_serial_number=data.get('memory_serial_number'),
            battery=data.get('battery'),
            battery_serial_number=data.get('battery_serial_number'),
            adapter=data.get('adapter'),
            adapter_serial_number=data.get('adapter_serial_number'),
            client_id=data['client_id'],
            warranty_status=data.get('warranty_status', False)
        )
        db.session.add(new_device)
        db.session.commit()
        return new_device.to_dict(), 201

@device_ns.route('/<int:device_id>', endpoint='devices/<int:device_id>')
class DeviceResource(Resource):
    def get(self, device_id):
        """Retrieve a device by ID."""
        device = Device.query.get_or_404(device_id)
        return device.to_dict(), 200

    def put(self, device_id):
        """Update a device by ID."""
        device = Device.query.get_or_404(device_id)
        data = device_parser.parse_args()
        device.device_serial_number = data['device_serial_number']
        device.device_model = data['device_model']
        device.brand = data['brand']
        device.hdd_or_ssd = data.get('hdd_or_ssd')
        device.hdd_or_ssd_serial_number = data.get('hdd_or_ssd_serial_number')
        device.memory = data.get('memory')
        device.memory_serial_number = data.get('memory_serial_number')
        device.battery = data.get('battery')
        device.battery_serial_number = data.get('battery_serial_number')
        device.adapter = data.get('adapter')
        device.adapter_serial_number = data.get('adapter_serial_number')
        device.client_id = data['client_id']
        device.warranty_status = data.get('warranty_status', False)
        db.session.commit()
        return device.to_dict(), 200

    def delete(self, device_id):
        """Delete a device by ID."""
        device = Device.query.get_or_404(device_id)
        db.session.delete(device)
        db.session.commit()
        return '', 204
    

# Users routes
@users_ns.route('', endpoint='users')
class UserListResource(Resource):
    def get(self):
        """Retrieve a list of users."""
        users = Users.query.all()
        return [user.to_dict(rules=('-password',)) for user in users], 200

    def post(self):
        """Create a new user."""
        data = users_parser.parse_args()
        
        # Create a new user instance
        new_user = Users(
            username=data['username'],
            email=data['email'],
            role=data['role']
        )
        
        # Hash and set the password
        new_user.set_password(data['password'])
        
        # Add the user to the session and commit
        db.session.add(new_user)
        db.session.commit()
        
        return new_user.to_dict(rules=('-password',)), 201

@users_ns.route('/<int:user_id>', endpoint='users/<int:user_id>')
class UserResource(Resource):
    def get(self, user_id):
        """Retrieve a user by ID."""
        user = Users.query.get_or_404(user_id)
        return user.to_dict(rules=('-password',)), 200

    def delete(self, user_id):
        """Delete a user by ID."""
        user = Users.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return 'Deleted User', 204
    

@users_ns.route('/login', endpoint='login')
class UserLoginResource(Resource):
    def post(self):
        """Authenticate user and return a JWT."""
        data = login_parser.parse_args()
        user = Users.query.filter_by(username=data['username']).first()

        if not user or not user.check_password(data['password']):
            return {'message': 'Invalid username or password'}, 401
        
        # Generate a JWT access token
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))

        return {
            'access_token': access_token,
            'username': user.username,
            'id': user.id,
            'role': user.role, 
            'message': 'Login successful'
        }, 200
    

@jobcards_ns.route('', endpoint='jobcards')
class JobcardsResource(Resource):
    def get(self):
        """Retrieve a list of jobcards with an optional status filter."""
        # Parse the optional status argument
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str, help='Status of the jobcard')
        args = parser.parse_args()

        # Apply filter if status argument is provided
        if args['status']:
            jobcards = Jobcards.query.filter_by(status=args['status']).all()
        else:
            jobcards = Jobcards.query.all()  # Retrieve all job cards if no status filter is provided

        # Serialize and return the filtered job cards
        return [jobcard.to_dict() for jobcard in jobcards], 200
     
    def post(self):
        """Create a new jobcard."""
        data = jobcards_parser.parse_args()
        new_jobcard = Jobcards(
            problem_description=data['problem_description'],
            status=data['status'],
            device_id=data['device_id']
        )
        db.session.add(new_jobcard)
        db.session.commit()
        return new_jobcard.to_dict(), 201

@jobcards_ns.route('/<int:jobcard_id>/details', endpoint='jobcard_details')
class JobcardDetailsResource(Resource):
    def get(self, jobcard_id):
        """Retrieve client and device details for a specific jobcard."""
        jobcard = Jobcards.query.get_or_404(jobcard_id)
        details = jobcard.get_client_device_info()
        
        if details:
            return details, 200
        else:
            return {"message": "Details not found for the specified jobcard."}, 404