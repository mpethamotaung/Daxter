import random
from datetime import datetime, timedelta
from database import engine, SessionLocal
from models import Base, Payment, Invoice

def seed_data():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    # Clear existing
    session.query(Payment).delete()
    session.query(Invoice).delete()

    # 25 Payments
    for i in range(25):
        session.add(Payment(
            id=i+1,
            amount=round(random.uniform(100, 1000), 2),
            date=datetime.now() - timedelta(days=random.randint(1, 90)),
            status=random.choice(['paid', 'unpaid'])
        ))

    # 25 Invoices
    for i in range(25):
        session.add(Invoice(
            id=i+1,
            amount=round(random.uniform(200, 2000), 2),
            date=datetime.now() - timedelta(days=random.randint(1, 90)),
            status=random.choice(['paid', 'unpaid'])
        ))

    session.commit()
    session.close()
    print("Seeded 50 records!")