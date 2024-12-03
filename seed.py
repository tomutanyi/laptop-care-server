from faker import Faker
from app import app, db 
from app.models import Client, Device, Users, Jobcards

fake = Faker()

def seed_clients(n=10):
    """Seeds clients into the database."""
    for _ in range(n):
        client = Client(
            name=fake.name(),
            email=fake.unique.email(),
            phone_number=fake.phone_number(),
            address=fake.address()
        )
        db.session.add(client)
    db.session.commit()

def seed_devices(n=10):
    """Seeds devices into the database."""
    clients = Client.query.all() 

    for _ in range(n):
        if clients: 
            client = fake.random_element(elements=clients)
            device = Device(
                device_serial_number=fake.unique.uuid4(),
                device_model=fake.word(),
                brand=fake.company(),
                hdd_or_ssd=fake.word(),
                hdd_or_ssd_serial_number=fake.unique.uuid4(),
                memory=fake.word(),
                memory_serial_number=fake.unique.uuid4(),
                battery=fake.word(),
                battery_serial_number=fake.unique.uuid4(),
                adapter=fake.word(),
                adapter_serial_number=fake.unique.uuid4(),
                client_id=client.id,
                warranty_status=fake.boolean()
            )
            db.session.add(device)
    db.session.commit()

def seed_clients(n=10):
    """Seeds clients into the database."""
    for _ in range(n):
        client = Client(
            name=fake.name(),
            email=fake.unique.email(),
            phone_number=fake.phone_number(),
            address=fake.address()
        )
        db.session.add(client)
    db.session.commit()

def seed_devices(n=20):
    """Seeds devices into the database."""
    clients = Client.query.all()  # Fetch all clients

    for _ in range(n):
        if clients:
            client = fake.random_element(elements=clients)
            device = Device(
                device_serial_number=fake.unique.uuid4(),
                device_model=fake.word(),
                brand=fake.company(),
                hdd_or_ssd=fake.word(),
                hdd_or_ssd_serial_number=fake.unique.uuid4(),
                memory=fake.word(),
                memory_serial_number=fake.unique.uuid4(),
                battery=fake.word(),
                battery_serial_number=fake.unique.uuid4(),
                adapter=fake.word(),
                adapter_serial_number=fake.unique.uuid4(),
                client_id=client.id,
                warranty_status=fake.boolean()
            )
            db.session.add(device)
    db.session.commit()

def seed_users(n=10):
    """Seeds users into the database."""
    roles = ["admin", "clerk", "technician"]  # Define possible roles

    for _ in range(n):
        user = Users(
            email=fake.unique.email(),
            username=fake.user_name(),
            password=fake.password(),  # Plaintext password
            role=fake.random_element(elements=roles)
        )

        db.session.add(user)
    db.session.commit()

def seed_jobcards():
    # Ensure there are devices to reference; if not, you'll need to create devices first.
    device1 = Device.query.first()  # Assuming there is at least one device in the database.
    if not device1:
        print("No devices found. Add devices first before seeding jobcards.")
        return

    # Create jobcards for the existing device (replace `device1.id` with valid device IDs)
    jobcard1 = Jobcards(
        problem_description="Battery not charging",
        status="Pending",
        device_id=device1.id
    )
    jobcard2 = Jobcards(
        problem_description="Screen flickering",
        status="In Progress",
        device_id=device1.id
    )
    jobcard3 = Jobcards(
        problem_description="Keyboard malfunction",
        status="Completed",
        device_id=device1.id
    )

    db.session.add_all([jobcard1, jobcard2, jobcard3])
    db.session.commit()



if __name__ == '__main__':
    with app.app_context():
        # Clear out existing data in tables
        # Device.query.delete()
        # Client.query.delete()
        # Users.query.delete()

        db.session.commit()


        # seed_clients(10)
        # seed_devices(20)
        # seed_users(10)
        seed_jobcards()     

        print("Database seeded successfully!")
