from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PaymentSchema(BaseModel):
    id: int
    amount: float
    date: datetime
    status: str

class InvoiceSchema(BaseModel):
    id: int
    amount: float
    date: datetime
    status: str

class SummarySchema(BaseModel):
    total_payments: float
    unpaid_invoices: float
    monthly: List[dict]  # [{"month": 10, "total": 5000}]

class QuerySchema(BaseModel):
    query: str

class LogEntry(BaseModel):
    type: str
    timestamp: datetime
    error: Optional[str] = None