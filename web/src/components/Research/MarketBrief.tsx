import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Chip, Stack, Divider, Grid, CircularProgress } from '@mui/material';
import { Zap } from 'lucide-react';
import { getMarketRegime } from '../../api/client';

export default function MarketBrief() {
  const [regime, setRegime] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMarketRegime().then(setRegime).finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress size={20} />;

  return (
    <Box sx={{ mb: 4 }}>
      <Paper sx={{ p: 3, border: '1px solid #10b981', bgcolor: 'rgba(16, 185, 129, 0.05)' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
           <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Zap size={20} className="text-emerald-500" />
              <Typography variant="h6" fontWeight="bold">AI Daily Intelligence</Typography>
           </Box>
           <Chip label="Vision 2.0 Active" size="small" color="primary" sx={{ fontWeight: 'bold' }} />
        </Box>

        <Grid container spacing={3}>
           <Grid item xs={12} md={12}>
              <Box sx={{ p: 2, bgcolor: 'rgba(15, 23, 42, 0.5)', borderRadius: 2 }}>
                 <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" fontWeight="bold" color="primary">MARKET REGIME</Typography>
                 </Box>
                 <Typography variant="subtitle1" fontWeight="bold" gutterBottom>{regime?.regime || 'SIDEWAYS'}</Typography>
                 <Typography variant="body2" color="textSecondary" sx={{ lineHeight: 1.6 }}>{regime?.description || 'Loading market behavior...'}</Typography>
              </Box>
           </Grid>
        </Grid>

        <Divider sx={{ my: 3, opacity: 0.1 }} />

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
           <MarketRegimeTag label="Regime" value={regime?.regime} color="#10b981" />
           <MarketRegimeTag label="Risk Mode" value={regime?.risk_mode} color="#3b82f6" />
           <MarketRegimeTag label="VIX" value={regime?.volatility_index} color="#94a3b8" />
        </Box>
      </Paper>
    </Box>
  );
}

function MarketRegimeTag({ label, value, color }: any) {
  return (
    <Box>
       <Typography variant="caption" color="textSecondary" display="block">{label}</Typography>
       <Typography variant="subtitle2" fontWeight="bold" sx={{ color }}>{value || '---'}</Typography>
    </Box>
  );
}
