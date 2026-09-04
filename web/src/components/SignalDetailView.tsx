import {
  Box, Typography, Grid, Paper, Stack, Chip, Divider,
  Table, TableBody, TableCell, TableRow, alpha, CircularProgress
} from '@mui/material';
import {
  Activity, Shield, Brain, Globe, RefreshCcw,
  CheckCircle2, Fingerprint, PieChart, TrendingUp, TrendingDown
} from 'lucide-react';

interface SignalDetailViewProps {
  signal: any;
  loading?: boolean;
}

export default function SignalDetailView({ signal, loading }: SignalDetailViewProps) {
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
      <Grid container spacing={3}>
        {/* A. Decision & Identity */}
        <Grid item xs={12} md={6}>
          <SectionHeader icon={<Shield size={18} />} title="A. DECISION & IDENTITY" />
          <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.02) }}>
            <DataRow label="SIGNAL ID" value={signal.id} />
            <DataRow label="SYMBOL" value={signal.symbol} bold color="primary.main" />
            <DataRow label="DIRECTION" value={signal.direction}
               color={signal.direction === 'LONG' ? '#10b981' : '#ef4444'} bold />
            <DataRow label="STRATEGY" value="V2.2 FROZEN" />
            <DataRow label="STATUS" value={signal.status} />
          </Paper>
        </Grid>

        {/* B. Price & Risk */}
        <Grid item xs={12} md={6}>
          <SectionHeader icon={<Activity size={18} />} title="B. PRICE & RISK" />
          <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.02) }}>
            <DataRow label="ENTRY PRICE" value={signal.entry?.toFixed(2)} />
            <DataRow label="TARGET PRICE" value={signal.target?.toFixed(2)} color="#10b981" />
            <DataRow label="STOP LOSS" value={signal.stop?.toFixed(2)} color="#ef4444" />
            <DataRow label="RISK/REWARD" value="1.0 (Fixed)" />
            <DataRow label="SLIPPAGE MODEL" value="0.10%" />
          </Paper>
        </Grid>

        {/* C. AI / ML Intelligence */}
        <Grid item xs={12} md={6}>
          <SectionHeader icon={<Brain size={18} />} title="C. AI/ML INTELLIGENCE" />
          <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.02) }}>
            <DataRow label="PROBABILITY" value={`${(signal.probability * 100).toFixed(1)}%`} bold />
            <DataRow label="EXPECTED VALUE" value={`+${signal.ev?.toFixed(4)}`} color="#10b981" />
            <DataRow label="MODEL VERSION" value={signal.model_version} />
            <DataRow label="PREDICTION ID" value={signal.prediction_id || 'N/A'} />
          </Paper>
        </Grid>

        {/* D. Market Context */}
        <Grid item xs={12} md={6}>
          <SectionHeader icon={<Globe size={18} />} title="D. MARKET CONTEXT" />
          <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.02) }}>
            <DataRow label="REGIME" value={signal.regime} bold />
            <DataRow label="SECTOR" value={signal.sector} />
            <DataRow label="TIMEFRAME" value="SWING" />
            <DataRow label="UNIVERSE" value="NIFTY 200" />
          </Paper>
        </Grid>

        {/* F. Outcome & Forensic Analytics */}
        <Grid item xs={12}>
          <SectionHeader icon={<CheckCircle2 size={18} />} title="F. OUTCOME & FORENSIC ANALYTICS" />
          <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.02) }}>
            <Grid container spacing={4}>
               <Grid item xs={12} md={4}>
                  <DataRow label="EXIT PRICE" value={signal.exit_price?.toFixed(2) || '--'} bold />
                  <DataRow label="EXIT TIME" value={signal.exit_timestamp || '--'} />
               </Grid>
               <Grid item xs={12} md={4}>
                  <DataRow label="GROSS P&L" value={`${signal.pnl_percentage?.toFixed(2)}%`}
                     color={(signal.pnl_percentage || 0) > 0 ? '#10b981' : '#ef4444'} bold />
                  <DataRow label="NET P&L (FRICTION)" value={`${signal.net_pnl?.toFixed(2)}%`} bold />
               </Grid>
               <Grid item xs={12} md={4}>
                  <DataRow label="MAE (Max Adverse)" value={`${signal.mae?.toFixed(2)}%`} color="#ef4444" />
                  <DataRow label="MFE (Max Favorable)" value={`${signal.mfe?.toFixed(2)}%`} color="#10b981" />
               </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* G. Provenance (Workstream 8) */}
        <Grid item xs={12}>
          <SectionHeader icon={<Fingerprint size={18} />} title="G. PROVENANCE (WHY THIS SIGNAL?)" />
          <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.02) }}>
             {signal.prediction?.metadata ? (
                <Grid container spacing={2}>
                   {Object.entries(signal.prediction.metadata).map(([k, v]: [string, any]) => (
                      <Grid item xs={6} md={3} key={k}>
                         <Typography variant="caption" sx={{ color: 'slategray', display: 'block' }}>{k.toUpperCase()}</Typography>
                         <Typography variant="body2" sx={{ fontWeight: 700 }}>{String(v)}</Typography>
                      </Grid>
                   ))}
                </Grid>
             ) : (
                <Typography variant="body2" color="text.secondary">Detailed input features not snapshotted for this record.</Typography>
             )}
          </Paper>
        </Grid>

        {/* H. Audit Trail */}
        <Grid item xs={12}>
          <SectionHeader icon={<RefreshCcw size={18} />} title="H. AUDIT TRAIL (STATE TRANSITIONS)" />
          <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.02) }}>
             {signal.audit_trail && signal.audit_trail.length > 0 ? (
                <Stack spacing={2}>
                   {signal.audit_trail.map((evt: any, idx: number) => (
                      <Box key={idx} sx={{ display: 'flex', justifyContent: 'space-between', borderLeft: '2px solid', borderColor: 'primary.main', pl: 2 }}>
                         <Box>
                            <Typography variant="body2" sx={{ fontWeight: 800 }}>{evt.type}</Typography>
                            <Typography variant="caption" color="text.secondary">{evt.reason || 'Transition Verified'}</Typography>
                         </Box>
                         <Typography variant="caption" sx={{ fontFamily: 'JetBrains Mono' }}>{evt.timestamp}</Typography>
                      </Box>
                   ))}
                </Stack>
             ) : (
                <Typography variant="body2" color="text.secondary">Audit trail for this signal is currently being synchronized.</Typography>
             )}
          </Paper>
        </Grid>

        {/* I. Portfolio Impact */}
        <Grid item xs={12}>
          <SectionHeader icon={<PieChart size={18} />} title="I. PORTFOLIO IMPACT" />
          <Paper variant="outlined" sx={{ p: 2, bgcolor: alpha('#fff', 0.02) }}>
            <DataRow label="CAPITAL ALLOCATION" value="₹1,00,000" />
            <DataRow label="ESTIMATED FRICTION" value="₹200 (0.20%)" />
            <DataRow label="POSITION WEIGHT" value="10.0%" />
          </Paper>
        </Grid>
      </Grid>
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
    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
      <Typography variant="caption" sx={{ fontWeight: 800, color: 'slategray' }}>{label}</Typography>
      <Typography variant="body2" sx={{ fontWeight: bold ? 950 : 700, color: color || 'white', fontFamily: 'JetBrains Mono' }}>
        {value || '--'}
      </Typography>
    </Box>
  );
}
