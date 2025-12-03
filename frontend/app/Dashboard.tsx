'use client';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { format } from 'date-fns';
import { useState } from 'react';

interface Payment { id: number; amount: number; date: string; status: string; }
interface Invoice { id: number; amount: number; date: string; status: string; }
interface Summary { total_payments: number; unpaid_invoices: number; monthly: { month: number; total: number }[]; }
interface Log { type: string; timestamp: string; error?: string; prompt?: string; response?: string; count?: number; }

// Fetchers for API endpoints
const fetchPayments = async (offset = 0, limit = 10, status = ''): Promise<Payment[]> => {
  let url = `/api/payments?offset=${offset}&limit=${limit}`;
  if (status) url += `&status=${status}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Payments fetch failed');
  return res.json();
};

const fetchInvoices = async (offset = 0, limit = 10, status = ''): Promise<Invoice[]> => {
  let url = `/api/invoices?offset=${offset}&limit=${limit}`;
  if (status) url += `&status=${status}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Invoices fetch failed');
  return res.json();
};

const fetchSummary = async (): Promise<Summary> => {
  const res = await fetch('/api/summary');
  if (!res.ok) throw new Error('Summary fetch failed');
  return res.json();
};

const fetchLogs = async (): Promise<Log[]> => {
  const res = await fetch('/api/agent-logs?limit=15');
  if (!res.ok) throw new Error('Logs fetch failed');
  return res.json();
};

const postAIQuery = async (query: string): Promise<{ response: string }> => {
  const res = await fetch('/api/ai-assistant', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error('AI query failed');
  return res.json();
};

export default function Dashboard() {
  // State for pagination and filtering
  const [paymentsOffset, setPaymentsOffset] = useState(0);
  const [invoicesOffset, setInvoicesOffset] = useState(0);
  const [paymentsStatus, setPaymentsStatus] = useState('');
  const [invoicesStatus, setInvoicesStatus] = useState('');
  const [aiQuery, setAiQuery] = useState('');
  const [aiHistory, setAiHistory] = useState<{ q: string; r: string }[]>([]);
  const [selectedBar, setSelectedBar] = useState<number | null>(null);
  const limit = 10; // Per page

  // Data queries
  const { data: summary, isLoading: sLoading, isError: sError } = useQuery({
    queryKey: ['summary'],
    queryFn: fetchSummary,
    //onError: (error) => console.error('Summary fetch error:', error),
  });

  const { data: payments, isLoading: pLoading, isError: pError } = useQuery({
    queryKey: ['payments', paymentsOffset, paymentsStatus],
    queryFn: () => fetchPayments(paymentsOffset, limit, paymentsStatus),
  });

  const { data: invoices, isLoading: iLoading, isError: iError } = useQuery({
    queryKey: ['invoices', invoicesOffset, invoicesStatus],
    queryFn: () => fetchInvoices(invoicesOffset, limit, invoicesStatus),
  });

  const { data: logs, isLoading: lLoading, isError: lError } = useQuery({
    queryKey: ['logs'],
    queryFn: fetchLogs,
    refetchInterval: 5000, // Auto-refresh every 5s
  });

  const queryClient = useQueryClient();
  const aiMutation = useMutation({
    mutationFn: postAIQuery,
    onSuccess: (data) => {
      setAiHistory(prev => [{ q: aiQuery, r: data.response }, ...prev.slice(0, 4)]);
      setAiQuery('');
      queryClient.invalidateQueries({ queryKey: ['logs'] }); // Refresh logs after AI call
    },
  });

  // Handlers
  const handleBarClick = (data: any, index: number) => {
    setSelectedBar(index === selectedBar ? null : index);
  };
  const handleAiSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (aiQuery.trim()) aiMutation.mutate(aiQuery);
  };

  // Loading/Error UI
  if (sLoading) return <div className="p-6 text-center">Loading dashboard...</div>;

  return (
    <div className="p-4 md:p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl md:text-3xl font-bold text-gray-800 mb-6">Daxter Accountant Dashboard</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-lg font-semibold text-gray-700">Total Payments</h2>
          <p className="text-2xl font-bold text-green-600">
            {sError ? 'Error' : `$${summary?.total_payments.toFixed(2) || '0.00'}`}
          </p>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-lg font-semibold text-gray-700">Unpaid Invoices</h2>
          <p className="text-2xl font-bold text-red-600">
            {sError ? 'Error' : `$${summary?.unpaid_invoices.toFixed(2) || '0.00'}`}
          </p>
        </div>
      </div>

      {/* Monthly Chart */}
      <div className="mb-6 bg-white p-4 rounded shadow">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">Monthly Payments</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={summary?.monthly || []} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
            <XAxis dataKey="month" tickFormatter={m => `Month ${m}`} />
            <YAxis />
            <Tooltip formatter={v => `$${v}`} />
            <Bar dataKey="total" onClick={handleBarClick}>
              {(summary?.monthly || []).map((entry, index) => (
                <Cell key={`cell-${index}`} fill={index === selectedBar ? '#82ca9d' : '#8884d8'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Tables: Payments & Invoices */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Payments */}
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-3 text-gray-700">Payments</h2>
          <div className="mb-3 flex flex-col sm:flex-row gap-2">
            <select
              value={paymentsStatus}
              onChange={e => { setPaymentsStatus(e.target.value); setPaymentsOffset(0); }}
              className="border p-2 rounded text-sm"
            >
              <option value="">All Status</option>
              <option value="paid">Paid</option>
              <option value="unpaid">Unpaid</option>
            </select>
            <div className="flex gap-2">
              <button
                onClick={() => setPaymentsOffset(p => Math.max(0, p - limit))}
                className="bg-gray-200 px-3 py-2 rounded text-sm"
                disabled={paymentsOffset <= 0}
              >
                Prev
              </button>
              <button
                onClick={() => setPaymentsOffset(p => p + limit)}
                className="bg-gray-200 px-3 py-2 rounded text-sm"
                disabled={(payments?.length || 0) < limit}
              >
                Next
              </button>
              <span className="text-sm p-2">Page {paymentsOffset / limit + 1}</span>
            </div>
          </div>
          {pLoading ? (
            <p className="text-gray-500">Loading...</p>
          ) : pError ? (
            <p className="text-red-500">Error loading payments</p>
          ) : !payments?.length ? (
            <p className="text-gray-500">No payments found</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-sm">
                <thead>
                  <tr className="border-b bg-gray-100">
                    <th className="p-2 text-left font-semibold">ID</th>
                    <th className="p-2 text-left font-semibold">Amount</th>
                    <th className="p-2 text-left font-semibold">Date</th>
                    <th className="p-2 text-left font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {payments.map(p => (
                    <tr key={p.id} className="border-b hover:bg-gray-50">
                      <td className="p-2">{p.id}</td>
                      <td className="p-2">${p.amount.toFixed(2)}</td>
                      <td className="p-2">{format(new Date(p.date), 'yyyy-MM-dd')}</td>
                      <td className="p-2">{p.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Invoices */}
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-3 text-gray-700">Invoices</h2>
          <div className="mb-3 flex flex-col sm:flex-row gap-2">
            <select
              value={invoicesStatus}
              onChange={e => { setInvoicesStatus(e.target.value); setInvoicesOffset(0); }}
              className="border p-2 rounded text-sm"
            >
              <option value="">All Status</option>
              <option value="paid">Paid</option>
              <option value="unpaid">Unpaid</option>
            </select>
            <div className="flex gap-2">
              <button
                onClick={() => setInvoicesOffset(p => Math.max(0, p - limit))}
                className="bg-gray-200 px-3 py-2 rounded text-sm"
                disabled={invoicesOffset <= 0}
              >
                Prev
              </button>
              <button
                onClick={() => setInvoicesOffset(p => p + limit)}
                className="bg-gray-200 px-3 py-2 rounded text-sm"
                disabled={(invoices?.length || 0) < limit}
              >
                Next
              </button>
              <span className="text-sm p-2">Page {invoicesOffset / limit + 1}</span>
            </div>
          </div>
          {iLoading ? (
            <p className="text-gray-500">Loading...</p>
          ) : iError ? (
            <p className="text-red-500">Error loading invoices</p>
          ) : !invoices?.length ? (
            <p className="text-gray-500">No invoices found</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-sm">
                <thead>
                  <tr className="border-b bg-gray-100">
                    <th className="p-2 text-left font-semibold">ID</th>
                    <th className="p-2 text-left font-semibold">Amount</th>
                    <th className="p-2 text-left font-semibold">Date</th>
                    <th className="p-2 text-left font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {invoices.map(i => (
                    <tr key={i.id} className="border-b hover:bg-gray-50">
                      <td className="p-2">{i.id}</td>
                      <td className="p-2">${i.amount.toFixed(2)}</td>
                      <td className="p-2">{format(new Date(i.date), 'yyyy-MM-dd')}</td>
                      <td className="p-2">{i.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* AI Assistant + Logs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-3 text-gray-700">AI Assistant</h2>
          <form onSubmit={handleAiSubmit} className="mb-3 flex gap-2">
            <input
              type="text"
              value={aiQuery}
              onChange={e => setAiQuery(e.target.value)}
              placeholder="Ask about data (e.g., 'Show invoices from last month')"
              className="flex-1 border p-2 rounded text-sm"
              disabled={aiMutation.isPending}
            />
            <button
              type="submit"
              className="bg-blue-500 text-white px-4 py-2 rounded text-sm hover:bg-blue-600"
              disabled={aiMutation.isPending || !aiQuery.trim()}
            >
              {aiMutation.isPending ? 'Sending...' : 'Send'}
            </button>
          </form>
          {aiMutation.isError && (
            <p className="text-red-500 text-sm mb-2">Error: {(aiMutation.error as Error).message}</p>
          )}
          {aiHistory.length > 0 ? (
            <div className="space-y-2 max-h-48 overflow-y-auto text-sm">
              {aiHistory.map((h, i) => (
                <div key={i} className="border-b pb-2">
                  <p className="font-semibold text-gray-700">Q: {h.q}</p>
                  <p className="text-gray-600">A: {h.r}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No queries yet. Try asking about invoices or payments.</p>
          )}
        </div>

        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-3 text-gray-700">Recent Activity Logs</h2>
          {lLoading ? (
            <p className="text-gray-500">Loading logs...</p>
          ) : lError ? (
            <p className="text-red-500">Error loading logs</p>
          ) : !logs?.length ? (
            <p className="text-gray-500">No logs available</p>
          ) : (
            <div className="overflow-y-auto max-h-64 text-xs">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b bg-gray-100 sticky top-0">
                    <th className="p-2 text-left font-semibold">Type</th>
                    <th className="p-2 text-left font-semibold">Time</th>
                    <th className="p-2 text-left font-semibold">Details</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log, i) => (
                    <tr key={i} className="border-b hover:bg-gray-50">
                      <td className="p-2">{log.type}</td>
                      <td className="p-2">{format(new Date(log.timestamp), 'HH:mm:ss')}</td>
                      <td className="p-2 truncate">
                        {log.prompt ? `Q: ${log.prompt}` : log.count ? `${log.count} items` : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}