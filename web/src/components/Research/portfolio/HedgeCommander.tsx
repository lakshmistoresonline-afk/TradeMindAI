import { Box, Typography, Paper, Button, Stack, Chip, Divider, CircularProgress, Grid } from '@mui/material';
import { ShieldCheck, Zap } from 'lucide-react';
import { useState, useEffect } from 'react';
import { getPortfolioHedge } from '../../../api/client';

export default function HedgeCommander() {
  const [hedge, setHedge] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPortfolioHedge()
      .then(setHedge)
      .catch(err => console.error("Hedge Error:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Box sx={{ py: 4, textAlign: 'center' }}><CircularProgress size={24} /></Box>;

  return (
    <Paper sx={{ p: 3, border: '1px solid #1e293b', bgcolor: 'rgba(16, 185, 129, 0.02)' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
         <Stack direction="row" spacing={1} alignItems="center">
            <ShieldCheck size={20} className="text-emerald-500" />
            <Typography variant="subtitle2" fontWeight={900}>HEDGE COMMANDER</Typography>
         </Stack>
         <Chip label="DELTA MONITORING ACTIVE" size="small" sx={{ fontWeight: 900, height: 20, fontSize: '0.55rem', bgcolor: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }} />
      </Box>

      <Grid container spacing={3}>
         <Grid item xs={12} md={6}>
            <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>PORTFOLIO DELTA BIAS (BETA)</Typography>
            <Typography variant="h4" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', mt: 0.5 }}>
               {hedge?.portfolio_beta?.toFixed(2) || '1.14'}
            </Typography>
            <Typography variant="caption" sx={{ color: (hedge?.portfolio_beta > 1 ? '#f43f5e' : '#10b981'), fontWeight: 700 }}>
               {hedge?.portfolio_beta > 1 ? 'Aggressive Market Sensitivity' : 'Defensive Market Sensitivity'}
            </Typography>
         </Grid>
         <Grid item xs={12} md={6}>
            <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>TAIL-RISK PROTECTION</Typography>
            <Box sx={{ mt: 1 }}>
               {hedge?.recommendation !== "NONE" ? (
                  <Chip label="PROTECTION REQUIRED" color="error" size="small" sx={{ fontWeight: 900 }} />
               ) : (
                  <Chip label="BUFFER SUFFICIENT" color="primary" variant="outlined" size="small" sx={{ fontWeight: 900 }} />
               )}
            </Box>
         </Grid>
      </Grid>

      <Divider sx={{ my: 3, opacity: 0.05 }} />

      <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1.5, border: '1px dashed #334155' }}>
         <Typography variant="caption" color="primary" fontWeight={900} display="block" gutterBottom>AI HEDGING RECOMMENDATION</Typography>
         {hedge?.recommendation !== "NONE" ? (
            <Box>
               <Typography variant="body2" sx={{ fontWeight: 600, mb: 2 }}>
                  {hedge?.reasoning}
               </Typography>
               <Stack direction="row" spacing={2}>
                  <Box sx={{ flex: 1, p: 1.5, bgcolor: '#0f172a', borderRadius: 1, border: '1px solid #1e293b' }}>
                     <Typography variant="caption" color="textSecondary">INSTRUMENT</Typography>
                     <Typography variant="body2" fontWeight={800}>{hedge?.hedge_asset} Puts</Typography>
                  </Box>
                  <Box sx={{ flex: 1, p: 1.5, bgcolor: '#0f172a', borderRadius: 1, border: '1px solid #1e293b' }}>
                     <Typography variant="caption" color="textSecondary">SUGGESTED QUANTITY</Typography>
                     <Typography variant="body2" fontWeight={800}>{hedge?.suggested_lots} Lots</Typography>
                  </Box>
               </Stack>
               <Button
                  fullWidth
                  variant="contained"
                  startIcon={<Zap size={16} />}
                  sx={{ mt: 2, fontWeight: 900, bgcolor: 'primary.main', color: 'black' }}
               >
                  ONE-CLICK HEDGE EXECUTION
               </Button>
            </Box>
         ) : (
            <Typography variant="body2" sx={{ fontStyle: 'italic', opacity: 0.6 }}>
               No immediate delta-neutral adjustments required for current volatility regime.
            </Typography>
         )}
      </Box>
    </Paper>
  );
}
