# backend/app/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, func, JSON 
from sqlalchemy.orm import declarative_base 
from .database import Base 


class AccountantData(Base):
    """
    Represents aggregated and processed financial data from a single agent source.
    (Your existing model, preserved and slightly refined for JSON payload)
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
    
    # NEW: Include a column for the raw ingested data payload (essential for AI processing)
    raw_data_payload = Column(JSON, nullable=True)

    # Timestamps
    data_ingested_at = Column(DateTime, default=func.now())
    data_period_start = Column(DateTime)
    data_period_end = Column(DateTime)

    # Observability Fields (for AI Agent use)
    is_processed_by_ai = Column(Boolean, default=False)
    ai_summary_hash = Column(String, nullable=True) # Hash/Pointer to the DataSummary entry
    
    def __repr__(self):
        return f"<AccountantData(id={repr(self.id)}, agent={repr(self.agent_id)}, liability={repr(self.tax_liability)})>"


class DataSummary(Base):
    """
    Table to store AI-generated summaries, alerts, or insights.
    This is the output of the LangGraph/Multi-Agent system.
    """
    __tablename__ = "data_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to the Agent/Client
    # This links the summary back to the specific client/agent ID
    agent_id = Column(String, index=True, nullable=False) 
    
    # AI Workflow Output
    summary_type = Column(String, nullable=False) # e.g., 'Compliance_Alert', 'Financial_Overview', 'RAG_Query_Result'
    summary_text = Column(String, nullable=False) # The actual output text from the LLM
    
    # Observability: Link back to the specific data point that triggered the summary
    source_data_id = Column(Integer, nullable=True) 
    workflow_id = Column(String, nullable=True) # LangSmith/Airflow correlation ID
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    llm_model_used = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<DataSummary(id={repr(self.id)}, type={repr(self.summary_type)}, agent={repr(self.agent_id)})>"