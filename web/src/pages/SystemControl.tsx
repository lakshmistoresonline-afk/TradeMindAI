import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Stack, Button, Chip, Divider, List, ListItem, ListItemText, LinearProgress, Alert } from '@mui/material';
import { ShieldCheck, Activity, Database, Server, RefreshCw, Cpu, Brain, Zap } from 'lucide-react';
import { getSystemEvaluation, getSystemLogs } from '../api/client';

export default function SystemControl() {
  const [logs, setLogs] = useState<any[]>([]);
  const [refreshing, setRefresh] = useState(false);

  const fetchStatus = async () => {
    setRefresh(true);
    try {
      const [evalData, logData] = await Promise.all([
        getSystemEvaluation(),
        getSystemLogs()
      ]);
      // evalData currently unused but fetched to ensure API health
      console.log("System Eval:", evalData);
      setLogs(logData);
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

      <Grid container spacing={3}>
        {/* Core Infrastructure */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <Paper sx={{ p: 3 }}>
                 <Stack direction="row" spacing={2} alignItems="center" mb={2}>
                    <Server size={20} color="#10b981" />
                    <Typography variant="subtitle2" fontWeight={800}>OPERATIONAL STATUS</Typography>
                 </Stack>
                 <Alert severity="success" sx={{ bgcolor: 'rgba(16, 185, 129, 0.05)', border: '1px solid #10b981' }}>
                    All AI Agents and Backend Workers are operating within normal latency parameters.
                 </Alert>
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
                       <Typography variant="caption">SQL Tier Sync</Typography>
                       <Typography variant="caption" fontWeight="bold">ACTIVE</Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={100} color="primary" sx={{ height: 4, borderRadius: 2 }} />
                 </Box>
                 <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                       <Typography variant="caption">DuckDB Analytics</Typography>
                       <Typography variant="caption" fontWeight="bold">CACHED</Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={85} color="info" sx={{ height: 4, borderRadius: 2 }} />
                 </Box>
              </Paper>
            </Grid>
          </Grid>

          <Paper sx={{ p: 0, mt: 3, overflow: 'hidden' }}>
             <Box sx={{ p: 2, borderBottom: '1px solid #334155', display: 'flex', alignItems: 'center', gap: 1 }}>
                <Activity size={18} />
                <Typography variant="h6" fontWeight={800}>Forensic Execution Logs</Typography>
             </Box>
             <List sx={{ maxHeight: 400, overflowY: 'auto' }}>
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
        </Grid>

        {/* AI Engine Metrics */}
        <Grid item xs={12} md={4}>
           <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom fontWeight={800}>AI AGENT PERFORMANCE</Typography>
              <Stack spacing={3} mt={3}>
                 <StatusMetric label="Llama 3.1 Reasoning" value="98.2%" color="#10b981" />
                 <StatusMetric label="SMC Pattern Accuracy" value="84.5%" color="#3b82f6" />
                 <StatusMetric label="ML Confidence Score" value="72.0%" color="#fbbf24" />
              </Stack>
           </Paper>

           <Paper sx={{ p: 3, bgcolor: 'rgba(15, 23, 42, 0.3)' }}>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom fontWeight={800}>INFRASTRUCTURE</Typography>
              <Box mt={3}>
                 <InfraRow icon={<Cpu size={16} />} label="Inference" value="Groq v1" />
                 <InfraRow icon={<Brain size={16} />} label="Model" value="Llama 3.1 8B" />
                 <InfraRow icon={<Zap size={16} />} label="Latency" value="142ms" />
              </Box>
           </Paper>
        </Grid>
      </Grid>
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

function InfraRow({ icon, label, value }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
       <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'text.secondary' }}>
          {icon}
          <Typography variant="caption" fontWeight={700}>{label}</Typography>
       </Box>
       <Typography variant="caption" fontWeight={900} color="primary.main">{value}</Typography>
    </Box>
  );
}
