# backend/app/seeder.py

import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from .models import AccountantData, DataSummary
from .schemas import ComplianceStatus 
import logging

logger = logging.getLogger(__name__)

async def seed_database(db: AsyncSession, num_agents: int = 3, entries_per_agent: int = 10):
    """
    Generates mock financial data and AI summaries and adds them to the database
    if the AccountantData table is empty.
    """
    # 1. Check if the database is already seeded (by checking the main table)
    result = await db.execute(select(func.count(AccountantData.id)))
    if result.scalar_one() > 0:
        logger.info("Database already contains data. Skipping seeding.")
        return

    logger.info(f"Seeding database with {num_agents * entries_per_agent} financial entries...")
    
    current_time = datetime.now()
    all_data_to_add = []
    
    for i in range(1, num_agents + 1):
        agent_id = f"AGENT-{i:03d}"
        client_name = f"Client {i} Global"
        
        for j in range(entries_per_agent):
            # Generate random but realistic financial data
            revenue = round(random.uniform(50000.00, 500000.00), 2)
            liability = round(revenue * random.uniform(0.1, 0.2), 2)
            
            # Generate consistent timestamps, going backward in time
            ingestion_time = current_time - timedelta(hours=i*3, minutes=j*15, seconds=random.randint(10, 59))
            period_end = ingestion_time - timedelta(days=30)
            period_start = period_end - timedelta(days=90)
            
            # Cycle through compliance statuses
            status_list = list(ComplianceStatus)
            compliance_status = status_list[j % len(status_list)].value
            
            data_entry = AccountantData(
                agent_id=agent_id,
                client_name=client_name,
                tax_liability=liability,
                total_revenue=revenue,
                compliance_status=compliance_status,
                data_ingested_at=ingestion_time,
                data_period_start=period_start,
                data_period_end=period_end,
                raw_data_payload={
                    "filing_year": 2025,
                    "quarter": f"Q{(j % 4) + 1}",
                    "details": f"Generated entry {j+1} for agent {i}"
                }
            )
            all_data_to_add.append(data_entry)

            # Add a mock AI summary for compliance-critical entries (j=4)
            if j % 4 == 0:
                summary_type = "Compliance_Alert" if compliance_status == "Pending" else "Financial_Overview"
                summary_text = (
                    f"AI noted a {summary_type} for {client_name}. "
                    f"Revenue was ${revenue}. LLM assessment complete."
                )
                summary_entry = DataSummary(
                    agent_id=agent_id,
                    summary_type=summary_type,
                    summary_text=summary_text,
                    llm_model_used="Mock-LLM-v2"
                )
                all_data_to_add.append(summary_entry)

    # Bulk add and commit to ensure persistence
    db.add_all(all_data_to_add)
    await db.commit()
    logger.info("Database seeding complete and persistent for the session.")