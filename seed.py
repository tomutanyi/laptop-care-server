from faker import Faker
from app import app, db 
from app.models import Client, Device

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

if __name__ == '__main__':
    with app.app_context():
        
        Device.query.delete()
        Client.query.delete()

    
        db.session.commit()

        seed_clients(10)  
        seed_devices(20)

        print("Database seeded successfully!")