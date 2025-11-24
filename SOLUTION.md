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

## Key Technology Choices & Rationale

| Component | Technology | Rationale |
| --- | --- | --- |
| Backend API | FastAPI (Python) | Chosen for its high performance, native asynchronous support, and strong tooling with Pydantic for data validation. This is critical for high-throughput data ingestion and responsive API calls for the dashboard. |
| Database | PostgreSQL | A mature, reliable, and highly scalable relational database, ideal for structured financial and compliance data. |
| ORM & Driver | SQLAlchemy (async) & asyncpg | Provides robust, object-oriented interaction with the database. The asynchronous setup ensures the API server remains non-blocking during database operations. |
| Frontend Framework | Next.js | Offers built-in routing, performance optimizations (SSR/SSG), and a strong foundation for a professional, scalable dashboard application. |
| State Management | Redux Toolkit | Although complex for small projects, Redux provides centralized, predictable state management, which is essential for handling real-time data streams, dashboard synchronization, and AI chat history in a complex application. |
| Orchestration | LangGraph | Specifically selected for its ability to define and manage complex, stateful, multi-step agentic workflows, moving beyond simple single-call RAG chains. |

## Major Assumptions and Tradeoffs

**Assumptions**

- **No Authentication:** As this is an MVP, all authentication and authorization logic has been omitted to focus purely on the core data ingestion and AI interaction features.
- **Development Environment:** The primary development environment is assumed to be **containerised** using Docker Compose for maximum consistency and ease of setup.
- **External Agents are Mocked:** The "Agent Data Sources" are mocked external entities that will hit a single ingestion endpoint ( **/api/data-ingestion**).

**Tradeoffs**

| Decision | Rationale for Choice | Tradeoff Incurred |
| --- | --- | --- |
| FastAPI vs. Django | **High Performance & Minimalist.** FastAPI requires less boilerplate, allowing faster setup and development of micro-APIs. | Requires more manual configuration (e.g., routing, ORM setup) compared to the "batteries-included" nature of Django. |
| Docker Isolation | **Reproducibility.** Ensures the exact same versions of Python, Node, and Postgres run everywhere. | Adds complexity to the initial setup (multiple Dockerfiles, Docker Compose config) and slight overhead during development compared to local binaries. |
| Redux in Demo | Future Scalability. Prepares the UI for complex real-time data handling (dashboard metrics, live agent status). | **Overkill for a simple demo.** Increases boilerplate code for basic state management. |
