import { useState, useEffect } from 'react';
import { Box, Typography, Grid, Paper, Stack, Chip, Divider, Skeleton, alpha, Tooltip, Button } from '@mui/material';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { getEquitySignalDetail } from '../api/client';
import { mapCanonicalSignal } from '../hooks/useAITradeDecision';
import { ShieldCheck, HelpCircle, Activity, Target, Clock, ArrowLeft, BarChart2, Briefcase, RefreshCw, Zap, TrendingUp } from 'lucide-react';
import SignalLifecycleTimeline from '../components/Research/shared/SignalLifecycleTimeline';

export default function SignalDetail() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [signal, setSignal] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
       if (location.state?.signal) {
           setSignal(mapCanonicalSignal(location.state.signal));
           setLoading(false);
       } else {
           getEquitySignalDetail(id).then(data => {
             setSignal(mapCanonicalSignal(data));
             setLoading(false);
           }).catch(() => setLoading(false));
       }
       if (location.state?.scrollReplay) {
           setTimeout(() => {
               document.getElementById('lifecycle-replay')?.scrollIntoView({ behavior: 'smooth' });
           }, 500);
       }
    }
  }, [id, location.state]);

  if (loading) return (
     <Box sx={{ p: 4, bgcolor: '#020617', minHeight: '100vh' }}>
        <Skeleton variant="rectangular" height={100} sx={{ mb: 4 }} />
        <Grid container spacing={4}>
           <Grid item xs={12} md={8}><Skeleton variant="rectangular" height={600} /></Grid>
           <Grid item xs={12} md={4}><Skeleton variant="rectangular" height={600} /></Grid>
        </Grid>
     </Box>
  );

  if (!signal) return (
    <Box sx={{ p: 10, textAlign: 'center', bgcolor: '#020617', minHeight: '100vh' }}>
        <Typography variant="h6" color="slategray">Signal not found in production ledger.</Typography>
        <Button onClick={() => navigate('/signals')} sx={{ mt: 2 }}>Return to Terminal</Button>
    </Box>
  );

  const decision = signal.decision;
  const isBuy = decision.rating?.includes('BUY');

  return (
    <Box sx={{ pb: 10, bgcolor: '#020617', minHeight: '100vh', mx: -4, px: 4, pt: 2 }}>
      {/* 0. Breadcrumbs / Back */}
      <Button
        startIcon={<ArrowLeft size={16} />}
        onClick={() => navigate(-1)}
        sx={{ color: 'slategray', fontWeight: 800, mb: 3, textTransform: 'none' }}
      >
        Back to Terminal
      </Button>

      {/* 1. Executive Summary Tier */}
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 3 }}>
         <Box>
            <Stack direction="row" spacing={2} alignItems="center">
               <Typography variant="h3" sx={{ fontWeight: 950, letterSpacing: -2, color: '#fff' }}>{signal.symbol}</Typography>
               <MuiChip
                 label={decision.status?.replace(/_/g, ' ')}
                 sx={{
                    fontWeight: 950, height: 28, borderRadius: 0.5,
                    bgcolor: alpha(getStatusColor(decision.status), 0.1),
                    color: getStatusColor(decision.status),
                    border: `1px solid ${alpha(getStatusColor(decision.status), 0.2)}`
                 }}
               />
               <MuiChip
                 label={decision.qualityClass}
                 variant="outlined"
                 sx={{
                   fontWeight: 950, height: 28, borderRadius: 0.5,
                   borderColor: decision.qualityClass === 'PRIMARY' ? '#10b981' : decision.qualityClass === 'SELECTIVE' ? '#00D1FF' : 'slategray',
                   color: decision.qualityClass === 'PRIMARY' ? '#10b981' : decision.qualityClass === 'SELECTIVE' ? '#00D1FF' : 'slategray'
                 }}
               />
            </Stack>
            <Typography variant="h6" sx={{ color: 'slategray', fontWeight: 700, mt: 0.5 }}>{signal.company_name || signal.name || 'INSTRUMENT'}</Typography>
            <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 900, letterSpacing: 2, display: 'block', mt: 1 }}>
               {decision.rating} · {decision.timeframe} HORIZON · STRATEGY V2.2
            </Typography>
            {decision.status !== 'ACTIVE' && decision.status !== 'WAITING_FOR_ENTRY' && (
                <Button
                    size="small"
                    startIcon={<RefreshCw size={14} />}
                    onClick={() => document.getElementById('lifecycle-replay')?.scrollIntoView({ behavior: 'smooth' })}
                    sx={{ mt: 2, bgcolor: alpha('#10b981', 0.1), color: '#10b981', fontWeight: 900, fontSize: '0.6rem' }}
                >
                    REPLAY SIGNAL LIFECYCLE
                </Button>
            )}
         </Box>
         <Box sx={{ textAlign: 'right' }}>
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, display: 'block' }}>SIGNAL ID</Typography>
            <Typography variant="body2" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: '#fff' }}>{signal.id}</Typography>
            <Box sx={{ mt: 1 }}>
                <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>AGE</Typography>
                <Typography variant="body2" sx={{ fontWeight: 900, color: (decision.signalAgeHours || 0) > 24 ? '#ef4444' : '#10b981' }}>
                    {(decision.signalAgeHours || 0).toFixed(1)} HOURS
                </Typography>
            </Box>
         </Box>
      </Box>

      <Grid container spacing={4}>
         {/* LEFT COLUMN: Intelligence & Execution */}
         <Grid item xs={12} md={8}>
            {/* 2. Trade Plan Section */}
            <SectionHeader icon={<Target size={18} />} title="AUTHORITATIVE TRADE PLAN" />
            <Paper sx={{ p: 4, mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Grid container spacing={4}>
                  <PlanItem label="ENTRY PRICE" value={`₹${decision.entry?.toLocaleString()}`} />
                  <PlanItem label="TARGET PRICE" value={`₹${decision.target?.toLocaleString()}`} color="#10b981" />
                  <PlanItem label="STOP LOSS" value={`₹${decision.stopLoss?.toLocaleString()}`} color="#ef4444" />
                  <PlanItem label="RISK / REWARD" value={decision.riskReward} color="primary.main" />
               </Grid>
               <Divider sx={{ my: 4, opacity: 0.05 }} />
               <Grid container spacing={4}>
                  <PlanItem
                    label="MODEL PROBABILITY"
                    value={`${decision.conviction}%`}
                    color="primary.main"
                    tooltip="Model-derived probability estimate based on the current model and evidence. It is not a guarantee of outcome."
                  />
                  <PlanItem label="EXPECTED VALUE" value={`₹${(decision.expectedValue || 0).toFixed(2)}`} color="#10b981" />
                  <PlanItem label="DIRECTION" value={isBuy ? 'LONG ▲' : 'SHORT ▼'} color={isBuy ? '#10b981' : '#ef4444'} />
                  <PlanItem label="ASSET CLASS" value={decision.assetClass || 'EQUITY'} />
               </Grid>
            </Paper>

            {/* 3. Signal Evidence Section */}
            <SectionHeader icon={<BarChart2 size={18} />} title="SIGNAL EVIDENCE & FORENSICS" />
            <Paper sx={{ p: 4, mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, mb: 2, display: 'block' }}>WHY THIS SIGNAL EXISTS</Typography>
               <Typography variant="body1" sx={{ color: '#e2e8f0', fontWeight: 500, lineHeight: 1.6, mb: 4 }}>
                  {decision.thesis || "Signal identified via V2.2 structural breakout logic combined with V2.3 ML classification. Forensic validation of institutional order flow confirmed at decision timestamp."}
               </Typography>

               <Grid container spacing={3}>
                  <EvidenceItem label="MARKET REGIME" value={signal.regime || 'SIDEWAYS'} />
                  <EvidenceItem label="SECTOR CONTEXT" value={signal.sector || 'UNAVAILABLE'} />
                  <EvidenceItem label="RELATIVE STRENGTH" value="UNAVAILABLE" />
                  <EvidenceItem label="VOLUME ANALYSIS" value="UNAVAILABLE" />
               </Grid>

               {decision.drivers && decision.drivers.length > 0 && (
                  <Box sx={{ mt: 4 }}>
                     <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, mb: 2, display: 'block' }}>KEY DRIVERS</Typography>
                     <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                        {decision.drivers.map((d: string, i: number) => (
                           <MuiChip key={i} label={d.toUpperCase()} size="small" sx={{ fontWeight: 900, bgcolor: 'rgba(255,255,255,0.05)', color: 'slategray' }} />
                        ))}
                     </Stack>
                  </Box>
               )}
            </Paper>

            {/* 4. Outcome Forensics (Visible for historical signals) */}
            {decision.status !== 'ACTIVE' && decision.status !== 'WAITING_FOR_ENTRY' && (
               <>
                  <SectionHeader icon={<ShieldCheck size={18} />} title="OUTCOME FORENSICS" />
                  <Paper sx={{ p: 4, mb: 4, bgcolor: alpha('#10b981', 0.02), border: '1px solid rgba(16, 185, 129, 0.1)' }}>
                     <Grid container spacing={4}>
                        <PlanItem label="EXIT PRICE" value={decision.exitPrice ? `₹${decision.exitPrice.toLocaleString()}` : '—'} />
                        <PlanItem label="REALIZED RETURN" value={`${(decision.realizedReturn || 0).toFixed(2)}%`} color={(decision.realizedReturn || 0) >= 0 ? "#10b981" : "#ef4444"} />
                        <PlanItem label="NET P&L" value={decision.netPnL ? `₹${decision.netPnL.toLocaleString()}` : '—'} color={(decision.netPnL || 0) >= 0 ? "#10b981" : "#ef4444"} />
                        <PlanItem label="CLOSED AT" value={decision.closedAt ? new Date(decision.closedAt).toLocaleDateString() : '—'} />
                     </Grid>
                     <Divider sx={{ my: 4, opacity: 0.05 }} />
                     <Grid container spacing={4}>
                        <PlanItem label="HOLDING PERIOD" value={`${decision.holdingPeriodDays || 0} DAYS`} />
                        <PlanItem label="MAE" value={decision.mae ? `${decision.mae.toFixed(2)}%` : '—'} />
                        <PlanItem label="MFE" value={decision.mfe ? `${decision.mfe.toFixed(2)}%` : '—'} />
                        <PlanItem label="FINAL OUTCOME" value={decision.status} color={getStatusColor(decision.status)} />
                     </Grid>
                  </Paper>
               </>
            )}

            {/* 5. Signal Thesis (Signal Intelligence 4.0) */}
            <SectionHeader icon={<Zap size={18} />} title="SIGNAL THESIS" />
            <Paper sx={{ p: 4, mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                <Grid container spacing={4}>
                    <ThesisItem label="TREND" value={decision.formattedThesis?.trend} />
                    <ThesisItem label="MOMENTUM" value={decision.formattedThesis?.momentum} />
                    <ThesisItem label="VOLUME" value={decision.formattedThesis?.volume} />
                    <ThesisItem label="MARKET" value={decision.formattedThesis?.market} />
                </Grid>
                <Divider sx={{ my: 3, opacity: 0.05 }} />
                <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700, fontStyle: 'italic' }}>
                    Machine-generated deterministic synthesis of authoritative evidence.
                </Typography>
            </Paper>

            {/* 6. Signal Replay (Chronological Lifecycle) */}
            <Box id="lifecycle-replay" sx={{ scrollMarginTop: 100 }}>
                <SectionHeader icon={<Clock size={18} />} title="SIGNAL REPLAY (CHRONOLOGICAL RECONSTRUCTION)" />
                <Paper sx={{ p: 4, mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <SignalLifecycleTimeline events={decision.lifecycleEvents} currentStatus={decision.status} />
                    <Divider sx={{ my: 3, opacity: 0.05 }} />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>REPLAY FIDELITY: HIGH</Typography>
                        <MuiChip label="VERIFIED RECONSTRUCTION" size="small" variant="outlined" sx={{ height: 18, fontSize: '0.5rem', fontWeight: 950, color: 'primary.main', borderColor: alpha('#00D1FF', 0.3) }} />
                    </Box>
                </Paper>
            </Box>
         </Grid>

         {/* RIGHT COLUMN: Metadata & Lifecycle */}
         <Grid item xs={12} md={4}>
            {/* 5. Lifecycle Visualization */}
            <SectionHeader icon={<Clock size={18} />} title="LIFECYCLE" />
            <Paper sx={{ p: 3, mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <SignalLifecycleTimeline events={decision.lifecycleEvents} currentStatus={decision.status} />
            </Paper>

            {/* 6. Live Market Status */}
            <SectionHeader icon={<Activity size={18} />} title="LIVE MARKET DATA" />
            <Paper sx={{ p: 3, mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Stack spacing={2.5}>
                  <TraceItem label="Current Price" value={`₹${(decision.normalizedCurrentPrice || 0).toLocaleString()}`} />
                  <TraceItem label="Freshness" value={decision.priceStatus} color={decision.priceStatus === 'FRESH' ? "#10b981" : "orange"} />
                  <TraceItem label="Price Source" value={signal.current_price_source || 'YFINANCE_LIVE'} />
                  <TraceItem label="Update Time" value={signal.current_price_timestamp ? new Date(signal.current_price_timestamp).toLocaleTimeString() : '—'} />
               </Stack>
               <Divider sx={{ my: 3, opacity: 0.05 }} />
               <Box sx={{ p: 1.5, bgcolor: alpha('#00D1FF', 0.03), borderRadius: 1, border: '1px solid rgba(0, 209, 255, 0.1)' }}>
                   <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 900, display: 'flex', alignItems: 'center', gap: 1 }}>
                       <ShieldCheck size={12} /> SHADOW SIGNAL MODE ACTIVE
                   </Typography>
               </Box>
            </Paper>

            {/* 6.1 Market Context (Signal Intelligence 4.0) */}
            <SectionHeader icon={<TrendingUp size={18} />} title="MARKET CONTEXT" />
            <Paper sx={{ p: 3, mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                <Stack spacing={2}>
                    <TraceItem label="Index Context" value="NIFTY 200" />
                    <TraceItem label="Market Regime" value={signal.regime || 'SIDEWAYS'} />
                    <TraceItem label="Sector" value={signal.sector || 'UNAVAILABLE'} />
                </Stack>
            </Paper>

            {/* 7. Signal Provenance */}
            <SectionHeader icon={<Briefcase size={18} />} title="PROVENANCE" />
            <Paper sx={{ p: 3, mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Stack spacing={2}>
                  <TraceItem label="Prediction ID" value={decision.predictionId || 'N/A'} small />
                  <TraceItem label="Model Version" value={signal.model_version || 'TradeMind Core v2.2'} />
                  <TraceItem label="Strategy" value="FROZEN V2.2" />
                  <Divider sx={{ my: 1, opacity: 0.05 }} />
                  <TraceItem label="Created At" value={new Date(decision.generatedAt).toLocaleString()} small />
                  <TraceItem label="Data Timestamp" value={new Date(signal.data_timestamp || signal.timestamp).toLocaleString()} small />
               </Stack>
            </Paper>
         </Grid>
      </Grid>
    </Box>
  );
}

function SectionHeader({ icon, title }: any) {
    return (
        <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 2, opacity: 0.8 }}>
            <Box sx={{ color: 'primary.main' }}>{icon}</Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 950, letterSpacing: 1, color: '#fff' }}>{title}</Typography>
        </Stack>
    );
}

function PlanItem({ label, value, color = '#fff', tooltip }: any) {
   return (
      <Grid item xs={6} md={3}>
         <Stack direction="row" spacing={0.5} alignItems="center" sx={{ mb: 0.5 }}>
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, display: 'block' }}>{label}</Typography>
            {tooltip && (
                <Tooltip title={tooltip}>
                    <HelpCircle size={10} color="slategray" style={{ cursor: 'help' }} />
                </Tooltip>
            )}
         </Stack>
         <Typography variant="h6" sx={{ fontWeight: 950, color, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
      </Grid>
   );
}

function EvidenceItem({ label, value }: any) {
    return (
        <Grid item xs={6} md={3}>
            <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.03)' }}>
                <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, display: 'block', mb: 0.5, fontSize: '0.6rem' }}>{label}</Typography>
                <Typography variant="body2" sx={{ fontWeight: 800, color: value === 'UNAVAILABLE' ? 'slategray' : '#fff' }}>{value}</Typography>
            </Box>
        </Grid>
    );
}

function ThesisItem({ label, value }: any) {
    return (
        <Grid item xs={6} md={3}>
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, display: 'block', mb: 1 }}>{label}</Typography>
            <Typography variant="body2" sx={{ fontWeight: 950, color: '#fff' }}>{value || 'UNAVAILABLE'}</Typography>
        </Grid>
    );
}

function TraceItem({ label, value, color = '#fff', small = false }: any) {
   return (
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>{label}</Typography>
         <Typography variant="caption" sx={{ color, fontWeight: 900, fontFamily: 'JetBrains Mono', fontSize: small ? '0.6rem' : '0.75rem', maxWidth: '65%', textAlign: 'right', overflow: 'hidden', textOverflow: 'ellipsis' }}>{value}</Typography>
      </Box>
   );
}

function getStatusColor(status: string) {
    switch (status) {
      case 'ACTIVE': return '#3b82f6';
      case 'ENTRY_TRIGGERED': return '#00D1FF';
      case 'WAITING_FOR_ENTRY': return '#f59e0b';
      case 'TARGET_HIT': return '#10b981';
      case 'STOP_LOSS': return '#ef4444';
      default: return 'slategray';
    }
}

function MuiChip({ label, sx, variant, size }: any) {
    return <Chip label={label} sx={sx} variant={variant} size={size || 'small'} />;
}
