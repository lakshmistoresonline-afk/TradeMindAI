import { useState, useEffect } from 'react';
import { Box, Typography, Grid, Paper, Stack, Chip, Divider, Skeleton, alpha } from '@mui/material';
import { useParams, useLocation } from 'react-router-dom';
import { getEquitySignalDetail } from '../api/client';
import { mapCanonicalSignal } from '../hooks/useAITradeDecision';

export default function SignalDetail() {
  const { id } = useParams();
  const location = useLocation();
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
    }
  }, [id, location.state]);

  if (loading) return (
     <Box sx={{ p: 4 }}>
        <Skeleton variant="rectangular" height={100} sx={{ mb: 4 }} />
        <Grid container spacing={4}>
           <Grid item xs={12} md={8}><Skeleton variant="rectangular" height={400} /></Grid>
           <Grid item xs={12} md={4}><Skeleton variant="rectangular" height={400} /></Grid>
        </Grid>
     </Box>
  );

  if (!signal) return <Typography sx={{ p: 10 }}>Signal not found in production ledger.</Typography>;

  return (
    <Box sx={{ pb: 8 }}>
      {/* 1. Summary Tier */}
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
         <Box>
            <Stack direction="row" spacing={2} alignItems="center">
               <Typography variant="h3" sx={{ fontWeight: 950, letterSpacing: -1 }}>{signal.symbol}</Typography>
               <Chip label={signal.status} color="primary" sx={{ fontWeight: 900, height: 24, borderRadius: 0.5 }} />
               {signal.quality_class && (
                  <Chip
                    label={signal.quality_class}
                    variant="outlined"
                    sx={{
                      fontWeight: 950, height: 24, borderRadius: 0.5,
                      borderColor: signal.quality_class === 'PRIMARY' ? '#10b981' : signal.quality_class === 'SELECTIVE' ? '#00D1FF' : 'slategray',
                      color: signal.quality_class === 'PRIMARY' ? '#10b981' : signal.quality_class === 'SELECTIVE' ? '#00D1FF' : 'slategray'
                    }}
                  />
               )}
            </Stack>
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
               {signal.direction} {signal.decision.timeframe} SIGNAL • STRATEGY {signal.strategy_version}
            </Typography>
         </Box>
         <Box sx={{ textAlign: 'right' }}>
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>SIGNAL ID</Typography>
            <Typography variant="body2" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono' }}>{signal.id}</Typography>
            <Chip
                label={signal.decision.qualityClass}
                size="small"
                sx={{ mt: 1, fontWeight: 900, fontSize: '0.6rem' }}
            />
         </Box>
      </Box>

      <Grid container spacing={4}>
         {/* 2. Trade Plan */}
         <Grid item xs={12} md={8}>
            <Paper sx={{ p: 4, mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4, letterSpacing: 1 }}>TRADE PLAN</Typography>
               <Grid container spacing={4}>
                  <PlanItem label="ENTRY PRICE" value={`₹${signal.decision.entry?.toLocaleString()}`} />
                  <PlanItem label="PRIMARY TARGET" value={`₹${signal.decision.target?.toLocaleString()}`} color="#10b981" />
                  <PlanItem label="STOP LOSS" value={`₹${signal.decision.stopLoss?.toLocaleString()}`} color="#ef4444" />
                  <PlanItem label="RISK/REWARD" value={signal.decision.riskReward} color="primary.main" />
               </Grid>
            </Paper>

            <Paper sx={{ p: 4, mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4, letterSpacing: 1 }}>FORENSIC EVIDENCE & PROBABILITY</Typography>
               <Grid container spacing={4}>
                  <PlanItem label="MODEL PROBABILITY" value={`${signal.decision.conviction}%`} color="primary.main" />
                  <PlanItem label="EXPECTED VALUE" value={`₹${(signal.decision.expectedValue || 0).toFixed(2)}`} color="#10b981" />
                  <PlanItem label="MARKET REGIME" value={signal.regime || 'SIDEWAYS'} />
                  <PlanItem label="DATA STATUS" value={signal.decision.priceStatus} color={signal.decision.priceStatus === 'FRESH' ? "#10b981" : "orange"} />
               </Grid>
               <Divider sx={{ my: 4, opacity: 0.05 }} />
               <Box>
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, mb: 2, display: 'block' }}>WHY THIS SIGNAL EXISTS</Typography>
                  <Typography variant="body2" sx={{ color: 'slategray', fontWeight: 700, lineHeight: 1.6 }}>
                     {signal.provenance?.evidence || "Signal identified via V2.2 structural breakout logic combined with V2.3 ML classification. Forensic validation of institutional order flow confirmed at decision timestamp."}
                  </Typography>
               </Box>
            </Paper>

            {signal.decision.status !== 'ACTIVE' && signal.decision.status !== 'WAITING_FOR_ENTRY' && (
               <Paper sx={{ p: 4, bgcolor: alpha('#10b981', 0.02), border: '1px solid rgba(16, 185, 129, 0.1)' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4, letterSpacing: 1 }}>OUTCOME FORENSICS</Typography>
                  <Grid container spacing={4}>
                     <PlanItem label="EXIT PRICE" value={signal.decision.exitPrice ? `₹${signal.decision.exitPrice.toLocaleString()}` : '—'} />
                     <PlanItem label="REALIZED RETURN" value={`${(signal.decision.realizedReturn || 0).toFixed(2)}%`} color={(signal.decision.realizedReturn || 0) >= 0 ? "#10b981" : "#ef4444"} />
                     <PlanItem label="NET P&L" value={signal.decision.netPnL ? `₹${signal.decision.netPnL.toLocaleString()}` : '—'} color={(signal.decision.netPnL || 0) >= 0 ? "#10b981" : "#ef4444"} />
                     <PlanItem label="OUTCOME" value={signal.decision.status} />
                  </Grid>
               </Paper>
            )}
         </Grid>

         {/* 3. Market Data & Trace */}
         <Grid item xs={12} md={4}>
            <Stack spacing={4}>
               <Paper sx={{ p: 3, border: '1px solid rgba(255,255,255,0.05)' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 3 }}>LIVE MARKET DATA</Typography>
                  <Stack spacing={2}>
                     <TraceItem label="Current Price" value={`₹${(signal.decision.normalizedCurrentPrice || 0).toLocaleString()}`} />
                     <TraceItem label="Freshness" value={signal.decision.priceStatus} color={signal.decision.priceStatus === 'FRESH' ? "#10b981" : "slategray"} />
                     <TraceItem label="Price Source" value={signal.current_price_source || 'YFinance'} />
                     <TraceItem label="Price Timestamp" value={signal.current_price_timestamp ? new Date(signal.current_price_timestamp).toLocaleTimeString() : '—'} />
                  </Stack>
               </Paper>

               <Paper sx={{ p: 3, border: '1px solid rgba(255,255,255,0.05)' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 3 }}>SIGNAL METADATA</Typography>
                  <Stack spacing={2}>
                     <TraceItem label="Signal ID" value={signal.id} small />
                     <TraceItem label="Model Version" value={signal.model_version} />
                     <TraceItem label="Strategy" value="FROZEN V2.2" />
                     <Divider sx={{ my: 1, opacity: 0.05 }} />
                     <TraceItem label="Created At" value={new Date(signal.timestamp).toLocaleString()} small />
                     <TraceItem label="Data Timestamp" value={new Date(signal.data_timestamp).toLocaleString()} small />
                  </Stack>
               </Paper>
            </Stack>
         </Grid>
      </Grid>
    </Box>
  );
}

function PlanItem({ label, value, color = '#fff' }: any) {
   return (
      <Grid item xs={6} md={3}>
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, display: 'block', mb: 0.5 }}>{label}</Typography>
         <Typography variant="h6" sx={{ fontWeight: 950, color, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
      </Grid>
   );
}

function TraceItem({ label, value, color = '#fff', small = false }: any) {
   return (
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>{label}</Typography>
         <Typography variant="caption" sx={{ color, fontWeight: 900, fontFamily: 'JetBrains Mono', fontSize: small ? '0.6rem' : '0.75rem', maxWidth: '60%', textAlign: 'right', overflow: 'hidden', textOverflow: 'ellipsis' }}>{value}</Typography>
      </Box>
   );
}
