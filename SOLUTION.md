# SOLUTION.md - Daxter Take-Home Assignment

## Why I had to pivot and simplify everything

I originaly started with a very complex and ambitious architecture:

- Docker Compose
- Postgres + Alembic
- LangGraph
- LangSmith
- Redux 
- Real async agents 

After 1 week of fighting Docker networking, volume mounts, and 
dependency hell, I realized I was burning the 4-hour window 
(or week + extension) on infrastructure trying to build a perfect
architecure.

**180 degrees pivot 1 week in:**
I realized I was trying to go above and beyond. I threw everything 
away and went 100% local-first, in-memory (SQLite), with a fraction
of the required dependencies. I shot myself in the foot but the pivot
was the right engineering decision for a timed take-home.

### Final Architecture 

| Layer | Technology | Reason |
| --- | --- | --- |
| Backend | FastAPI + SQLAlchemy (in-memory SQLite) | Zero setup, instant reload |
| Database | "sqlite:///daxter.db" | No file, no migrations, no Alembic needed |
| AI Assistant | Simple mock | Mock LLM setup allowed |
| Observability | Python list | Lightweight, meets requirements |
| Frontend | Next.js 13+ App Router, React Query, Tailwind, and Recharts | Fast, no Redux boilerplate |
| State Management | React Query (only) | Redux is overkill for such a small project. This is 90% less code, with caching |

### Key Trade-offs & Justification

| Decision | Why? | Trade-off |
| --- | --- | --- |
| Dropped Docker | Lost a week to network issues. | Slightly less reproducible, but runs in 10 seconds locally |
| Remove LangGraph/LangSmity | assigment allows mock LLM | Less "impressive" on paper, but 100% requirements met/onscope working|
| Removed Redux | too complex for 4-hour task | Simple, faster, and cleaner code |
| In-memory DB (mock data) | Immediate results | No data persistence on app load |
| Simple string AI mock | Works withou API keys | No real AI data, but it demonstrates understanding of flow |

### What I actually delivered 

- `/api/payments` & `/api/invoices` Paginated & filterable
- `/api/summary` Monthly totals & Monthly breadowns
- `api/ai-assistant` Accepts query and returns relevant answer using DB data
- `api/agent-logs` Shows activity log (clicks & queries)
- Dashboard with summary cards, two tables, Recharts bar chart, AI chat, activity log
- Github repo containing the code, readme, solution, and loom video

### Final Note 

I could have kept the professional over-engineered version and submitted a broken, incomplete, or barely-working demo. Instead, I took a risk and made a pivot to ship a clean, complete, working solution.

I went way beyond the 4 hours/1 week because I'm so used to building scalable & maintainable applications while avoiding technical debt with a monolithic architecture. But I realized that I have to ruthlessly cut the scope, deliver it fast and make it reproduceable.

I hope that my mistakes have not affected my application because I really wanted to show how multi versed I am in this domain. 

Thank you for the your consideration.