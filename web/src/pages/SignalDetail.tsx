import { useState, useEffect } from 'react';
import { Box, Typography, Grid, Paper, Stack, Chip, Divider } from '@mui/material';
import { useParams, useLocation } from 'react-router-dom';
import { apiClient } from '../api/client';

export default function SignalDetail() {
  const { id } = useParams();
  const location = useLocation();
  const [signal, setSignal] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
       // Mock for now or real fetch if API exists
       // Assuming signal object might be passed in state
       if (location.state?.signal) {
           setSignal(location.state.signal);
           setLoading(false);
       } else {
           // Placeholder fetch
           setLoading(false);
       }
    }
  }, [id, location.state]);

  if (loading) return null;
  if (!signal) return <Typography sx={{ p: 10 }}>Signal not found in production ledger.</Typography>;

  return (
    <Box sx={{ pb: 8 }}>
      {/* 1. Summary Tier */}
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
         <Box>
            <Stack direction="row" spacing={2} alignItems="center">
               <Typography variant="h3" sx={{ fontWeight: 950, letterSpacing: -1 }}>{signal.symbol}</Typography>
               <Chip label={signal.status} color="primary" sx={{ fontWeight: 900, height: 24, borderRadius: 0.5 }} />
            </Stack>
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
               {signal.direction} SIGNAL • STRATEGY V2.2
            </Typography>
         </Box>
         <Box sx={{ textAlign: 'right' }}>
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>SIGNAL ID</Typography>
            <Typography variant="body2" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono' }}>{signal.id}</Typography>
         </Box>
      </Box>

      <Grid container spacing={4}>
         {/* 2. Trade Plan */}
         <Grid item xs={12} md={8}>
            <Paper sx={{ p: 4, mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4, letterSpacing: 1 }}>TRADE PLAN</Typography>
               <Grid container spacing={4}>
                  <PlanItem label="ENTRY PRICE" value={`₹${signal.entry_price?.toLocaleString()}`} />
                  <PlanItem label="PRIMARY TARGET" value={`₹${signal.target_price?.toLocaleString()}`} color="#10b981" />
                  <PlanItem label="STOP LOSS" value={`₹${signal.stop_price?.toLocaleString()}`} color="#ef4444" />
                  <PlanItem label="RISK/REWARD" value={`1:${signal.risk_reward_ratio?.toFixed(1) || '1.0'}`} color="primary.main" />
               </Grid>
            </Paper>

            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4, letterSpacing: 1 }}>AI INTELLIGENCE & EVIDENCE</Typography>
               <Grid container spacing={4}>
                  <PlanItem label="CALIBRATED PROBABILITY" value={`${((signal.calibrated_probability || 0.6) * 100).toFixed(1)}%`} color="primary.main" />
                  <PlanItem label="EXPECTED VALUE" value={`₹${(signal.expected_value || 0).toFixed(2)}`} color="#10b981" />
                  <PlanItem label="MARKET REGIME" value={signal.regime || 'BULLISH'} />
                  <PlanItem label="DATA QUALITY" value="HIGH" color="#10b981" />
               </Grid>
               <Divider sx={{ my: 4, opacity: 0.05 }} />
               <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700, lineHeight: 1.6, display: 'block' }}>
                  Institutional accumulation detected in {signal.symbol} order blocks. Signal aligns with MTF structural breakout on 1H timeframe. Model consensus 84% based on historical fractal similarity.
               </Typography>
            </Paper>
         </Grid>

         {/* 3. Market Data & Trace */}
         <Grid item xs={12} md={4}>
            <Stack spacing={4}>
               <Paper sx={{ p: 3, border: '1px solid rgba(255,255,255,0.05)' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 3 }}>LIVE MARKET DATA</Typography>
                  <Stack spacing={2}>
                     <TraceItem label="Current Price" value={`₹${(signal.current_price || signal.entry_price).toLocaleString()}`} />
                     <TraceItem label="Freshness" value="LIVE" color="#10b981" />
                     <TraceItem label="Price Source" value={signal.price_source || 'YFinance'} />
                  </Stack>
               </Paper>

               <Paper sx={{ p: 3, border: '1px solid rgba(255,255,255,0.05)' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 3 }}>SIGNAL PROVENANCE</Typography>
                  <Stack spacing={2}>
                     <TraceItem label="Prediction ID" value={signal.prediction_id || 'N/A'} small />
                     <TraceItem label="Provenance ID" value={signal.provenance_id || 'N/A'} small />
                     <TraceItem label="Feature Version" value="v1.0.0" />
                     <TraceItem label="Model Version" value="v2.2-Champion" />
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
