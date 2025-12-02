# backend/app/schemas.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

# --- ENUMERATIONS ---
class ComplianceStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"

# --- INGESTION SCHEMAS ---
class AccountantDataCreate(BaseModel):
    """Schema for incoming data from a data source/agent (POST request body)."""
    agent_id: str = Field(..., description="Unique ID of the external agent providing the data.")
    client_name: str = Field(..., description="Name of the client associated with this data.")
    tax_liability: float = Field(..., gt=0, description="Calculated tax liability for the period.")
    total_revenue: float = Field(..., gt=0, description="Total revenue for the period.")
    data_period_start: datetime = Field(..., description="Start date of the financial data period.")
    data_period_end: datetime = Field(..., description="End date of the financial data period.")
    compliance_status: ComplianceStatus = ComplianceStatus.PENDING
    raw_data_payload: Dict[str, Any] # Essential for AI to analyze the raw JSON/data

    class Config:
        from_attributes = True

# --- RESPONSE SCHEMAS ---
class AccountantDataResponse(AccountantDataCreate):
    """Schema for data returned to the user (GET request response)."""
    id: int
    data_ingested_at: datetime
    is_processed_by_ai: bool = False
    ai_summary_hash: Optional[str] = None
    # Removed raw_data_payload from response for security/brevity, 
    # but kept it in the Create schema for ingestion.

class DashboardSummary(BaseModel):
    """Schema for the aggregated summary data for the dashboard."""
    total_clients: int
    total_tax_liability_gbp: float
    total_revenue_gbp: float
    compliance_pending_count: int
    last_ingestion_time: Optional[datetime]

# --- AI AGENT WORKFLOW SCHEMAS (NEW) ---
class SummaryRequest(BaseModel):
    """Request schema for POST /api/ai-summary to generate a summary."""
    agent_id: str = Field(..., description="The ID of the agent/client to analyze.")
    summary_type: str = Field(..., description="Type of summary requested (e.g., 'Compliance_Alert', 'Financial_Overview').")
    
class SummaryResponse(BaseModel):
    """Response schema for POST /api/ai-summary."""
    agent_id: str
    summary_type: str
    summary_text: str