import { Box, Typography, Paper, Grid, Chip, Stack, List, ListItem, ListItemText, ListItemIcon, LinearProgress } from '@mui/material';
import { Target, RefreshCcw } from 'lucide-react';

export default function PortfolioOptimization() {
  const recommendations = [
    { type: 'REBALANCE', text: 'Reduce IT Sector exposure by 5% to match institutional benchmarks.', priority: 'HIGH' },
    { type: 'SIZE', text: 'RELIANCE: Increase position size by 2.5% based on breakout conviction.', priority: 'MEDIUM' },
    { type: 'DIVERSIFY', text: 'Add Healthcare exposure to reduce portfolio beta to 0.85.', priority: 'LOW' }
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Target size={20} className="text-emerald-500" /> AI Portfolio Optimization
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>ACTIVE REBALANCING SUGGESTIONS</Typography>
            <List>
               {recommendations.map((rec, i) => (
                 <ListItem key={i} sx={{ bgcolor: 'rgba(255,255,255,0.02)', mb: 1, borderRadius: 2 }}>
                    <ListItemIcon>
                       {rec.type === 'REBALANCE' ? <RefreshCcw className="text-blue-400" /> : <Target className="text-emerald-500" />}
                    </ListItemIcon>
                    <ListItemText primary={rec.text} primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }} />
                    <Chip label={rec.priority} size="small" color={rec.priority === 'HIGH' ? 'error' : 'primary'} variant="outlined" sx={{ fontSize: '0.6rem' }} />
                 </ListItem>
               ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, height: '100%', bgcolor: 'rgba(16, 185, 129, 0.05)', border: '1px solid #10b981' }}>
             <Typography variant="subtitle2" color="primary" gutterBottom>PORTFOLIO HEALTH SCORE</Typography>
             <Box sx={{ textAlign: 'center', my: 4 }}>
                <Typography variant="h2" fontWeight="bold">82</Typography>
                <Typography variant="caption" color="textSecondary">AAA - EXCELLENT</Typography>
             </Box>
             <Stack spacing={2}>
                <Box>
                   <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="caption">Risk/Reward Ratio</Typography>
                      <Typography variant="caption" fontWeight="bold">1.82</Typography>
                   </Box>
                   <LinearProgress variant="determinate" value={82} sx={{ height: 6, borderRadius: 2 }} />
                </Box>
                <Box>
                   <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="caption">Diversification</Typography>
                      <Typography variant="caption" fontWeight="bold">High</Typography>
                   </Box>
                   <LinearProgress variant="determinate" value={90} color="success" sx={{ height: 6, borderRadius: 2 }} />
                </Box>
             </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
