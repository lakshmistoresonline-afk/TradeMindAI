import {
  Box, Typography, Grid, Paper, Stack, Chip, Divider,
  Table, TableBody, TableCell, TableRow, alpha, CircularProgress, Tabs, Tab
} from '@mui/material';
import {
  Activity, Shield, Brain, Globe, RefreshCcw,
  CheckCircle2, Fingerprint, PieChart, TrendingUp, TrendingDown, Clock, Search, Database, Lock, AlertCircle
} from 'lucide-react';
import { useState } from 'react';

interface SignalDetailViewProps {
  signal: any;
  loading?: boolean;
}

export default function SignalDetailView({ signal, loading }: SignalDetailViewProps) {
  const [tab, setTab] = useState(0);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!signal) return null;

  return (
    <Box sx={{ color: 'white' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'rgba(255,255,255,0.05)', mb: 3 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} variant="scrollable" scrollButtons="auto">
          <Tab label="EXECUTIVE SUMMARY" sx={{ fontWeight: 900, fontSize: '0.7rem' }} />
          <Tab label="PRICE & EXECUTION" sx={{ fontWeight: 900, fontSize: '0.7rem' }} />
          <Tab label="AI & PROVENANCE" sx={{ fontWeight: 900, fontSize: '0.7rem' }} />
          <Tab label="AUDIT & INTEGRITY" sx={{ fontWeight: 900, fontSize: '0.7rem' }} />
        </Tabs>
      </Box>

      {tab === 0 && (
        <Grid container spacing={3}>
          {/* A. SIGNAL IDENTITY */}
          <Grid item xs={12} md={6}>
            <SectionHeader icon={<Shield size={18} />} title="A. SIGNAL IDENTITY" />
            <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.01) }}>
              <DataRow label="SIGNAL ID" value={signal.id} />
              <DataRow label="SYMBOL" value={signal.symbol} bold color="primary.main" />
              <DataRow label="DIRECTION" value={signal.direction}
                 color={signal.direction === 'LONG' ? '#10b981' : '#ef4444'} bold />
              <DataRow label="ASSET TYPE" value={signal.asset_type || "EQUITY"} />
              <DataRow label="STRATEGY" value={signal.strategy_version || "V2.2 FROZEN"} />
              <DataRow label="VERIFICATION" value={getVerificationLabel(signal.verification_level)}
                 color={signal.verification_level >= 3 ? '#10b981' : '#f59e0b'} bold />
            </Paper>
          </Grid>

          {/* B. DECISION SUMMARY */}
          <Grid item xs={12} md={6}>
            <SectionHeader icon={<TrendingUp size={18} />} title="B. DECISION" />
            <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.01) }}>
              <DataRow label="RATING" value={signal.signal_rating || signal.rating} />
              <DataRow label="CONVICTION" value={`${signal.conviction || '--'}%`} bold />
              <DataRow label="LIFECYCLE STATE" value={signal.lifecycle_state || "TERMINAL"} />
              <DataRow label="STATUS" value={signal.status} bold color={getStatusColor(signal.status)} />
              <DataRow label="OUTCOME" value={signal.outcome_status || signal.status} />
            </Paper>
          </Grid>

          {/* G. CURRENT STATUS & P&L */}
          <Grid item xs={12}>
            <SectionHeader icon={<Activity size={18} />} title="G. CURRENT STATUS & P&L" />
            <Paper variant="outlined" sx={{ p: 3, bgcolor: alpha('#fff', 0.02), border: '1px solid rgba(0, 209, 255, 0.2)' }}>
              <Grid container spacing={4}>
                 <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="slategray" sx={{ fontWeight: 900 }}>NET P&L %</Typography>
                    <Typography variant="h4" sx={{ fontWeight: 950, color: (signal.net_pnl || 0) >= 0 ? '#10b981' : '#ef4444' }}>
                       {signal.net_pnl !== null ? `${signal.net_pnl > 0 ? '+' : ''}${signal.net_pnl.toFixed(2)}%` : '--'}
                    </Typography>
                 </Grid>
                 <Grid item xs={6} md={3}>
                    <Typography variant="caption" color="slategray" sx={{ fontWeight: 900 }}>EXIT PRICE</Typography>
                    <Typography variant="h4" sx={{ fontWeight: 950 }}>{signal.exit_price ? `₹${signal.exit_price.toFixed(2)}` : '--'}</Typography>
                 </Grid>
                 <Grid item xs={12} md={6}>
                    <DataRow label="HOLDING PERIOD" value={formatDuration(signal.created_at || signal.timestamp, signal.exit_timestamp || signal.outcome_timestamp)} />
                    <DataRow label="MAE (Max Adverse)" value={`${signal.mae?.toFixed(2)}%`} color="#ef4444" />
                    <DataRow label="MFE (Max Favorable)" value={`${signal.mfe?.toFixed(2)}%`} color="#10b981" />
                 </Grid>
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      )}

      {tab === 1 && (
        <Grid container spacing={3}>
          {/* C. PRICE & D. TARGET/STOP */}
          <Grid item xs={12} md={6}>
            <SectionHeader icon={<Database size={18} />} title="C. PRICING" />
            <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.01) }}>
              <DataRow label="ENTRY PRICE" value={`₹${signal.entry?.toFixed(2)}`} />
              <DataRow label="ENTRY ZONE LOW" value={signal.entry_zone_low ? `₹${signal.entry_zone_low.toFixed(2)}` : 'UNAVAILABLE'} />
              <DataRow label="ENTRY ZONE HIGH" value={signal.entry_zone_high ? `₹${signal.entry_zone_high.toFixed(2)}` : 'UNAVAILABLE'} />
              <DataRow label="CURRENT PRICE" value={signal.current_price ? `₹${signal.current_price.toFixed(2)}` : 'UNAVAILABLE'} bold />
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <SectionHeader icon={<Lock size={18} />} title="D. TARGET / STOP" />
            <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.01) }}>
              <DataRow label="TARGET PRICE" value={`₹${signal.target?.toFixed(2)}`} color="#10b981" bold />
              <DataRow label="STOP LOSS" value={`₹${signal.stop?.toFixed(2)}`} color="#ef4444" bold />
              <DataRow label="REWARD AMOUNT" value={signal.reward_amount_abs ? `₹${signal.reward_amount_abs.toFixed(2)}` : '--'} />
              <DataRow label="RISK AMOUNT" value={signal.risk_amount_abs ? `₹${signal.risk_amount_abs.toFixed(2)}` : '--'} />
            </Paper>
          </Grid>

          {/* J. TIMELINE */}
          <Grid item xs={12}>
            <SectionHeader icon={<Clock size={18} />} title="J. TIMELINE" />
            <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.01) }}>
               <Grid container spacing={2}>
                  <Grid item xs={6} md={3}><TimelineItem label="CREATED" value={formatIST(signal.created_at)} /></Grid>
                  <Grid item xs={6} md={3}><TimelineItem label="SIGNAL TIMESTAMP" value={formatIST(signal.signal_timestamp || signal.timestamp)} /></Grid>
                  <Grid item xs={6} md={3}><TimelineItem label="ENTRY AT" value={formatIST(signal.entry_timestamp)} /></Grid>
                  <Grid item xs={6} md={3}><TimelineItem label="EXIT AT" value={formatIST(signal.exit_timestamp || signal.outcome_timestamp)} /></Grid>
               </Grid>
            </Paper>
          </Grid>
        </Grid>
      )}

      {tab === 2 && (
        <Grid container spacing={3}>
           {/* E. PROBABILITY & F. EV */}
           <Grid item xs={12} md={6}>
            <SectionHeader icon={<Brain size={18} />} title="E. PROBABILITY" />
            <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.01) }}>
              <DataRow label="RAW PROBABILITY" value={signal.raw_probability ? `${(signal.raw_probability * 100).toFixed(2)}%` : 'UNAVAILABLE'} />
              <DataRow label="CALIBRATED PROB" value={signal.calibrated_probability ? `${(signal.calibrated_probability * 100).toFixed(2)}%` : 'UNAVAILABLE'} bold />
              <DataRow label="CALIBRATION STATUS" value={signal.calibrated_probability ? "WELL_CALIBRATED (Low Conf)" : "UNAVAILABLE"} />
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <SectionHeader icon={<TrendingUp size={18} />} title="F. EV / R:R" />
            <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.01) }}>
              <DataRow label="EXPECTED VALUE" value={signal.ev ? `+${signal.ev.toFixed(4)}` : 'UNAVAILABLE'} color="#10b981" bold />
              <DataRow label="RISK/REWARD" value={signal.rr?.toFixed(2) || "1.00"} />
              <DataRow label="EXPECTED RETURN" value={signal.expected_return ? `${(signal.expected_return * 100).toFixed(2)}%` : 'UNAVAILABLE'} />
            </Paper>
          </Grid>

          {/* L. PROVENANCE */}
          <Grid item xs={12}>
            <SectionHeader icon={<Fingerprint size={18} />} title="L. PROVENANCE (WHY THIS SIGNAL?)" />
            <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.01) }}>
               {signal.provenance_data ? (
                 <Box>
                    <DataRow label="PROVENANCE ID" value={signal.provenance_data.id} />
                    <DataRow label="MODEL VERSION" value={signal.provenance_data.model_version} />
                    <DataRow label="DATA SOURCES" value={Object.keys(signal.provenance_data.data_sources).join(', ')} />
                    <DataRow label="INPUT HASH" value={signal.provenance_data.input_hash} />
                    <Divider sx={{ my: 2, opacity: 0.1 }} />
                    <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900 }}>DATA SNAPSHOT TIMESTAMPS</Typography>
                    <Grid container spacing={1} sx={{ mt: 1 }}>
                       {Object.entries(signal.provenance_data.source_timestamps).map(([k, v]: [string, any]) => (
                          <Grid item xs={12} md={4} key={k}>
                             <Typography variant="caption" display="block" color="textSecondary">{k.toUpperCase()}</Typography>
                             <Typography variant="body2" sx={{ fontFamily: 'JetBrains Mono', fontSize: '0.65rem' }}>{v}</Typography>
                          </Grid>
                       ))}
                    </Grid>
                 </Box>
               ) : (
                 <Typography variant="body2" color="text.secondary">Detailed provenance not snapshotted for this record (Legacy/Unverified).</Typography>
               )}
            </Paper>
          </Grid>
        </Grid>
      )}

      {tab === 3 && (
        <Grid container spacing={3}>
           {/* O. RECONCILIATION */}
           <Grid item xs={12}>
              <SectionHeader icon={<RefreshCcw size={18} />} title="O. RECONCILIATION" />
              <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.01) }}>
                 <DataRow label="LAST RECONCILED" value={formatIST(signal.last_reconciled_at)} />
                 <DataRow label="AUDIT STATUS" value={signal.audit_status || "PENDING"} bold color="#10b981" />
                 <DataRow label="AUTHORITY" value="NEON / POSTGRES" />
                 <DataRow label="RECORD HASH" value={signal.record_hash || "UNAVAILABLE"} />
              </Paper>
           </Grid>

           {/* H. AUDIT TRAIL */}
           <Grid item xs={12}>
            <SectionHeader icon={<Search size={18} />} title="Q. AUDIT HISTORY (STATE TRANSITIONS)" />
            <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.01) }}>
               {signal.audit_trail && signal.audit_trail.length > 0 ? (
                  <Stack spacing={2}>
                     {signal.audit_trail.map((evt: any, idx: number) => (
                        <Box key={idx} sx={{ display: 'flex', justifyContent: 'space-between', borderLeft: '2px solid', borderColor: 'primary.main', pl: 2 }}>
                           <Box>
                              <Typography variant="body2" sx={{ fontWeight: 800 }}>{evt.type}</Typography>
                              <Typography variant="caption" color="text.secondary">{evt.reason || 'Transition Verified'}</Typography>
                           </Box>
                           <Typography variant="caption" sx={{ fontFamily: 'JetBrains Mono' }}>{formatIST(evt.timestamp)}</Typography>
                        </Box>
                     ))}
                  </Stack>
               ) : (
                  <Typography variant="body2" color="text.secondary">Audit trail for this signal is currently being synchronized.</Typography>
               )}
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}

function SectionHeader({ icon, title }: any) {
  return (
    <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 1.5 }}>
      <Box sx={{ color: 'primary.main' }}>{icon}</Box>
      <Typography variant="caption" sx={{ fontWeight: 950, letterSpacing: 1.5, color: 'slategray' }}>{title}</Typography>
    </Stack>
  );
}

function DataRow({ label, value, color, bold }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.2, gap: 2 }}>
      <Typography variant="caption" sx={{ fontWeight: 800, color: 'slategray', whiteSpace: 'nowrap' }}>{label}</Typography>
      <Typography variant="body2" sx={{ fontWeight: bold ? 950 : 700, color: color || 'white', fontFamily: 'JetBrains Mono', textAlign: 'right', wordBreak: 'break-all' }}>
        {value || '--'}
      </Typography>
    </Box>
  );
}

function TimelineItem({ label, value }: any) {
  return (
    <Box>
       <Typography variant="caption" color="slategray" sx={{ fontWeight: 900, display: 'block' }}>{label}</Typography>
       <Typography variant="body2" sx={{ fontFamily: 'JetBrains Mono', fontSize: '0.7rem' }}>{value || '--'}</Typography>
    </Box>
  );
}

function getVerificationLabel(level: number) {
  const labels: any = {
    0: "LEVEL 0 - UNVERIFIED",
    1: "LEVEL 1 - LOG ONLY",
    2: "LEVEL 2 - RECONSTRUCTED",
    3: "LEVEL 3 - MARKET VERIFIED",
    4: "LEVEL 4 - EXECUTION VERIFIED",
    5: "LEVEL 5 - PORTFOLIO VERIFIED"
  };
  return labels[level] || `LEVEL ${level}`;
}

function getStatusColor(status: string) {
  if (status === 'TARGET_HIT') return '#10b981';
  if (status === 'STOP_LOSS') return '#ef4444';
  if (status === 'ACTIVE') return '#00D1FF';
  return 'white';
}

const formatIST = (timestamp: string | null) => {
  if (!timestamp) return '--';
  try {
    const date = new Date(timestamp);
    return date.toLocaleString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false
    }) + ' IST';
  } catch { return timestamp; }
};

const formatDuration = (start: string | null, end: string | null) => {
  if (!start) return '--';
  try {
    const s = new Date(start).getTime();
    const e = end ? new Date(end).getTime() : new Date().getTime();
    const diff = e - s;
    if (diff < 0) return '--';
    const mins = Math.floor(diff / (1000 * 60));
    const hrs = Math.floor(mins / 60);
    const days = Math.floor(hrs / 24);
    if (days > 0) return `${days}d ${hrs % 24}h ${mins % 60}m`;
    if (hrs > 0) return `${hrs}h ${mins % 60}m`;
    return `${mins}m`;
  } catch { return '--'; }
};
