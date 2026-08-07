import { Box, Typography, Paper, Grid } from '@mui/material';

export default function StockHealthScorecard({ metrics }: any) {
  if (!metrics) return null;

  return (
    <Paper sx={{ p: 2.5, height: '100%', border: '1px solid #1e293b' }}>
      <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 2 }}>ASSET HEALTH DNA</Typography>

      <Grid container spacing={1.5}>
        <HealthMetric label="Technical" value={metrics?.Technical || 'STABLE'} color={metrics?.Technical === 'WEAK' ? 'error' : 'primary'} />
        <HealthMetric label="Financial" value={metrics?.Financial || 'STABLE'} color="primary" />
        <HealthMetric label="Growth" value={metrics?.Growth || 'HIGH'} color="primary" />
        <HealthMetric label="Valuation" value={metrics?.Valuation || 'STABLE'} color={metrics?.Valuation === 'EXPENSIVE' ? 'warning' : 'primary'} />
      </Grid>

      <Box sx={{ mt: 2.5, p: 1.5, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.05)' }}>
         <Typography variant="caption" color="textSecondary" display="block">HEALTH SUMMARY</Typography>
         <Typography variant="caption" sx={{ fontWeight: 600 }}>Asset shows strong institutional backing with stable fundamental health.</Typography>
      </Box>
    </Paper>
  );
}

function HealthMetric({ label, value, color }: any) {
  return (
    <Grid item xs={6}>
       <Box sx={{ p: 1, border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1 }}>
          <Typography variant="caption" color="textSecondary" display="block">{label}</Typography>
          <Typography variant="body2" fontWeight={800} color={`${color}.main`}>{value}</Typography>
       </Box>
    </Grid>
  );
}
