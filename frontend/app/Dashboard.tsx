// frontend/app/Dashboard.tsx 

'use client'; 

import { useState, useEffect } from 'react';

// Define the shape of the summary data
interface SummaryData {
  total_clients: number;
  total_tax_liability_usd: number;
  total_revenue_usd: number;
  compliance_pending_count: number;
  last_ingestion_time: string | null;
}

// Use the environment variable set in docker-compose.yml
const API_URL = process.env.NEXT_PUBLIC_API_URL + "/api/summary";

// The main Dashboard component
export default function Dashboard() { 
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSummary() {
      // ... (fetch logic from the previous response goes here) ...
      try {
        const response = await fetch(API_URL);
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}. Check if backend is running on port 8000.`);
        }
        
        const data: SummaryData = await response.json();
        setSummary(data);
      } catch (e) {
        setError(`Failed to fetch data: ${e instanceof Error ? e.message : 'Unknown error'}`);
      } finally {
        setIsLoading(false);
      }
    }

    fetchSummary();
  }, []); 

  if (isLoading) return <div>Loading Daxter Dashboard...</div>;
  if (error) return <div style={{ color: 'red', padding: '20px', border: '1px solid red' }}>Error: {error}</div>;
  if (!summary) return <div>No data available.</div>;

  // Render the dashboard using the fetched summary data
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">📊 Daxter Financial Summary</h1>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Clients" value={summary.total_clients} />
        <StatCard title="Total Revenue (USD)" value={summary.total_revenue_usd.toFixed(2)} isCurrency />
        <StatCard title="Tax Liability (USD)" value={summary.total_tax_liability_usd.toFixed(2)} isCurrency />
        <StatCard title="Compliance Pending" value={summary.compliance_pending_count} />
      </div>

      <p className="mt-8 text-sm text-gray-500">
        Last Data Ingestion: {summary.last_ingestion_time ? new Date(summary.last_ingestion_time).toLocaleString() : 'N/A'}
      </p>
    </div>
  );
}

// Simple component for visualization (must be in the same file or imported)
function StatCard({ title, value, isCurrency = false }: { title: string, value: string | number, isCurrency?: boolean }) {
  const displayValue = isCurrency ? `$${value}` : value;
  return (
    <div className="bg-white p-4 shadow-lg rounded-lg border-l-4 border-blue-500">
      <p className="text-sm font-medium text-gray-500">{title}</p>
      <p className="text-2xl font-bold text-gray-900 mt-1">{displayValue}</p>
    </div>
  );
}
