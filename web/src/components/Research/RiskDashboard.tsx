import { Box, Typography, Paper, Grid, Chip, LinearProgress } from '@mui/material';
import { ShieldAlert, AlertTriangle, Zap, Activity } from 'lucide-react';

export default function RiskDashboard({ stock }: { stock: any }) {
  const risks = [
    { label: 'Market Risk', score: 65, level: 'MEDIUM', desc: 'Sensitivity to broader Nifty 100 volatility.' },
    { label: 'Company Risk', score: 25, level: 'LOW', desc: 'Financial stability and management quality.' },
    { label: 'Liquidity Risk', score: 15, level: 'LOW', desc: 'Ease of entry/exit without price impact.' },
    { label: 'Volatility Risk', score: 72, level: 'HIGH', desc: 'Expected daily price swings based on Beta.' },
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <ShieldAlert size={20} className="text-rose-500" /> Enterprise Risk Dashboard
      </Typography>

      <Grid container spacing={3}>
        {risks.map((risk) => (
          <Grid item xs={12} sm={6} md={3} key={risk.label}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle2" fontWeight="bold">{risk.label}</Typography>
                <Chip
                  label={risk.level}
                  size="small"
                  sx={{
                    bgcolor: risk.level === 'HIGH' ? 'rgba(244, 63, 94, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                    color: risk.level === 'HIGH' ? '#f43f5e' : '#10b981',
                    fontSize: '0.6rem', fontWeight: 'bold'
                  }}
                />
              </Box>
              <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mb: 2, height: 40 }}>
                {risk.desc}
              </Typography>
              <Box sx={{ mt: 'auto' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                   <Typography variant="caption">Risk Probability</Typography>
                   <Typography variant="caption" fontWeight="bold">{risk.score}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={risk.score}
                  color={risk.score > 70 ? 'error' : risk.score > 40 ? 'warning' : 'primary'}
                  sx={{ height: 6, borderRadius: 2 }}
                />
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
