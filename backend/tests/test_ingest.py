import requests

data = {
    "agent_id": "AG001",
    "client_name": "Test Client",
    "tax_liability": 1000.0,
    "total_revenue": 5000.0,
    "compliance_status": "Pending",
    "data_period_start": "2023-01-01T00:00:00",
    "data_period_end": "2023-12-31T00:00:00"
}
response = requests.post("http://localhost:8000/api/data-ingest", json=data)
print(response.json())