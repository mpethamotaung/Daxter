from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base
from datetime import datetime

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    date = Column(DateTime)
    status = Column(String, default="paid")  # 'paid' or 'unpaid'

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    date = Column(DateTime)
    status = Column(String, default="unpaid")