import { useState } from 'react';
import { Box, Typography, Paper, Grid, Slider, Chip, Divider } from '@mui/material';
import { Play, TrendingUp, TrendingDown } from 'lucide-react';

export default function DecisionSimulator({ stock }: { stock: any }) {
  const [positionSize, setPositionSize] = useState(10);
  const [holdingDays, setHoldingDays] = useState(30);

  const calculateReturn = () => {
     // RC-3: Simulation logic based on AI structured consensus
     const structured = stock.structured_consensus || {};
     const rating = structured.rating || 'HOLD';

     let bias = 0;
     if (rating === 'STRONG BUY') bias = 1.8;
     else if (rating === 'BUY') bias = 1.2;
     else if (rating === 'STRONG SELL') bias = -1.5;
     else if (rating === 'SELL') bias = -0.8;
     else bias = 0.2; // Baseline drift

     const vol = stock.beta || 1.0;
     const projected = (bias * vol * (holdingDays / 365)) * 100;
     return projected;
  };

  const projectedReturn = calculateReturn();

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Play size={20} className="text-emerald-500" /> Decision Simulator
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>INPUT PARAMETERS</Typography>
            <Box sx={{ mt: 3 }}>
               <Typography variant="caption">Portfolio Weight: {positionSize}%</Typography>
               <Slider value={positionSize} onChange={(_, v) => setPositionSize(v as number)} min={1} max={100} size="small" />
            </Box>
            <Box sx={{ mt: 2 }}>
               <Typography variant="caption">Holding Horizon: {holdingDays} Days</Typography>
               <Slider value={holdingDays} onChange={(_, v) => setHoldingDays(v as number)} min={1} max={365} size="small" />
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, bgcolor: 'rgba(16, 185, 129, 0.05)', border: '1px solid #10b981' }}>
             <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                   <Typography variant="subtitle2" color="primary">SIMULATED OUTCOME</Typography>
                   <Typography variant="h4" fontWeight="bold" sx={{ my: 1 }}>
                      {projectedReturn >= 0 ? '+' : ''}{projectedReturn.toFixed(2)}%
                   </Typography>
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                   <Typography variant="caption" color="textSecondary">Projected Value</Typography>
                   <Typography variant="h6">₹{(stock.last_price * (1 + projectedReturn/100)).toLocaleString()}</Typography>
                </Box>
             </Box>

             <Divider sx={{ my: 2, opacity: 0.1 }} />

             <Box sx={{ display: 'flex', gap: 2 }}>
                <Chip icon={<TrendingUp size={14} />} label="Quality Momentum" size="small" variant="outlined" />
                <Chip icon={<TrendingDown size={14} />} label="Hedge Required" size="small" variant="outlined" />
             </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
