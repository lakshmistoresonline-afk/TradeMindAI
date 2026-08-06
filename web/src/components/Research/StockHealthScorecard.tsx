import { Box, Typography, Paper, Grid } from '@mui/material';
import { CheckCircle2, AlertCircle } from 'lucide-react';

export default function StockHealthScorecard({ metrics }: any) {
  if (!metrics) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'EXCELLENT': return '#10b981';
      case 'GOOD':
      case 'STABLE':
      case 'STRONG':
      case 'HIGH': return '#34d399';
      case 'WEAK': return '#f43f5e';
      default: return '#94a3b8';
    }
  };

  return (
    <Paper sx={{ p: 3, height: '100%' }}>
      <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ fontWeight: 'bold' }}>STOCK HEALTH AUDIT</Typography>

      <Grid container spacing={2} sx={{ mt: 1 }}>
        {Object.entries(metrics).map(([key, val]: [string, any]) => (
          <Grid item xs={6} key={key}>
            <Box sx={{ p: 1.5, border: '1px solid #334155', borderRadius: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
               <Box sx={{ width: 8, height: 8, bgcolor: getStatusColor(val), borderRadius: '50%' }} />
               <Box>
                  <Typography variant="caption" color="textSecondary" sx={{ display: 'block', lineHeight: 1 }}>{key}</Typography>
                  <Typography variant="body2" fontWeight="bold">{val}</Typography>
               </Box>
            </Box>
          </Grid>
        ))}
        <Grid item xs={6}>
            <Box sx={{ p: 1.5, border: '1px solid #334155', borderRadius: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
               <CheckCircle2 size={14} className="text-emerald-500" />
               <Box>
                  <Typography variant="caption" color="textSecondary" sx={{ display: 'block', lineHeight: 1 }}>Governance</Typography>
                  <Typography variant="body2" fontWeight="bold">PRISTINE</Typography>
               </Box>
            </Box>
        </Grid>
        <Grid item xs={6}>
            <Box sx={{ p: 1.5, border: '1px solid #334155', borderRadius: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
               <AlertCircle size={14} className={metrics?.Valuation === 'EXPENSIVE' ? "text-amber-500" : "text-emerald-500"} />
               <Box>
                  <Typography variant="caption" color="textSecondary" sx={{ display: 'block', lineHeight: 1 }}>Valuation</Typography>
                  <Typography variant="body2" fontWeight="bold">{metrics?.Valuation || 'STABLE'}</Typography>
               </Box>
            </Box>
        </Grid>
      </Grid>
    </Paper>
  );
}
