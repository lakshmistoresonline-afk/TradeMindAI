import { Box, Typography, Paper, Grid, LinearProgress, Divider, Stack } from '@mui/material';
import { Brain, Target, ShieldCheck, Clock, Zap, AlertTriangle } from 'lucide-react';

export default function AIExecutiveSummary({ stock }: { stock: any }) {
  if (!stock || !stock.analysis) return null;

  const analysis = stock.analysis;
  const structured = stock.structured_consensus || {};

  // Resilient signal resolver
  const getRating = () => {
    if (structured.rating) return structured.rating;
    if (analysis.consensus) {
      const c = analysis.consensus.toUpperCase();
      if (c.includes('STRONG BUY')) return 'STRONG BUY';
      if (c.includes('STRONG SELL')) return 'STRONG SELL';
      if (c.includes('BUY')) return 'BUY';
      if (c.includes('SELL')) return 'SELL';
    }
    return 'HOLD';
  };

  const rating = getRating();
  const conviction = structured.conviction || stock.ai_investment_score || 50;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Brain size={20} className="text-emerald-500" /> Institutional Decision Hub
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%', border: '1px solid #10b981', bgcolor: 'rgba(16, 185, 129, 0.05)', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <Typography variant="subtitle2" color="textSecondary">INSTITUTIONAL RATING</Typography>
            <Typography variant="h2" color={rating.includes('BUY') ? 'primary' : rating.includes('SELL') ? 'error' : 'warning.main'} fontWeight="bold" sx={{ my: 1 }}>
                {rating}
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="caption">AI Conviction</Typography>
                <Typography variant="caption" fontWeight="bold">{conviction}%</Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={conviction}
                color={conviction > 70 ? 'primary' : conviction > 40 ? 'warning' : 'error'}
                sx={{ height: 8, borderRadius: 5 }}
              />
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <SummaryStat icon={<Zap size={16} />} label="Entry Zone" value={`₹${stock.last_price?.toLocaleString()}`} color="primary.main" />
              </Grid>
              <Grid item xs={6} sm={3}>
                <SummaryStat icon={<Target size={16} />} label="Price Target" value={structured.target ? `₹${structured.target.toLocaleString()}` : '---'} color="primary.main" />
              </Grid>
              <Grid item xs={6} sm={3}>
                <SummaryStat icon={<ShieldCheck size={16} />} label="Stop Loss" value={structured.stop_loss ? `₹${structured.stop_loss.toLocaleString()}` : '---'} color="error.main" />
              </Grid>
              <Grid item xs={6} sm={3}>
                <SummaryStat icon={<Clock size={16} />} label="Risk/Reward" value={structured.risk_reward || '1:2.0'} />
              </Grid>
            </Grid>

            <Divider sx={{ my: 3, opacity: 0.1 }} />

            <Typography variant="subtitle2" color="textSecondary" gutterBottom>PRIMARY THESIS</Typography>
            <Typography variant="body2" sx={{ lineHeight: 1.7, color: 'text.primary', mb: 2 }}>
              {structured.thesis || analysis.consensus}
            </Typography>

            <Stack direction="row" spacing={2} sx={{ mt: 'auto' }}>
               <Box sx={{ flex: 1, p: 1.5, bgcolor: 'rgba(244, 63, 94, 0.05)', borderRadius: 2, borderLeft: '3px solid #f43f5e' }}>
                  <Typography variant="caption" color="error" fontWeight="bold" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                     <AlertTriangle size={12} /> INVALIDATION
                  </Typography>
                  <Typography variant="caption" display="block" color="textSecondary">{structured.invalidation_point || 'Weekly close below major support.'}</Typography>
               </Box>
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function SummaryStat({ icon, label, value, color }: any) {
  return (
    <Box>
      <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        {icon} {label}
      </Typography>
      <Typography variant="h6" fontWeight="bold" sx={{ color: color || 'text.primary', fontSize: { xs: '1rem', sm: '1.25rem' } }}>{value}</Typography>
    </Box>
  );
}
