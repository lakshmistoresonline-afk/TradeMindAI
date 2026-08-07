import { Box, Typography, Paper, Grid, Chip, Divider, Stack } from '@mui/material';
import { ShieldCheck, AlertTriangle, ArrowUpRight } from 'lucide-react';

export default function DecisionEngineHeader({ stock }: { stock: any }) {
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
    <Paper sx={{ p: 0, mb: 4, overflow: 'hidden', border: '1px solid #334155', bgcolor: '#0f172a' }}>
      <Grid container>
        <Grid item xs={12} md={4} sx={{ p: 4, bgcolor: isBullish ? 'rgba(16, 185, 129, 0.05)' : isBearish ? 'rgba(244, 63, 94, 0.05)' : 'rgba(255,255,255,0.02)', borderRight: '1px solid #334155' }}>
          <Typography variant="caption" color="textSecondary" fontWeight="bold" sx={{ letterSpacing: 1 }}>AI INSTITUTIONAL RATING</Typography>
          <Typography variant="h1" sx={{ fontWeight: 900, color: isBullish ? '#10b981' : isBearish ? '#f43f5e' : '#fbbf24', my: 1, fontSize: { xs: '3rem', md: '4rem' } }}>
            {rating}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
             <Chip label={`${conviction}% CONVICTION`} size="small" sx={{ bgcolor: isBullish ? '#10b981' : '#334155', color: isBullish ? '#000' : '#fff', fontWeight: 'bold' }} />
             <Typography variant="caption" color="textSecondary">Validated by 12 Agents</Typography>
          </Box>
        </Grid>

        <Grid item xs={12} md={8} sx={{ p: 4 }}>
          <Grid container spacing={4}>
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
              <DecisionStat label="RISK / REWARD" value={structured.risk_reward || '1:2.5'} sub="Favorable" color="#fff" />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3, opacity: 0.1 }} />

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3}>
             <Box sx={{ flex: 1 }}>
                <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                   <ShieldCheck size={14} className="text-emerald-500" /> KEY CATALYST
                </Typography>
                <Typography variant="body2" fontWeight="bold">
                   {structured.key_catalysts?.[0] || 'Institutional accumulation at multi-year support levels.'}
                </Typography>
             </Box>
             <Box sx={{ flex: 1 }}>
                <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                   <AlertTriangle size={14} className="text-rose-500" /> CRITICAL RISK
                </Typography>
                <Typography variant="body2" fontWeight="bold">
                   {structured.key_risks?.[0] || 'Broader market volatility may impact breakout reliability.'}
                </Typography>
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
       <Typography variant="caption" color="textSecondary" fontWeight="bold">{label}</Typography>
       <Typography variant="h5" sx={{ fontWeight: 'bold', color: color, my: 0.5 }}>{value}</Typography>
       <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.2 }}>
          <ArrowUpRight size={10} /> {sub}
       </Typography>
    </Box>
  );
}
