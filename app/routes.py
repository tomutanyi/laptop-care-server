from flask import request, current_app, jsonify, send_file
from flask_restx import Resource, Namespace, reqparse
from flask_jwt_extended import create_access_token
from . import db
from .models import Client, Device, Users, Jobcards
from .email_service import email_service
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import os
import io
from datetime import datetime, timedelta


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
jobcards_parser.add_argument('assigned_technician_id', type=int, required=False, help='Technician ID for assignment')

# Parser for updating cost and diagnostic
jobcard_update_parser = reqparse.RequestParser()
jobcard_update_parser.add_argument('cost', type=int, required=False, help='Cost of the repair')
jobcard_update_parser.add_argument('diagnostic', type=str, required=False, help='Diagnostic information')


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
    
@client_ns.route('/search', endpoint='clients_search')
class ClientSearchResource(Resource):
    def get(self):
        """Search for a client by phone number."""
        parser = reqparse.RequestParser()
        parser.add_argument('phone_number', type=str, required=True, help="Phone number to search for")
        args = parser.parse_args()

        # Query the database for clients with the given phone number
        client = Client.query.filter_by(phone_number=args['phone_number']).first()
        
        if client:
            return client.to_dict(), 200
        else:
            return {'message': 'Client not found'}, 404



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
    
@device_ns.route('/search', endpoint='devices_search')
class DeviceSearchResource(Resource):
    def get(self):
        """Search for a device by serial number."""
        parser = reqparse.RequestParser()
        parser.add_argument('device_serial_number', type=str, required=True, help='Device serial number to search for')
        args = parser.parse_args()

        # Query the database for the device with the given serial number
        device = Device.query.filter_by(device_serial_number=args['device_serial_number']).first()
        
        if device:
            return device.to_dict(), 200
        else:
            return {'message': 'Device not found'}, 404

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
    
@users_ns.route('/technicians', endpoint='technicians') #Endpoint to fetch all technicians
class TechnicianListResource(Resource):
    def get(self):
        """Retrieve a list of users with the role of technician."""
        technicians = Users.query.filter_by(role='technician').all()
        return [technician.to_dict(rules=('-password',)) for technician in technicians], 200
    

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
        """Retrieve a list of jobcards with optional status and assigned technician ID filters."""
        # Parse the optional status and assigned technician ID arguments
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str, help='Status of the jobcard')
        parser.add_argument('assigned_technician_id', type=int, help='Technician ID assigned to the jobcard')
        args = parser.parse_args()

        # Build the query with optional filters
        query = Jobcards.query
        
        if args['status']:
            query = query.filter_by(status=args['status'])
        
        if args['assigned_technician_id']:
            query = query.filter_by(assigned_technician_id=args['assigned_technician_id'])

        # Retrieve filtered job cards
        jobcards = query.all()

        # Get additional client and device details for each job card
        jobcards_with_details = []
        for jobcard in jobcards:
            jobcard_details = jobcard.to_dict()  # Assuming you have a `to_dict` method on Jobcards
            client_device_info = jobcard.get_client_device_info()  # Get client and device info

            if client_device_info:
                jobcard_details.update(client_device_info)  # Add client and device info to the jobcard details

            jobcards_with_details.append(jobcard_details)

        # Serialize and return the filtered job cards with client and device details
        return jobcards_with_details, 200


     
    def post(self):
        """Create a new jobcard."""
        data = jobcards_parser.parse_args()

        print("Data received from front end for posting:", data)
        print("Assigned technician ID:", data.get('assigned_technician_id'))  # Log assigned_technician_id specifically

        new_jobcard = Jobcards(
            problem_description=data['problem_description'],
            status=data['status'],
            device_id=data['device_id'],
            assigned_technician_id=data.get('assigned_technician_id'),
        )
        db.session.add(new_jobcard)
        db.session.commit()

        # Get client and device details for the email
        client_info = new_jobcard.get_client_device_info()
        email_sent = False
        
        # Log the client info retrieval
        if client_info is None:
            print(f"WARNING: No client info found for jobcard ID {new_jobcard.id}")
            print(f"Device ID: {new_jobcard.device_id}")
            
            # Additional debugging: check the device and client
            device = Device.query.get(new_jobcard.device_id)
            if device:
                print(f"Device found: {device}")
                print(f"Device client ID: {device.client_id}")
                
                client = Client.query.get(device.client_id)
                if client:
                    print(f"Client found: {client}")
                    print(f"Client email: {client.email}")
        
        if client_info:
            try:
                email_sent = email_service.send_jobcard_notification(
                    client_name=client_info['client_name'],
                    client_email=client_info['client_email'],
                    jobcard_id=new_jobcard.id,
                    problem_description=new_jobcard.problem_description,
                    device_model=client_info['device_model'],
                    device_brand=client_info['device_brand']
                )
            except Exception as e:
                print(f"Error sending email notification: {str(e)}")

        # Return jobcard details along with email sending status
        response = new_jobcard.to_dict()
        response['email_sent'] = email_sent

        return response, 201

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
        
@jobcards_ns.route('/<int:jobcard_id>/status', endpoint='update_jobcard_status')
class JobcardStatusUpdateResource(Resource):
    def patch(self, jobcard_id):
        """Update the status of a jobcard."""
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str, required=True, help='New status for the jobcard')
        args = parser.parse_args()

        # Find the jobcard by ID
        jobcard = Jobcards.query.get_or_404(jobcard_id)

        # Update the status field
        jobcard.status = args['status']
        db.session.commit()

        return {'message': 'Jobcard status updated successfully', 'jobcard': jobcard.to_dict()}, 200

@jobcards_ns.route('/<int:jobcard_id>/update', endpoint='update_jobcard_details')
class JobcardUpdateResource(Resource):
    def patch(self, jobcard_id):
        """Update the status, cost and/or diagnostic of a jobcard."""
        jobcard = Jobcards.query.get_or_404(jobcard_id)
        data = request.get_json()
        
        # Track what fields were updated
        updated_fields = []
        
        if 'status' in data:
            valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
            if data['status'] not in valid_statuses:
                return {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}, 400
            jobcard.status = data['status']
            updated_fields.append('status')
            
        if 'cost' in data:
            if not isinstance(data['cost'], (int, float)) or data['cost'] < 0:
                return {'error': 'Cost must be a non-negative number'}, 400
            jobcard.cost = data['cost']
            updated_fields.append('cost')
            
        if 'diagnostic' in data:
            if not isinstance(data['diagnostic'], str):
                return {'error': 'Diagnostic must be a string'}, 400
            jobcard.diagnostic = data['diagnostic']
            updated_fields.append('diagnostic')
            
        if not updated_fields:
            return {'error': 'No valid fields to update provided'}, 400

        try:
            db.session.commit()
            return {
                'message': 'Jobcard updated successfully',
                'updated_fields': updated_fields,
                'jobcard': jobcard.to_dict()
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

def generate_invoice_pdf(invoice_data):
    """
    Generate a PDF invoice from the provided invoice data
    
    :param invoice_data: Dictionary containing invoice details
    :return: BytesIO object with PDF content
    """
    # Create a buffer for the PDF
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Company Header
    elements.append(Paragraph("Laptop Care Service", styles['Title']))
    elements.append(Paragraph("Invoice", styles['Heading2']))
    
    # Company Details
    company_details = [
        ["Laptop Care Service"],
        ["Nairobi, Kenya"],
        ["Phone: +254 (0) 700 000 000"],
        ["Email: support@laptopcare.com"]
    ]
    company_details_table = Table(company_details, colWidths=[6*inch])
    company_details_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    elements.append(company_details_table)
    
    # Client Information
    client_info = [
        ["Bill To:", "Invoice Details:"],
        [invoice_data['client_name'], f"Invoice Number: {invoice_data['jobcard_id']}"],
        [invoice_data['client_email'], f"Date: {datetime.now().strftime('%Y-%m-%d')}"],
        [invoice_data['device_info'], ""]
    ]
    client_info_table = Table(client_info, colWidths=[3*inch, 3*inch])
    client_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
    ]))
    elements.append(client_info_table)
    
    # Invoice Items
    items_data = [['Type', 'Description', 'Quantity', 'Unit Price', 'Total']]
    total_amount = 0
    for item in invoice_data['items']:
        # Default quantity to 1 if not specified
        quantity = item.get('quantity', 1)
        unit_price = float(item['price'])
        item_total = quantity * unit_price
        total_amount += item_total
        
        items_data.append([
            item['type'].capitalize(), 
            item['description'], 
            str(quantity),
            f"Ksh {unit_price:,.2f}", 
            f"Ksh {item_total:,.2f}"
        ])
    
    # Add total row
    items_data.append(['', '', '', 'Total:', f"Ksh {total_amount:,.2f}"])
    
    items_table = Table(items_data, colWidths=[1*inch, 3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(items_table)
    
    # Additional Notes
    elements.append(Paragraph("Thank you for your business!", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Move buffer pointer to the beginning
    buffer.seek(0)
    return buffer

@jobcards_ns.route('/generate-invoice', endpoint='generate_invoice')
class InvoiceGenerationResource(Resource):
    def post(self):
        data = request.get_json()
        required_fields = ['jobcard_id', 'client_name', 'client_email', 'device_info', 'items', 'total']
        
        # Validate required fields
        for field in required_fields:
            if field not in data:
                return {'error': f'Missing required field: {field}'}, 400

        try:
            # Generate PDF
            pdf_buffer = generate_invoice_pdf(data)
            
            # Prepare email body with PDF details
            email_html_body = f'''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4;">
                    <h2 style="color: #2c3e50;">Invoice for Job Card #{data['jobcard_id']}</h2>
                    <p>Dear {data['client_name']},</p>
                    
                    <p>Please find attached the invoice for your recent laptop repair service.</p>
                    
                    <div style="margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: white;">
                        <p><strong>Job Card ID:</strong> {data['jobcard_id']}</p>
                        <p><strong>Device:</strong> {data['device_info']}</p>
                        <p><strong>Total Cost:</strong> Ksh {float(data['total']):,.2f}</p>
                    </div>
                    
                    <p>Thank you for choosing Laptop Care Service!</p>
                </div>
            </body>
            </html>
            '''
            
            # Save PDF to a file
            pdf_filename = f"invoice_{data['jobcard_id']}.pdf"
            pdf_path = os.path.join(current_app.root_path, 'invoices', pdf_filename)
            
            # Ensure invoices directory exists
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            with open(pdf_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            
            # Send email using email service with PDF attachment
            email_service.send_email(
                subject=f"Invoice for Job Card #{data['jobcard_id']}", 
                recipient=data['client_email'], 
                html_body=email_html_body,
                attachments=[{
                    'filename': pdf_filename,
                    'content': pdf_buffer.getvalue(),
                    'subtype': 'pdf'
                }]
            )
            
            # Return PDF as a response
            return send_file(
                pdf_buffer, 
                mimetype='application/pdf', 
                as_attachment=True, 
                download_name=pdf_filename
            )
            
        except Exception as e:
            current_app.logger.error(f"Invoice generation error: {str(e)}")
            return {'error': str(e)}, 500
