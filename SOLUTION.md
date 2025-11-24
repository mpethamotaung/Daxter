# Daxter Project Architecture and Implementation Rationale

This document outlines the architectural design, core technology choices, and major trade-offs made during the initial setup of the Daxter project (Account Data Aggregation
and Insights Dashboard).

## Architectural Design: The Decoupled Three-Tier System

The Daxter project utilizes a **decoupled three-tier architecture** with a specialized **AI Agent Layer** integrated into the application logic tier.
This design ensures separation of concerns, scalability, and independent deployment of the core services.

**Key Tiers**

| Tier | Services | Primary Role |
| --- | --- | --- |
| Presentation | Next.js, React.js, Material UI, Redux | Provides the user interface, manages client-side state, and handles API calls. |
| Application Logic & AI | FastAPI, LangGraph, LLM API | Serves as the API gateway, contains all business logic, manages data ingestion, and orchestrates the AI agent workflows. |
| Data | PostgreSQL, SQLAlchemy | Provides persistent, transactional storage for all ingested financial data and AI agent state/logs. |
