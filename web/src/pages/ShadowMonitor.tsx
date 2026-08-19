
import { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Paper, Stack, Chip, Divider,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, alpha, LinearProgress
} from '@mui/material';
import {
  Activity,
  Clock,
  RefreshCcw,
  Zap,
  AlertTriangle
} from 'lucide-react';
import { getShadowStatus, getShadowSummary, getShadowActiveSignals, getShadowUniverse, getShadowPerformance, getShadowHealth } from '../api/client';

export default function ShadowMonitor() {
  const [status, setStatus] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);
  const [activeSignals, setActiveSignals] = useState<any[]>([]);
  const [universe, setUniverse] = useState<any[]>([]);
  const [perf, setPerf] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());

  const fetchData = async () => {
    try {
      const [sStatus, sSum, sActive, sUni, sPerf, sHealth] = await Promise.all([
        getShadowStatus(),
        getShadowSummary(),
        getShadowActiveSignals(),
        getShadowUniverse(),
        getShadowPerformance(),
        getShadowHealth()
      ]);
      setStatus(sStatus);
      setSummary(sSum);
      setActiveSignals(sActive);
      setUniverse(sUni);
      setPerf(sPerf);
      setHealth(sHealth);
      setLastRefreshed(new Date());
    } catch (err) {
      console.error("Failed to fetch shadow data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // 30s auto-refresh
    return () => clearInterval(interval);
  }, []);

  if (loading && !status) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
            SHADOW MONITOR <Chip label="STRATEGY v2.2" color="primary" size="small" sx={{ fontWeight: 900, borderRadius: 0.5 }} />
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 700 }}>
            <Clock size={14} style={{ verticalAlign: 'middle', marginRight: 8 }} />
            BASELINE START: {status?.baseline_start} | LAST REFRESHED: {lastRefreshed.toLocaleTimeString()}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, display: 'block', mt: 0.5 }}>
            LAST CLOUD CYCLE: {health?.last_shadow_cycle || 'N/A'} | WORKER HB: {health?.last_worker_heartbeat || 'N/A'}
          </Typography>
        </Box>
        <Stack direction="row" spacing={2}>
           <StatusBadge label="ENGINE" status={health?.shadow_worker || "HEALTHY"} color={health?.shadow_worker === 'ONLINE' ? "#10b981" : "#f59e0b"} />
           <StatusBadge label="STRATEGY" status="FROZEN" color="#00D1FF" />
           <StatusBadge label="SAMPLE" status={perf?.sample_status || "INSUFFICIENT"} color="#f59e0b" />
        </Stack>
      </Stack>

      <Grid container spacing={3}>
        {/* Metric Grid */}
        <Grid item xs={12} md={3}>
          <MetricCard title="EVALUATION CYCLES" value={summary?.evaluation_cycles || 0} icon={<RefreshCcw size={20} color="#00D1FF" />} />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard title="EVALUATION EVENTS" value={summary?.evaluation_events || 0} icon={<Activity size={20} color="#7C3AED" />} />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard title="STRATEGY TRIGGER EVENTS" value={summary?.strategy_trigger_events || 0} icon={<Zap size={20} color="#f59e0b" />} />
        </Grid>
        <Grid item xs={12} md={3}>
          <ProgressCard title="COMPLETED TRADES" current={perf?.completed_trades || 0} target={20} />
        </Grid>

        {/* Active Signals */}
        <Grid item xs={12} md={8}>
           <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 900, fontSize: '0.9rem', letterSpacing: 1 }}>ACTIVE SIGNALS</Typography>
              {activeSignals.length === 0 ? (
                <Box sx={{ py: 6, textAlign: 'center', bgcolor: alpha('#fff', 0.02), borderRadius: 1 }}>
                   <Typography color="text.secondary" sx={{ fontWeight: 700 }}>ACTIVE SIGNAL = NONE</Typography>
                </Box>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>SYMBOL</TableCell>
                        <TableCell>DIRECTION</TableCell>
                        <TableCell>ENTRY</TableCell>
                        <TableCell>PROB</TableCell>
                        <TableCell>EV</TableCell>
                        <TableCell>STATUS</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {activeSignals.map((sig) => (
                        <TableRow key={sig.id}>
                          <TableCell sx={{ fontWeight: 900, color: 'primary.main' }}>{sig.symbol}</TableCell>
                          <TableCell>
                            <Chip
                              label={sig.direction}
                              size="small"
                              sx={{ fontWeight: 900, borderRadius: 0.5, bgcolor: sig.direction === 'LONG' ? alpha('#10b981', 0.1) : alpha('#ef4444', 0.1), color: sig.direction === 'LONG' ? '#10b981' : '#ef4444' }}
                            />
                          </TableCell>
                          <TableCell sx={{ fontFamily: 'JetBrains Mono' }}>{sig.entry.toFixed(2)}</TableCell>
                          <TableCell sx={{ fontWeight: 800 }}>{(sig.probability * 100).toFixed(1)}%</TableCell>
                          <TableCell sx={{ color: 'success.main', fontWeight: 800 }}>+{sig.ev.toFixed(2)}</TableCell>
                          <TableCell>
                             <Chip label={sig.status} size="small" variant="outlined" sx={{ fontWeight: 800, fontSize: '0.6rem' }} />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
           </Paper>
        </Grid>

        {/* Performance Overview */}
        <Grid item xs={12} md={4}>
           <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 900, fontSize: '0.9rem', letterSpacing: 1 }}>PERFORMANCE MONITOR</Typography>
              <Stack spacing={3}>
                 <PerfRow label="WIN RATE" value={`${perf?.win_rate || 0}%`} baseline="58.77%" />
                 <PerfRow label="NET EV" value={`${perf?.net_ev || 0}%`} baseline="0.3262%" />
                 <PerfRow label="PROB MEAN" value={perf?.probability_mean || "0.6293"} baseline="0.5870" />

                 <Box sx={{ mt: 2, p: 2, bgcolor: alpha('#f59e0b', 0.05), border: '1px solid rgba(245, 158, 11, 0.2)', borderRadius: 1 }}>
                    <Typography variant="caption" sx={{ color: '#f59e0b', fontWeight: 900, display: 'flex', alignItems: 'center', gap: 1 }}>
                       <AlertTriangle size={14} /> INSUFFICIENT SAMPLE
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'slategray', display: 'block', mt: 1, fontWeight: 700 }}>
                       Statistics are descriptive only. Statistical validation remains HOLD until 20 completed trades.
                    </Typography>
                 </Box>
              </Stack>
           </Paper>
        </Grid>

        {/* NIFTY 200 Rejection Table */}
        <Grid item xs={12}>
           <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 900, fontSize: '0.9rem', letterSpacing: 1 }}>UNIVERSE SCAN AUDIT (200 SYMBOLS)</Typography>
              <TableContainer sx={{ maxHeight: 600 }}>
                <Table stickyHeader size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>SYMBOL</TableCell>
                      <TableCell>MODELS</TableCell>
                      <TableCell>DECISION</TableCell>
                      <TableCell>REJECTION REASON</TableCell>
                      <TableCell>PROB</TableCell>
                      <TableCell>EV</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {universe.map((stock) => (
                      <TableRow key={stock.symbol} hover>
                        <TableCell sx={{ fontWeight: 900 }}>{stock.symbol}</TableCell>
                        <TableCell>
                           <Chip
                             label={stock.model_status}
                             size="small"
                             sx={{ fontSize: '0.6rem', fontWeight: 900, bgcolor: stock.model_status === 'READY' ? alpha('#10b981', 0.1) : alpha('#ef4444', 0.1), color: stock.model_status === 'READY' ? '#10b981' : '#ef4444' }}
                           />
                        </TableCell>
                        <TableCell>
                           <Chip
                             label={stock.decision}
                             size="small"
                             sx={{ fontWeight: 950, fontSize: '0.6rem', borderRadius: 0.5, bgcolor: stock.decision === 'TRADE_SIGNAL' ? '#10b981' : 'transparent', color: stock.decision === 'TRADE_SIGNAL' ? '#000' : 'text.secondary' }}
                           />
                        </TableCell>
                        <TableCell sx={{ fontSize: '0.75rem', fontWeight: 700, color: 'slategray' }}>
                          {stock.rejection_reason || '-'}
                        </TableCell>
                        <TableCell sx={{ fontWeight: 800 }}>{stock.probability ? `${(stock.probability*100).toFixed(1)}%` : '-'}</TableCell>
                        <TableCell sx={{ fontWeight: 800, color: stock.ev > 0 ? 'success.main' : 'error.main' }}>
                          {stock.ev ? `+${stock.ev.toFixed(2)}` : '-'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
           </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function MetricCard({ title, value, icon }: any) {
  return (
    <Paper sx={{ p: 2.5, border: '1px solid rgba(255,255,255,0.05)' }}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray', letterSpacing: 1.5 }}>{title}</Typography>
          <Typography variant="h4" sx={{ fontWeight: 950, mt: 1, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
        </Box>
        <Box sx={{ p: 1, bgcolor: alpha('#fff', 0.03), borderRadius: 1 }}>{icon}</Box>
      </Stack>
    </Paper>
  );
}

function ProgressCard({ title, current, target }: any) {
  const pct = (current / target) * 100;
  return (
    <Paper sx={{ p: 2.5, border: '1px solid rgba(255,255,255,0.05)', position: 'relative', overflow: 'hidden' }}>
      <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray', letterSpacing: 1.5 }}>{title}</Typography>
      <Stack direction="row" alignItems="baseline" spacing={1} sx={{ mt: 1 }}>
         <Typography variant="h4" sx={{ fontWeight: 950, fontFamily: 'JetBrains Mono' }}>{current}</Typography>
         <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 800 }}>/ {target}</Typography>
      </Stack>
      <Box sx={{ mt: 2 }}>
         <LinearProgress variant="determinate" value={pct} sx={{ height: 6, borderRadius: 3, bgcolor: alpha('#fff', 0.05), '& .MuiLinearProgress-bar': { borderRadius: 3 } }} />
      </Box>
    </Paper>
  );
}

function StatusBadge({ label, status, color }: any) {
  return (
    <Box sx={{ px: 2, py: 0.8, borderRadius: 1, border: `1px solid ${alpha(color, 0.2)}`, bgcolor: alpha(color, 0.05) }}>
       <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 950, fontSize: '0.65rem', mr: 1.5 }}>{label}:</Typography>
       <Typography variant="caption" sx={{ color: color, fontWeight: 950, fontSize: '0.65rem' }}>{status}</Typography>
    </Box>
  );
}

function PerfRow({ label, value, baseline }: any) {
  return (
    <Box>
       <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
          <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray' }}>{label}</Typography>
          <Typography variant="caption" sx={{ fontWeight: 900, color: 'primary.main' }}>LIVE: {value}</Typography>
       </Stack>
       <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="body2" sx={{ fontWeight: 800 }}>BASELINE: {baseline}</Typography>
          <Chip label="FROZEN" size="small" sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900, bgcolor: alpha('#fff', 0.05) }} />
       </Stack>
       <Divider sx={{ mt: 1.5, opacity: 0.05 }} />
    </Box>
  );
}
