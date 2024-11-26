from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import func, DateTime
from datetime import datetime
import pytz
import re

utc_now = datetime.now(pytz.utc)
nairobi_tz = pytz.timezone('Africa/Nairobi')
nairobi_now = utc_now.astimezone(nairobi_tz)

db = SQLAlchemy()
bcrypt = Bcrypt()

class Client(db.Model, SerializerMixin):
    __tablename__ = 'clients'
    serialize_rules = ('-devices.client',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(40), nullable=False)
    address = db.Column(db.String(300), nullable=True)

    devices = db.relationship('Device', backref='client', lazy=True, cascade="all, delete-orphan")

    def __init__(self, name, email, phone_number, address=None):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.address = address
        
        self.validate_fields()

    def get_jobcards(self):
        """Retrieve all job cards associated with this client."""
        return Jobcards.query.join(Device).filter(Device.client_id == self.id).all()


    def validate_fields(self):
        """Validate the client's fields."""
        if not self.name:
            raise ValueError("Name is required.")
        
        if not self.email:
            raise ValueError("Email is required.")
        
        if not self.is_valid_email(self.email):
            raise ValueError("Invalid email format.")

        if not self.phone_number:
            raise ValueError("Phone number is required.")

    @staticmethod
    def is_valid_email(email):
        """Check if the email is valid."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def __repr__(self):
        return f'<Client {self.name}>'

    def __str__(self):
        return f'{self.name} ({self.email})'


class Device(db.Model, SerializerMixin):
    __tablename__ = 'devices'
    serialize_rules = ('-client.devices',)

    id = db.Column(db.Integer, primary_key=True)
    device_serial_number = db.Column(db.String(50), unique=True, nullable=False)
    device_model = db.Column(db.String(100), nullable=False)  
    brand = db.Column(db.String(100), nullable=False) 
    hdd_or_ssd = db.Column(db.Text, nullable=True)
    hdd_or_ssd_serial_number = db.Column(db.String(50), nullable=True)
    memory = db.Column(db.String(50), nullable=True)
    memory_serial_number = db.Column(db.String(50), nullable=True)
    battery = db.Column(db.String(50), nullable=True)
    battery_serial_number = db.Column(db.String(50), nullable=True)
    adapter = db.Column(db.String(50), nullable=True) 
    adapter_serial_number = db.Column(db.String(50), nullable=True) 
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    warranty_status = db.Column(db.String(100), nullable=False) 

    def __repr__(self):
        return f'<Device {self.brand}>'

    def __str__(self):
        return f'{self.device_model} - {self.brand}'
    
    
class Users(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules =  ('-jobcards.user',) 

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), nullable=False)

    jobcards = db.relationship('Jobcards', backref='user', lazy=True, cascade="all, delete-orphan")

    # This hides the password from the db
    # @property
    # def password(self):
    #     raise AttributeError("Password is not a readable attribute.")

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Checks a password against the stored hash."""
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def __str__(self):
        return f'{self.username} - {self.role}'

class Jobcards(db.Model, SerializerMixin):
    __tablename__ = 'jobcards'
    serialize_rules = ('-device.jobcards',)
    id = db.Column(db.Integer, primary_key=True)
    problem_description = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    diagnostic = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(DateTime, default=lambda: datetime.now(pytz.timezone('Africa/Nairobi')))  # Add the timestamp column
    cost = db.Column(db.Integer, nullable=True)
    assigned_technician_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def get_client_device_info(self):
        """Retrieve client name, client email, device model, and device brand for this jobcard."""
    
        client_info = (
            db.session.query(
                Client.name.label('client_name'),
                Client.email.label('client_email'),
                Device.device_model.label('device_model'),
                Device.brand.label('device_brand'),
                Jobcards.status.label('jobcards_status')

            )
            .select_from(Jobcards) 
            .join(Device, Jobcards.device_id == Device.id)
            .join(Client, Device.client_id == Client.id) 
            .filter(Jobcards.id == self.id)    
            .first()
        )

        if client_info:
            return {
                "client_name": client_info.client_name,
                "client_email": client_info.client_email,
                "device_model": client_info.device_model,
                "device_brand": client_info.device_brand,
                "jobcards_status": client_info.jobcards_status
            }
        

        return None
    

    @property
    def local_timestamp(self):
        """Returns the timestamp in the Nairobi timezone."""
        return self.timestamp.astimezone(pytz.timezone('Africa/Nairobi'))
    
    def __str__(self):
        return f"Jobcard(id={self.id}, problem='{self.problem_description}', status='{self.status}', timestamp='{self.timestamp}')"

    def __repr__(self):
        return f"<Jobcard(id={self.id}, problem='{self.problem_description}', status='{self.status}', timestamp='{self.timestamp}')>"




    