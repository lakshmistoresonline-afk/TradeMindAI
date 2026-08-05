import { Box, Typography, Paper, Grid, Chip, Divider } from '@mui/material';
import { Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function MultiTimeframeAnalysis({ mtf_data }: { mtf_data?: any }) {
  if (!mtf_data) {
     return (
        <Box sx={{ mb: 4 }}>
           <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Clock size={20} className="text-emerald-500" /> Multi-Timeframe Alignment
           </Typography>
           <Paper sx={{ p: 4, textAlign: 'center' }}><Typography color="textSecondary">No timeframe data available. Trigger analysis to generate.</Typography></Paper>
        </Box>
     );
  }

  const timeframes = [
    { tf: '1 HOUR', bias: mtf_data.timeframes['1H']?.bias, score: mtf_data.timeframes['1H']?.score, icon: mtf_data.timeframes['1H']?.bias === 'BULLISH' ? <TrendingUp size={14} /> : <TrendingDown size={14} /> },
    { tf: 'DAILY', bias: mtf_data.timeframes['1D']?.bias, score: mtf_data.timeframes['1D']?.score, icon: mtf_data.timeframes['1D']?.bias === 'BULLISH' ? <TrendingUp size={14} /> : <TrendingDown size={14} /> },
    { tf: 'WEEKLY', bias: mtf_data.timeframes['1W']?.bias, score: mtf_data.timeframes['1W']?.score, icon: mtf_data.timeframes['1W']?.bias === 'BULLISH' ? <TrendingUp size={14} /> : <TrendingDown size={14} /> },
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Clock size={20} className="text-emerald-500" /> Multi-Timeframe Alignment
      </Typography>

      <Paper sx={{ p: 3 }}>
         <Grid container spacing={2}>
            {timeframes.map((item) => (
              <Grid item xs={12} sm={4} key={item.tf}>
                 <Box sx={{ textAlign: 'center', p: 2, border: '1px solid #334155', borderRadius: 2 }}>
                    <Typography variant="caption" color="textSecondary" fontWeight="bold">{item.tf}</Typography>
                    <Box sx={{ my: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 0.5, color: item.bias === 'BULLISH' ? '#10b981' : item.bias === 'BEARISH' ? '#f43f5e' : '#94a3b8' }}>
                       {item.icon}
                       <Typography variant="subtitle2" fontWeight="bold">{item.bias}</Typography>
                    </Box>
                    <Typography variant="h6" fontWeight="bold">{Math.round(item.score)}</Typography>
                 </Box>
              </Grid>
            ))}
         </Grid>

         <Box sx={{ mt: 3, p: 2, bgcolor: 'rgba(16, 185, 129, 0.05)', borderRadius: 2, borderLeft: '4px solid #10b981' }}>
            <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
               {mtf_data.summary} Alignment: **{mtf_data.alignment_status}**.
            </Typography>
         </Box>
      </Paper>
    </Box>
  );
}
