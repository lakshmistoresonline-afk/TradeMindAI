import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Chip, Stack, Divider, Grid, CircularProgress } from '@mui/material';
import { Zap } from 'lucide-react';
import { getMarketRegime } from '../../api/client';

export default function MarketBrief() {
  const [regime, setRegime] = useState<any>(null);
  const [intel, setIntel] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getMarketRegime(), getMarketIntelligence('CLOSING')])
      .then(([regimeData, intelData]) => {
        setRegime(regimeData);
        setIntel(intelData);
      })
      .finally(() => setLoading(false));
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
           <Chip label={intel?.type || "MARKET_LIVE"} size="small" color="primary" sx={{ fontWeight: 'bold' }} />
        </Box>

        <Grid container spacing={3}>
           <Grid item xs={12} md={8}>
              <Box sx={{ p: 2, bgcolor: 'rgba(15, 23, 42, 0.5)', borderRadius: 2, height: '100%' }}>
                 <Typography variant="subtitle1" fontWeight="bold" gutterBottom>{intel?.summary || "AI Analysis pending for latest session..."}</Typography>
                 <Typography variant="body2" color="textSecondary" sx={{ lineHeight: 1.6 }}>{regime?.description}</Typography>
              </Box>
           </Grid>
           <Grid item xs={12} md={4}>
              <Box sx={{ p: 2, bgcolor: 'rgba(15, 23, 42, 0.5)', borderRadius: 2, height: '100%' }}>
                 <Typography variant="caption" fontWeight="bold" color="primary">KEY EVENTS</Typography>
                 <List dense>
                    {intel?.key_events?.map((e: string) => (
                      <ListItem key={e} sx={{ p: 0 }}><ListItemText primary={e} primaryTypographyProps={{ variant: 'caption' }} /></ListItem>
                    ))}
                 </List>
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
