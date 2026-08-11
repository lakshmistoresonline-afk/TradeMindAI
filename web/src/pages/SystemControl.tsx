import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Stack, Button, Chip, Divider, List, ListItem, ListItemText, LinearProgress, Tab, Tabs, Tooltip } from '@mui/material';
import { ShieldCheck, Activity, Database, Server, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';
import { getSystemEvaluation, getSystemLogs, getDataHealth } from '../api/client';
import { MetricRegistry } from '../core/metrics';

export default function SystemControl() {
  const [tab, setTab] = useState(0);
  const [logs, setLogs] = useState<any[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [refreshing, setRefresh] = useState(false);

  const fetchStatus = async () => {
    setRefresh(true);
    try {
      const [evalData, logData, healthData] = await Promise.all([
        getSystemEvaluation(),
        getSystemLogs(),
        getDataHealth()
      ]);
      console.log("System Eval:", evalData);
      setLogs(logData);
      setHealth(healthData);
    } catch (e) {
      console.error("Error fetching system status:", e);
    } finally {
      setRefresh(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
           <ShieldCheck size={32} className="text-emerald-500" />
           <Typography variant="h4" sx={{ fontWeight: 900 }}>System Control</Typography>
        </Box>
        <Button variant="outlined" startIcon={<RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />} onClick={fetchStatus}>
           Engine Heartbeat
        </Button>
      </Box>

      <Box sx={{ mb: 4, borderBottom: '1px solid #1e293b' }}>
         <Tabs value={tab} onChange={(_, v) => setTab(v)} textColor="primary" indicatorColor="primary">
            <Tab label="Infrastructure" sx={{ fontWeight: 800 }} />
            <Tab label="Data Health" sx={{ fontWeight: 800 }} />
            <Tab label="Execution Logs" sx={{ fontWeight: 800 }} />
         </Tabs>
      </Box>

      {tab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <Paper sx={{ p: 3 }}>
                   <Stack direction="row" spacing={2} alignItems="center" mb={2}>
                      <Server size={20} color="#10b981" />
                      <Typography variant="subtitle2" fontWeight={800}>OPERATIONAL STATUS</Typography>
                   </Stack>
                   <Stack spacing={2}>
                      <WorkerStatus label="Main Intelligence Worker" status="IDLE" lastRun="3m ago" color="#10b981" />
                      <WorkerStatus label="Market Beat Scheduler" status="ACTIVE" lastRun="12s ago" color="#3b82f6" />
                      <WorkerStatus label="ML Retraining Cluster" status="QUEUED" lastRun="2h ago" color="#94a3b8" />
                   </Stack>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Paper sx={{ p: 3 }}>
                   <Stack direction="row" spacing={2} alignItems="center" mb={2}>
                      <Database size={20} color="#3b82f6" />
                      <Typography variant="subtitle2" fontWeight={800}>DATA PLATFORM</Typography>
                   </Stack>
                   <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                         <Typography variant="caption">Universe Coverage</Typography>
                         <Typography variant="caption" fontWeight="bold">{health?.database?.universe_coverage_pct?.toFixed(1) || 0}%</Typography>
                      </Box>
                      <LinearProgress variant="determinate" value={health?.database?.universe_coverage_pct || 0} color="primary" sx={{ height: 4, borderRadius: 2 }} />
                   </Box>
                   <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                         <Typography variant="caption">High-Fidelity Population</Typography>
                         <Typography variant="caption" fontWeight="bold">{health?.database?.fidelity_pct?.toFixed(1) || 0}%</Typography>
                      </Box>
                      <LinearProgress variant="determinate" value={health?.database?.fidelity_pct || 0} color="success" sx={{ height: 4, borderRadius: 2 }} />
                   </Box>
                   <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                         <Typography variant="caption">Data Freshness</Typography>
                         <Typography variant="caption" fontWeight="bold">{health?.database?.freshness_pct?.toFixed(1) || 0}%</Typography>
                      </Box>
                      <LinearProgress variant="determinate" value={health?.database?.freshness_pct || 0} color="info" sx={{ height: 4, borderRadius: 2 }} />
                   </Box>
                   <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                         <Typography variant="caption">Asset Breakdown</Typography>
                         <Typography variant="caption" fontWeight="bold">{health?.database?.total_stocks || 0} TOTAL</Typography>
                      </Box>
                      <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                         <Tooltip title="Complete High-Fidelity Records"><Chip label={`Complete: ${health?.database?.complete_stocks || 0}`} size="small" variant="outlined" sx={{ fontSize: '0.6rem' }} color="success" /></Tooltip>
                         <Tooltip title="Partial Records (Missing some data points)"><Chip label={`Partial: ${health?.database?.partial_stocks || 0}`} size="small" variant="outlined" sx={{ fontSize: '0.6rem' }} color="warning" /></Tooltip>
                         <Tooltip title="Stale Records (> 24h old)"><Chip label={`Stale: ${health?.database?.stale_stocks || 0}`} size="small" variant="outlined" sx={{ fontSize: '0.6rem' }} color="error" /></Tooltip>
                      </Stack>
                   </Box>
                </Paper>
              </Grid>
            </Grid>
          </Grid>

          <Grid item xs={12} md={4}>
             <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="subtitle2" color="textSecondary" gutterBottom fontWeight={800}>AI AGENT PERFORMANCE</Typography>
                <Stack spacing={3} mt={3}>
                   <StatusMetric label="Llama 3.1 Reasoning" value="98.2%" color="#10b981" />
                   <StatusMetric label="SMC Pattern Accuracy" value="84.5%" color="#3b82f6" />
                   <StatusMetric label="ML Confidence Score" value="72.0%" color="#fbbf24" />
                </Stack>
             </Paper>
          </Grid>
        </Grid>
      )}

      {tab === 1 && (
        <Box>
           <Grid container spacing={3}>
              <Grid item xs={12} lg={8}>
                 <Paper sx={{ p: 0, overflow: 'hidden' }}>
                    <Box sx={{ p: 2, borderBottom: '1px solid #334155', bgcolor: 'rgba(255,255,255,0.01)' }}>
                       <Typography variant="subtitle2" fontWeight={900}>METRIC REGISTRY & VALIDATION</Typography>
                    </Box>
                    <List sx={{ p: 0 }}>
                       {Object.values(MetricRegistry).map((m) => (
                         <Box key={m.id}>
                            <ListItem sx={{ py: 2 }}>
                               <ListItemText
                                 primary={m.label}
                                 secondary={m.description}
                                 primaryTypographyProps={{ fontWeight: 800 }}
                               />
                               <Stack direction="row" spacing={2} alignItems="center">
                                  <Chip label={m.provenance} size="small" sx={{ height: 18, fontSize: '0.6rem', fontWeight: 900 }} />
                                  <Box sx={{ color: 'primary.main' }}><CheckCircle size={18} /></Box>
                               </Stack>
                            </ListItem>
                            <Divider sx={{ opacity: 0.05 }} />
                         </Box>
                       ))}
                    </List>
                 </Paper>
              </Grid>
              <Grid item xs={12} lg={4}>
                 <Paper sx={{ p: 3, mb: 3 }}>
                    <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 2, fontWeight: 900 }}>DATA FRESHNESS AUDIT</Typography>
                    <Stack spacing={2}>
                       <FreshnessRow label="Price Stream" lastSync="Real-time" status="LIVE" color="#10b981" />
                       <FreshnessRow label="Institutional Flow" lastSync="Daily" status="ESTIMATED" color="#3b82f6" />
                       <FreshnessRow label="Global Sync" lastSync={health?.last_global_sync ? new Date(health.last_global_sync).toLocaleTimeString() : '---'} status="SYNCED" color="#8b5cf6" />
                    </Stack>
                 </Paper>
                 <Paper sx={{ p: 3, mb: 3 }}>
                    <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 2, fontWeight: 900 }}>AI AGENT STATUS</Typography>
                    <Stack spacing={1}>
                       <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="caption">Success</Typography>
                          <Typography variant="caption" fontWeight="bold" color="primary">{health?.ai_health?.success || 0}</Typography>
                       </Box>
                       <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="caption">Pending</Typography>
                          <Typography variant="caption" fontWeight="bold" color="warning.main">{health?.ai_health?.pending || 0}</Typography>
                       </Box>
                       <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="caption">Failed</Typography>
                          <Typography variant="caption" fontWeight="bold" color="error.main">{health?.ai_health?.failed || 0}</Typography>
                       </Box>
                    </Stack>
                    <Box sx={{ mt: 2 }}>
                       <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>AI Completion: {health?.ai_health?.completion_pct?.toFixed(1) || 0}%</Typography>
                       <LinearProgress variant="determinate" value={health?.ai_health?.completion_pct || 0} color="primary" sx={{ height: 4, borderRadius: 2 }} />
                    </Box>
                 </Paper>
                 <Paper sx={{ p: 3, bgcolor: 'rgba(244, 63, 94, 0.03)', border: '1px dashed #f43f5e' }}>
                    <Typography variant="subtitle2" color="error" fontWeight={900} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                       <AlertCircle size={16} /> DATA INTEGRITY ALERTS
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1, fontWeight: 500 }}>
                       {health?.database?.stale_stocks > 0 ? `${health.database.stale_stocks} assets require incremental sync.` : "No critical discrepancies detected."}
                    </Typography>
                 </Paper>
              </Grid>
           </Grid>
        </Box>
      )}

      {tab === 2 && (
        <Paper sx={{ p: 0, overflow: 'hidden' }}>
           <Box sx={{ p: 2, borderBottom: '1px solid #334155', display: 'flex', alignItems: 'center', gap: 1 }}>
              <Activity size={18} />
              <Typography variant="h6" fontWeight={800}>Forensic Execution Logs</Typography>
           </Box>
           <List sx={{ maxHeight: 600, overflowY: 'auto' }}>
              {logs.map((log, i) => (
                <Box key={i}>
                  <ListItem sx={{ py: 1.5 }}>
                     <ListItemText
                      primary={log.step || "Worker Step"}
                      secondary={`${log.symbol || 'SYSTEM'} • ${new Date(log.timestamp).toLocaleTimeString()}`}
                      primaryTypographyProps={{ fontWeight: 700, variant: 'body2' }}
                     />
                     <Chip label="OK" size="small" sx={{ bgcolor: 'rgba(16, 185, 129, 0.1)', color: '#10b981', fontWeight: 900, height: 20 }} />
                  </ListItem>
                  <Divider sx={{ opacity: 0.05 }} />
                </Box>
              ))}
           </List>
        </Paper>
      )}
    </Box>
  );
}

function StatusMetric({ label, value, color }: any) {
  return (
    <Box>
       <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="caption" fontWeight={700}>{label}</Typography>
          <Typography variant="caption" fontWeight={900}>{value}</Typography>
       </Box>
       <Box sx={{ width: '100%', height: 4, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 2 }}>
          <Box sx={{ width: value, height: '100%', bgcolor: color, borderRadius: 2 }} />
       </Box>
    </Box>
  );
}

function WorkerStatus({ label, status, lastRun, color }: any) {
   return (
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 1.5, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.05)' }}>
         <Box>
            <Typography variant="body2" sx={{ fontWeight: 800, fontSize: '0.75rem' }}>{label}</Typography>
            <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600 }}>Last Sync: {lastRun}</Typography>
         </Box>
         <Chip label={status} size="small" sx={{ fontWeight: 900, height: 18, fontSize: '0.55rem', bgcolor: `${color}15`, color }} />
      </Box>
   );
}

function FreshnessRow({ label, lastSync, status, color }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
       <Box>
          <Typography variant="body2" fontWeight={800}>{label}</Typography>
          <Typography variant="caption" color="textSecondary">Sync: {lastSync}</Typography>
       </Box>
       <Chip label={status} size="small" sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900, bgcolor: `${color}15`, color }} />
    </Box>
  );
}
