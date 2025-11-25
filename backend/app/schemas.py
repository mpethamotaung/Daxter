from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# --- INGESTION SCHEMAS ---

class AccountantDataCreate(BaseModel):
    """Schema for incoming data from a data source/agent (POST request body)."""
    agent_id: str = Field(..., description="Unique ID of the external agent providing the data.")
    client_name: str = Field(..., description="Name of the client associated with this data.")
    tax_liability: float = Field(..., gt=0, description="Calculated tax liability for the period.")
    total_revenue: float = Field(..., gt=0, description="Total revenue for the period.")
    compliance_status: str = Field("Pending", description="Current compliance status (e.g., Pending, Approved).")
    data_period_start: datetime = Field(..., description="Start date of the financial data period.")
    data_period_end: datetime = Field(..., description="End date of the financial data period.")

    class Config:
        # Enables conversion of SQLAlchemy models to Pydantic objects
        from_attributes = True

# --- RESPONSE SCHEMAS ---

class AccountantDataResponse(AccountantDataCreate):
    """Schema for data returned to the user (GET request response)."""
    id: int
    data_ingested_at: datetime
    is_processed_by_ai: bool = False
    ai_summary_hash: Optional[str] = None


class DashboardSummary(BaseModel):
    """Schema for the aggregated summary data for the dashboard."""
    total_clients: int
    total_tax_liability_usd: float
    total_revenue_usd: float
    compliance_pending_count: int
    last_ingestion_time: Optional[datetime]