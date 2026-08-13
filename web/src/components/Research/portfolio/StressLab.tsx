import { Box, Typography, Paper, Slider, Grid, Stack, Chip, Divider } from '@mui/material';
import { AlertCircle } from 'lucide-react';
import { useState } from 'react';

export default function StressLab() {
  const [marketDrop, setMarketDrop] = useState(-5);
  const portfolioBeta = 1.14;
  const portfolioValue = 4280000;

  const estimatedImpact = (marketDrop / 100) * portfolioBeta * 100;
  const estimatedLoss = (portfolioValue * estimatedImpact) / 100;

  return (
    <Paper sx={{ p: 3, border: '1px solid #1e293b', bgcolor: 'rgba(244, 63, 94, 0.02)' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
         <Stack direction="row" spacing={1} alignItems="center">
            <AlertCircle size={20} className="text-rose-500" />
            <Typography variant="subtitle2" fontWeight={900}>RISK STRESS LAB</Typography>
         </Stack>
         <Chip label="MONTE CARLO SIMULATION" size="small" variant="outlined" sx={{ fontWeight: 900, height: 20, fontSize: '0.55rem' }} />
      </Box>

      <Box sx={{ px: 2, mb: 5 }}>
         <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, mb: 3, display: 'block' }}>SIMULATE MARKET CRASH (%)</Typography>
         <Slider
            value={marketDrop}
            min={-20}
            max={0}
            step={1}
            onChange={(_, v) => setMarketDrop(v as number)}
            valueLabelDisplay="on"
            color="error"
         />
      </Box>

      <Grid container spacing={3}>
         <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1.5, border: '1px solid #1e293b' }}>
               <Typography variant="caption" color="textSecondary" fontWeight={800}>ESTIMATED DRAWDOWN</Typography>
               <Typography variant="h4" sx={{ fontWeight: 900, color: '#f43f5e', fontFamily: 'JetBrains Mono', mt: 0.5 }}>
                  {estimatedImpact.toFixed(1)}%
               </Typography>
               <Typography variant="caption" color="textSecondary">Beta Multiplier Active</Typography>
            </Box>
         </Grid>
         <Grid item xs={12} md={6}>
            <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1.5, border: '1px solid #1e293b' }}>
               <Typography variant="caption" color="textSecondary" fontWeight={800}>POTENTIAL VALUE AT RISK (VaR)</Typography>
               <Typography variant="h4" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', mt: 0.5 }}>
                  ₹{Math.abs(Math.round(estimatedLoss)).toLocaleString()}
               </Typography>
               <Typography variant="caption" color="textSecondary">Portfolio Loss Estimate</Typography>
            </Box>
         </Grid>
      </Grid>

      <Divider sx={{ my: 3, opacity: 0.05 }} />

      <Box sx={{ p: 2, bgcolor: 'rgba(244, 63, 94, 0.05)', borderRadius: 1.5, border: '1px dashed #f43f5e' }}>
         <Typography variant="caption" color="error" fontWeight={900} display="block" gutterBottom>STRESS TEST VERDICT</Typography>
         <Typography variant="body2" sx={{ fontWeight: 500 }}>
            In a {Math.abs(marketDrop)}% market correction, your portfolio is expected to underperform the benchmark by **{(portfolioBeta - 1) * 100}%** due to high-beta tech concentration.
         </Typography>
      </Box>
    </Paper>
  );
}
