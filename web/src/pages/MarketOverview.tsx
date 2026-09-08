import { useState, useEffect } from 'react';
import { Box, Typography, Grid, Paper, Stack, alpha, Divider, LinearProgress } from '@mui/material';
import { Globe, TrendingUp } from 'lucide-react';
import { getMarketStats } from '../api/client';

export default function MarketOverview() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    getMarketStats().then(setStats);
  }, []);

  return (
    <Box sx={{ pb: 8 }}>
      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>MARKET INTELLIGENCE</Typography>
        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
           GLOBAL CONTEXT • NSE DOMESTIC NODES
        </Typography>
      </Box>

      <Grid container spacing={4}>
         {/* Regime Module */}
         <Grid item xs={12} md={4}>
            <Paper sx={{ p: 4, height: '100%', bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 4 }}>
                  <Globe size={20} color="primary.main" />
                  <Typography variant="subtitle2" sx={{ fontWeight: 900 }}>MARKET REGIME</Typography>
               </Stack>
               <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="h2" sx={{ fontWeight: 950, color: '#10b981' }}>{stats?.Regime || 'NEUTRAL'}</Typography>
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>V2.2 CONSENSUS ACTIVE</Typography>
               </Box>
               <Divider sx={{ my: 3, opacity: 0.05 }} />
               <Typography variant="caption" sx={{ color: 'slategray', display: 'block', mb: 2 }}>SUPPORTING METRICS</Typography>
               <Stack spacing={2}>
                  <RegimeMetric label="VIX Sentiment" value="LOW" />
                  <RegimeMetric label="Adv/Dec Ratio" value="1.42" />
               </Stack>
            </Paper>
         </Grid>

         {/* Sector Strength */}
         <Grid item xs={12} md={8}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 4 }}>
                  <TrendingUp size={20} color="#10b981" />
                  <Typography variant="subtitle2" sx={{ fontWeight: 900 }}>SECTOR RELATIVE STRENGTH</Typography>
               </Stack>
               <Grid container spacing={2}>
                  {['NIFTY IT', 'NIFTY BANK', 'NIFTY AUTO', 'NIFTY FMCG', 'NIFTY PHARMA', 'NIFTY METAL'].map((s, i) => (
                     <Grid item xs={12} sm={6} key={s}>
                        <Box sx={{ p: 2, bgcolor: alpha('#fff', 0.02), borderRadius: 1 }}>
                           <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900 }}>RANK #{i+1}</Typography>
                           <Typography sx={{ fontWeight: 900, mb: 1 }}>{s}</Typography>
                           <LinearProgress variant="determinate" value={90 - (i * 10)} sx={{ height: 4, borderRadius: 2 }} />
                        </Box>
                     </Grid>
                  ))}
               </Grid>
            </Paper>
         </Grid>
      </Grid>
    </Box>
  );
}

function RegimeMetric({ label, value }: any) {
   return (
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>{label}</Typography>
         <Typography variant="caption" sx={{ color: '#fff', fontWeight: 900 }}>{value}</Typography>
      </Box>
   );
}
