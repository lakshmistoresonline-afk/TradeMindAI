import { Box, Typography, Paper, Grid, Chip, Button, Divider } from '@mui/material';
import { Target, Zap, TrendingUp, Search, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function OpportunityEngine() {
  const navigate = useNavigate();
  const opportunities = [
    { symbol: 'RELIANCE', type: 'BREAKOUT', score: 88, thesis: 'Institutional accumulation complete. High probability momentum move detected.' },
    { symbol: 'HDFCBANK', type: 'UNDERVALUED', score: 72, thesis: 'Price reacting off major 1Y support with bullish RSI divergence.' },
    { symbol: 'INFY', type: 'REVERSAL', score: 65, thesis: 'Mean reversion pattern forming after overextended sell-off.' }
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Target size={20} className="text-emerald-500" /> AI Opportunity Engine
      </Typography>

      <Grid container spacing={3}>
         {opportunities.map((opp) => (
           <Grid item xs={12} md={4} key={opp.symbol}>
              <Paper sx={{ p: 3, height: '100%', border: '1px solid #334155', '&:hover': { borderColor: '#10b981' }, cursor: 'pointer', transition: 'all 0.2s' }}>
                 <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" fontWeight="bold">{opp.symbol}</Typography>
                    <Chip label={`${opp.score} AI`} color="primary" size="small" />
                 </Box>
                 <Chip label={opp.type} size="small" variant="outlined" sx={{ mb: 2, fontSize: '0.65rem' }} />
                 <Typography variant="body2" color="textSecondary" sx={{ lineHeight: 1.6, height: 60, overflow: 'hidden' }}>
                    {opp.thesis}
                 </Typography>
                 <Divider sx={{ my: 2, opacity: 0.1 }} />
                 <Button
                    fullWidth
                    variant="text"
                    size="small"
                    endIcon={<ChevronRight size={14} />}
                    onClick={() => navigate('/analysis', { state: { symbol: opp.symbol } })}
                    sx={{ justifyContent: 'space-between' }}
                 >
                    View Research
                 </Button>
              </Paper>
           </Grid>
         ))}
      </Grid>
    </Box>
  );
}
