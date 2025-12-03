from fastapi import FastAPI, Depends, Query
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
from typing import Optional, List
import random  

from database import engine, get_db
from models import Base, Payment, Invoice
from schemas import PaymentSchema, InvoiceSchema, SummarySchema, QuerySchema, LogEntry
from seeder import seed_data

app = FastAPI(title="Daxter OpenTax POC")

logs: List[dict] = []  # In-memory logs

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Drop tables to avoid stale state, then create fresh
    print("Dropping old tables if any...")
    Base.metadata.drop_all(bind=engine)
    # Startup: Create tables and seed data
    print("Creating fresh tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created, seeding data...")
    seed_data()
    print("Startup complete: Tables created and data seeded.")
    yield
    print("App shutdown complete")

app = FastAPI(title="Daxter OpenTax POC", lifespan=lifespan)

logs: List[dict] = []  # In-memory logs

@app.get("/api/payments", response_model=List[PaymentSchema])
def get_payments(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None
):
    query = db.query(Payment)
    if start_date: query = query.filter(Payment.date >= start_date)
    if end_date: query = query.filter(Payment.date <= end_date)
    if status: query = query.filter(Payment.status == status)
    payments = query.order_by(Payment.date.desc()).offset(offset).limit(limit).all()
    logs.append({"type": "payments", "timestamp": datetime.now().isoformat(), "count": len(payments)})
    return payments

@app.get("/api/invoices", response_model=List[InvoiceSchema])
def get_invoices(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Invoice)
    if start_date: query = query.filter(Invoice.date >= start_date)
    if end_date: query = query.filter(Invoice.date <= end_date)
    if status: query = query.filter(Invoice.status == status)
    invoices = query.order_by(Invoice.date.desc()).offset(offset).limit(limit).all()
    logs.append({"type": "invoices", "timestamp": datetime.now().isoformat(), "count": len(invoices)})
    return invoices

@app.get("/api/summary", response_model=SummarySchema)
def get_summary(db: Session = Depends(get_db)):
    total_payments = db.query(func.sum(Payment.amount)).scalar() or 0.0
    unpaid_invoices = db.query(func.sum(Invoice.amount)).filter(Invoice.status == 'unpaid').scalar() or 0.0
    monthly = db.query(
        extract('month', Payment.date).label('month'),
        func.sum(Payment.amount).label('total')
    ).group_by(extract('month', Payment.date)).order_by('month').all()
    monthly_list = [{"month": m.month, "total": float(m.total or 0)} for m in monthly]
    logs.append({"type": "summary", "timestamp": datetime.now().isoformat()})
    return SummarySchema(total_payments=total_payments, unpaid_invoices=unpaid_invoices, monthly=monthly_list)

@app.post("/api/ai-assistant", response_model=dict)
def ai_assistant(request: QuerySchema, db: Session = Depends(get_db)):
    query_lower = request.query.lower()
    response = "Understood query."
    if "invoice" in query_lower and "month" in query_lower:
        last_month = datetime.now() - timedelta(days=30)
        results = db.query(Invoice).filter(Invoice.date >= last_month).limit(5).all()
        response = f"Found {len(results)} recent invoices totaling ~${sum(i.amount for i in results):.2f}"
    elif "payment" in query_lower:
        unpaid = db.query(Payment).filter(Payment.status == 'unpaid').count()
        response = f"There are {unpaid} unpaid payments."
    else:
        response = "Try: 'Show invoices from last month' or 'unpaid payments'."
    log_entry = {"prompt": request.query, "response": response, "timestamp": datetime.now().isoformat()}
    logs.append(log_entry)
    return {"response": response}

@app.get("/api/agent-logs", response_model=List[LogEntry])
def get_logs(limit: int = Query(20, ge=1)):
    return logs[-limit:] if logs else []