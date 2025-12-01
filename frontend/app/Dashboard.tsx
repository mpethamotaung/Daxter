// frontend/app/Dashboard.tsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';
// Assuming you have a basic way to handle icons, e.g., react-icons or simple text
// Since you are using MUI, you would typically import Icons here (e.g., from @mui/icons-material)
import { Alert, Button, Card, CardContent, CircularProgress, Container, Grid, Typography, Box, TextField } from '@mui/material';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import GroupsIcon from '@mui/icons-material/Groups';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import WarningIcon from '@mui/icons-material/Warning';

// --- Types (Matching Backend Schemas) ---
interface AccountantDataPreview {
  id: number;
  client_name: string;
  tax_liability: number;
  total_revenue: number;
  data_ingested_at: string;
}

interface AISummary {
  summary_type: string;
  text: string;
  created_at: string;
  workflow_id: string; 
}

interface DashboardOverview {
  total_clients: number;
  total_tax_liability_usd: number;
  total_revenue_usd: number;
  compliance_pending_count: number;
  last_ingestion_time: string | null;
}

interface AgentData {
  agent_id: string;
  latest_raw_data_previews: AccountantDataPreview[];
  ai_summaries: AISummary[];
}

const API_BASE_URL = 'http://localhost:8000/api';

// --- API Client Functions ---

const fetchDashboardOverview = async (): Promise<DashboardOverview> => {
  const response = await fetch(`${API_BASE_URL}/summary`);
  if (!response.ok) throw new Error('Failed to fetch dashboard overview');
  return response.json();
};

const fetchAgentData = async (agentId: string): Promise<AgentData> => {
  const response = await fetch(`${API_BASE_URL}/agent-data/${agentId}`);
  if (!response.ok) {
    //If API returns 404 (No data found for agent), return an empty structure
    if (response.status === 404) {
      return { agent_id: agentId, latest_raw_data_previews: [], ai_summaries: [] };
    }
    // For any other error (500 Internal Server Error, etc.), throw an error
    throw new Error(`Failed to fetch data for agent ${agentId}`);
  }
  return response.json();
};

const generateAISummary = async (agentId: string, summaryType: string) => {
  const response = await fetch(`${API_BASE_URL}/ai-summary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ agent_id: agentId, summary_type: summaryType }),
  });
  if (!response.ok) throw new Error('Failed to trigger AI summary');
  return response.json();
};

// --- Helper Components ---

const StatCard: React.FC<{ title: string; value: string; icon: React.ReactElement }> = ({ title, value, icon }) => (
  <Card variant="outlined">
    <CardContent>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography color="textSecondary" gutterBottom>
          {title}
        </Typography>
        {icon}
      </Box>
      <Typography variant="h4" component="div" sx={{ mt: 1 }}>
        {value}
      </Typography>
    </CardContent>
  </Card>
);


// --- Main Dashboard Component ---

const DaxterDashboard: React.FC = () => {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [selectedAgentId, setSelectedAgentId] = useState<string>('AGENT-101'); // Default test agent
  const [inputAgentId, setInputAgentId] = useState<string>('AGENT-101');
  const [agentData, setAgentData] = useState<AgentData | null>(null);
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAILoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aiStatus, setAIStatus] = useState<string | null>(null);

  // Function to load all necessary data for the current agent
  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [overviewData, agentDetailData] = await Promise.all([
        fetchDashboardOverview(),
        fetchAgentData(selectedAgentId),
      ]);
      setOverview(overviewData);
      setAgentData(agentDetailData);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'An unknown error occurred while fetching dashboard data.');
    } finally {
      setLoading(false);
    }
  }, [selectedAgentId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handler for triggering AI Analysis
  const handleAITrigger = async (summaryType: string) => {
    setAILoading(true);
    setAIStatus(`Running AI ${summaryType}...`);
    setError(null);
    try {
      await generateAISummary(selectedAgentId, summaryType);
      setAIStatus('AI Summary successfully generated!');
      // Refresh the agent detail view to show the new summary
      await loadData(); 
    } catch (err: any) {
      setAIStatus(null);
      setError(`AI Error: ${err.message}`);
    } finally {
      setAILoading(false);
      setTimeout(() => setAIStatus(null), 5000); // Clear status after 5s
    }
  };

  const handleFetchAgent = () => {
    setSelectedAgentId(inputAgentId);
  };


  if (loading && !overview) {
    return (
      <Container maxWidth="xl" sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>Loading Daxter Dashboard...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
        OpenTax Unified Accountant Dashboard
      </Typography>

      {/* Error and Status Messages */}
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {aiStatus && <Alert severity="info" sx={{ mb: 3 }}>{aiStatus}</Alert>}

      {/* Aggregated Overview Section */}
      <Grid container spacing={3} sx={{ mb: 5 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Clients" value={overview?.total_clients.toString() || 'N/A'} icon={<GroupsIcon color="primary" />} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Revenue (USD)" value={`$${overview?.total_revenue_usd.toFixed(2) || '0.00'}`} icon={<AttachMoneyIcon color="success" />} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Pending Compliance" value={overview?.compliance_pending_count.toString() || 'N/A'} icon={<WarningIcon color="warning" />} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Last Ingestion" 
            value={overview?.last_ingestion_time ? new Date(overview.last_ingestion_time).toLocaleTimeString() : 'N/A'} 
            icon={<AccessTimeIcon color="action" />}
          />
        </Grid>
      </Grid>

      {/* Agent-Specific View Section */}
      <Card sx={{ p: 4 }}>
        <Typography variant="h5" component="h2" sx={{ mb: 3, borderBottom: 1, borderColor: 'divider', pb: 1 }}>
          Agent Details & AI Workflow
        </Typography>

        {/* Agent Selector */}
        <Box display="flex" alignItems="center" gap={2} sx={{ mb: 4 }}>
          <TextField
            label="Enter Agent ID"
            variant="outlined"
            size="small"
            value={inputAgentId}
            onChange={(e) => setInputAgentId(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleFetchAgent();
            }}
          />
          <Button 
            onClick={handleFetchAgent}
            disabled={loading || !inputAgentId}
            variant="contained"
          >
            Fetch Data
          </Button>
        </Box>

        {loading ? (
            <Box display="flex" justifyContent="center" py={4}><CircularProgress /></Box>
        ) : agentData ? (
          <Grid container spacing={4}>
            
            {/* AI Summary/Alerts Panel */}
            <Grid item xs={12} lg={6}>
              <Card variant="elevation" sx={{ p: 3, backgroundColor: 'rgba(255, 193, 7, 0.05)' }}>
                <Typography variant="h6" sx={{ color: 'warning.dark', mb: 2, fontWeight: 'medium' }}>
                  AI Summary & Alerts (LangGraph Simulation)
                </Typography>
                
                <Button 
                  onClick={() => handleAITrigger('Compliance_Alert')}
                  disabled={aiLoading}
                  variant="contained"
                  color="success"
                  size="small"
                  sx={{ mb: 3 }}
                  startIcon={aiLoading ? <CircularProgress size={16} color="inherit" /> : null}
                >
                  {aiLoading ? 'Running AI Agent...' : 'Trigger Compliance Check'}
                </Button>

                {agentData.ai_summaries.length > 0 ? (
                  <Box sx={{ maxHeight: 300, overflowY: 'auto' }}>
                    {agentData.ai_summaries.map((summary, index) => (
                      <Card key={index} variant="outlined" sx={{ mb: 2, borderLeft: 4, borderColor: 'warning.main' }}>
                        <CardContent sx={{ py: 1.5 }}>
                          <Typography variant="subtitle2">{summary.summary_type}</Typography>
                          <Typography variant="body1" sx={{ fontStyle: 'italic', color: 'text.secondary' }}>
                            {summary.text}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            Generated at: {new Date(summary.created_at).toLocaleString()} | Workflow ID: {summary.workflow_id || 'N/A'}
                          </Typography>
                        </CardContent>
                      </Card>
                    ))}
                  </Box>
                ) : (
                  <Typography color="textSecondary">No AI summaries found for this agent. Run a check!</Typography>
                )}
              </Card>
            </Grid>

            {/* Raw Data Observability Panel */}
            <Grid item xs={12} lg={6}>
              <Card variant="elevation" sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 'medium' }}>
                  Latest Raw Data Ingestion (Observability)
                </Typography>
                {agentData.latest_raw_data_previews.length > 0 ? (
                  <Box sx={{ maxHeight: 300, overflowY: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #e0e0e0' }}>ID</th>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #e0e0e0' }}>Client</th>
                          <th style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #e0e0e0' }}>Revenue</th>
                          <th style={{ textAlign: 'left', padding: '8px', borderBottom: '1px solid #e0e0e0' }}>Time</th>
                        </tr>
                      </thead>
                      <tbody>
                        {agentData.latest_raw_data_previews.map((data) => (
                          <tr key={data.id}>
                            <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>{data.id}</td>
                            <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>{data.client_name}</td>
                            <td style={{ textAlign: 'right', padding: '8px', borderBottom: '1px solid #f0f0f0' }}>${data.total_revenue.toFixed(2)}</td>
                            <td style={{ padding: '8px', borderBottom: '1px solid #f0f0f0' }}>{new Date(data.data_ingested_at).toLocaleTimeString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </Box>
                ) : (
                  <Typography color="textSecondary">No raw ingestion data found for this agent ID.</Typography>
                )}
              </Card>
            </Grid>
          </Grid>
        ) : (
            <Typography color="textSecondary">Enter an Agent ID and click 'Fetch Data' to view details.</Typography>
        )}
      </Card>
    </Container>
  );
};

export default DaxterDashboard;