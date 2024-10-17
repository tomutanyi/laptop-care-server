from faker import Faker
from sqlalchemy.orm import sessionmaker
from app import create_app, db 
from app.models import Client

fake = Faker()

app = create_app()

def get_session():
    """Creates a new session for interacting with the database."""
    Session = sessionmaker(bind=db.engine)
    return Session()

def seed_clients(n=10):
    with get_session() as session: 
        for _ in range(n):
            client = Client(
                name=fake.name(),
                email=fake.unique.email(),
                phone_number=fake.phone_number(),
                address=fake.address()
            )
            session.add(client)
        session.commit()



if __name__ == '__main__':
    with app.app_context():
        try:
            seed_clients(20)
            
            print("Database seeded successfully!")
        except Exception as e:
            print(f"An error occurred while seeding the database: {e}")
