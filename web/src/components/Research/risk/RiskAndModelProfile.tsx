import { Box, Typography, Paper, Grid, LinearProgress, Stack } from '@mui/material';
import { Shield, Cpu } from 'lucide-react';

export default function RiskAndModelProfile() {
  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Shield size={20} className="text-blue-500" /> Risk & Model Profile
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom fontWeight={800}>RISK SIGNATURE</Typography>
            <Stack spacing={2.5} sx={{ mt: 2 }}>
               <ProfileMetric label="Volatility Regime" value="MEDIUM" />
               <ProfileMetric label="Systematic Beta" value="1.14" />
               <ProfileMetric label="Historical Drawdown" value="-12.4%" color="error.main" />
               <ProfileMetric label="Institutional Correlation" value="0.82" />
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom fontWeight={800}>AI MODEL CONFIDENCE</Typography>
            <Grid container spacing={4} sx={{ mt: 1 }}>
               <Grid item xs={12} sm={6}>
                  <Box sx={{ mb: 3 }}>
                     <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" fontWeight={700}>Forensic Alignment</Typography>
                        <Typography variant="body2" fontWeight={800} color="primary">85%</Typography>
                     </Box>
                     <LinearProgress variant="determinate" value={85} sx={{ height: 6, borderRadius: 3 }} />
                  </Box>
                  <Box>
                     <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" fontWeight={700}>Backtest Stability</Typography>
                        <Typography variant="body2" fontWeight={800} color="primary">92%</Typography>
                     </Box>
                     <LinearProgress variant="determinate" value={92} sx={{ height: 6, borderRadius: 3 }} />
                  </Box>
               </Grid>
               <Grid item xs={12} sm={6}>
                  <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, border: '1px solid #334155' }}>
                     <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 700 }}>
                        <Cpu size={14} /> INTELLIGENCE PROFILE
                     </Typography>
                     <Typography variant="body2" sx={{ mt: 1, fontWeight: 500 }}>
                        Model shows high confidence in current structural breakout. SMC and Trend indicators are in strong institutional coordination.
                     </Typography>
                  </Box>
               </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function ProfileMetric({ label, value, color }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
       <Typography variant="body2" color="textSecondary" fontWeight={600}>{label}</Typography>
       <Typography variant="body2" fontWeight={800} sx={{ color }}>{value}</Typography>
    </Box>
  );
}
