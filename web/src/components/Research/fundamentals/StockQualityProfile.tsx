import { Box, Typography, Paper, Grid } from '@mui/material';

export default function StockQualityProfile({ metrics }: any) {
  if (!metrics) return null;

  return (
    <Paper sx={{ p: 2.5, height: '100%', border: '1px solid #1e293b' }}>
      <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 2, fontWeight: 800 }}>STOCK QUALITY PROFILE</Typography>

      <Grid container spacing={1.5}>
        <QualityMetric label="Technical Quality" value={metrics?.Technical || 'STABLE'} color={metrics?.Technical === 'WEAK' ? 'error' : 'primary'} />
        <QualityMetric label="Fundamental Quality" value={metrics?.Financial || 'STABLE'} color="primary" />
        <QualityMetric label="Growth Quality" value={metrics?.Growth || 'HIGH'} color="primary" />
        <QualityMetric label="Valuation Quality" value={metrics?.Valuation || 'STABLE'} color={metrics?.Valuation === 'EXPENSIVE' ? 'warning' : 'primary'} />
      </Grid>

      <Box sx={{ mt: 2.5, p: 1.5, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.05)' }}>
         <Typography variant="caption" color="textSecondary" display="block" sx={{ fontWeight: 700 }}>QUALITY SUMMARY</Typography>
         <Typography variant="caption" sx={{ fontWeight: 600 }}>Asset shows stable institutional quality scores across core metrics.</Typography>
      </Box>
    </Paper>
  );
}

function QualityMetric({ label, value, color }: any) {
  return (
    <Grid item xs={6}>
       <Box sx={{ p: 1, border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1 }}>
          <Typography variant="caption" color="textSecondary" display="block" sx={{ fontWeight: 700, fontSize: '0.65rem' }}>{label.toUpperCase()}</Typography>
          <Typography variant="body2" fontWeight={800} color={`${color}.main`}>{value}</Typography>
       </Box>
    </Grid>
  );
}
