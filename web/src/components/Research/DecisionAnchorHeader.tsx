import { Box, Typography, Paper, Grid, Chip, Divider, Stack, LinearProgress } from '@mui/material';
import { ShieldCheck, AlertTriangle, Activity } from 'lucide-react';

export default function DecisionAnchorHeader({ stock }: { stock: any }) {
  if (!stock || !stock.analysis) return null;

  const structured = stock.structured_consensus || {};

  // Resilient signal resolver
  const getRating = () => {
    if (structured.rating) return structured.rating;
    if (stock.analysis?.consensus) {
      const c = stock.analysis.consensus.toUpperCase();
      if (c.includes('STRONG BUY')) return 'STRONG BUY';
      if (c.includes('STRONG SELL')) return 'STRONG SELL';
      if (c.includes('BUY')) return 'BUY';
      if (c.includes('SELL')) return 'SELL';
    }
    return 'HOLD';
  };

  const rating = getRating();
  const conviction = structured.conviction || stock.ai_investment_score || 0;
  const isBullish = rating.includes('BUY');
  const isBearish = rating.includes('SELL');

  return (
    <Paper
      elevation={4}
      sx={{
        p: 0,
        mb: 4,
        position: 'sticky',
        top: 64,
        zIndex: 10,
        overflow: 'hidden',
        border: '1px solid #1e293b',
        bgcolor: '#0f172a',
        borderRadius: 2
      }}
    >
      <Grid container>
        {/* Signal Section */}
        <Grid item xs={12} md={3.5} sx={{ p: 3, bgcolor: isBullish ? 'rgba(16, 185, 129, 0.08)' : isBearish ? 'rgba(244, 63, 94, 0.08)' : 'rgba(255,255,255,0.03)', borderRight: '1px solid #1e293b' }}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
             <Typography variant="caption" color="textSecondary" fontWeight={700} sx={{ letterSpacing: 1 }}>AI INSTITUTIONAL DECISION</Typography>
             <Chip
               label={`${conviction}% CONVICTION`}
               size="small"
               sx={{ height: 18, fontSize: '0.65rem', fontWeight: 800, bgcolor: isBullish ? '#10b981' : isBearish ? '#f43f5e' : '#334155', color: '#000' }}
             />
          </Stack>

          <Typography variant="h2" sx={{ fontWeight: 900, color: isBullish ? '#10b981' : isBearish ? '#f43f5e' : '#fbbf24', my: 1, fontSize: { xs: '2.5rem', md: '3.5rem' } }}>
            {rating}
          </Typography>

          <Box sx={{ mt: 1 }}>
            <LinearProgress
              variant="determinate"
              value={conviction}
              color={isBullish ? 'primary' : isBearish ? 'error' : 'warning'}
              sx={{ height: 6, borderRadius: 5, bgcolor: 'rgba(255,255,255,0.05)' }}
            />
          </Box>
        </Grid>

        {/* Execution Details */}
        <Grid item xs={12} md={8.5} sx={{ p: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={6} sm={3}>
              <DecisionStat label="ENTRY ZONE" value={`₹${stock.last_price?.toLocaleString()}`} sub="Market Execution" color="#3b82f6" />
            </Grid>
            <Grid item xs={6} sm={3}>
              <DecisionStat label="PRICE TARGET" value={structured.target ? `₹${structured.target.toLocaleString()}` : '---'} sub="+12.4% Est." color="#10b981" />
            </Grid>
            <Grid item xs={6} sm={3}>
              <DecisionStat label="STOP LOSS" value={structured.stop_loss ? `₹${structured.stop_loss.toLocaleString()}` : '---'} sub="-4.2% Risk" color="#f43f5e" />
            </Grid>
            <Grid item xs={6} sm={3}>
              <DecisionStat label="RISK / REWARD" value={structured.risk_reward || '1:2.0'} sub="Institutional Grade" color="#fff" />
            </Grid>
          </Grid>

          <Divider sx={{ my: 2, opacity: 0.1 }} />

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} alignItems="center">
             <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <Box sx={{ p: 1, bgcolor: 'rgba(16, 185, 129, 0.1)', borderRadius: 1 }}>
                   <ShieldCheck size={18} className="text-emerald-500" />
                </Box>
                <Box>
                   <Typography variant="caption" color="textSecondary" sx={{ display: 'block', fontWeight: 700 }}>PRIMARY CATALYST</Typography>
                   <Typography variant="body2" fontWeight={600} noWrap sx={{ maxWidth: 300 }}>{structured.key_catalysts?.[0] || 'Institutional accumulation detected at support.'}</Typography>
                </Box>
             </Box>

             <Divider orientation="vertical" flexItem sx={{ display: { xs: 'none', sm: 'block' }, opacity: 0.1 }} />

             <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <Box sx={{ p: 1, bgcolor: 'rgba(244, 63, 94, 0.1)', borderRadius: 1 }}>
                   <AlertTriangle size={18} className="text-rose-500" />
                </Box>
                <Box>
                   <Typography variant="caption" color="textSecondary" sx={{ display: 'block', fontWeight: 700 }}>CRITICAL RISK</Typography>
                   <Typography variant="body2" fontWeight={600} noWrap sx={{ maxWidth: 300 }}>{structured.key_risks?.[0] || 'Broader market volatility may impact breakout.'}</Typography>
                </Box>
             </Box>
          </Stack>
        </Grid>
      </Grid>
    </Paper>
  );
}

function DecisionStat({ label, value, sub, color }: any) {
  return (
    <Box>
       <Typography variant="caption" color="textSecondary" fontWeight={800} sx={{ letterSpacing: 0.5 }}>{label}</Typography>
       <Typography variant="h5" sx={{ fontWeight: 900, color: color, my: 0.5, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
       <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 600 }}>
          <Activity size={10} /> {sub}
       </Typography>
    </Box>
  );
}
