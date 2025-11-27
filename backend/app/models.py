#Define data schema

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, func
from .database import Base


class AccountantData(Base):
    """
    Represents aggregated and processed financial data from a single agent source.
    """
    __tablename__ = "accountant_data"
    
    id = Column(Integer, primary_key=True, index=True)

    # Data Source/Agent Info
    agent_id = Column(String, index=True, nullable=False)
    client_name = Column(String, index=True, nullable=False)

    # Financial Metrics
    tax_liability = Column(Float, nullable=False)
    total_revenue = Column(Float, nullable=False)
    compliance_status = Column(String, default="Pending")

    # Timestamps
    data_ingested_at = Column(DateTime, default=func.now())
    data_period_start = Column(DateTime)
    data_period_end = Column(DateTime)

    # Observability Fields (for AI Agent use)
    is_processed_by_ai = Column(Boolean, default=False)
    ai_summary_hash = Column(String, nullable=True)

    def __repr__(self):
        return f"<AccountantData(id={repr(self.id)}, agent={repr(self.agent_id)}, liability={repr(self.tax_liability)})>"
