import { Box, Typography, Drawer, IconButton, Divider, Stack, Button, Paper, LinearProgress, Grid } from '@mui/material';
import { X, ExternalLink, Target, ShieldCheck, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAITradeDecision } from '../../hooks/useAITradeDecision';

interface QuickResearchDrawerProps {
  open: boolean;
  onClose: () => void;
  stock: any;
}

export default function QuickResearchDrawer({ open, onClose, stock }: QuickResearchDrawerProps) {
  const navigate = useNavigate();
  const decision = useAITradeDecision(stock);

  if (!stock) return null;

  const isBullish = decision.rating.includes('BUY');
  const isBearish = decision.rating.includes('SELL');

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: { width: { xs: '100%', sm: 400 }, bgcolor: '#0f172a', borderLeft: '1px solid #1e293b' }
      }}
    >
      <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight={800}>Quick Research</Typography>
          <IconButton onClick={onClose} size="small" sx={{ color: 'text.secondary' }}>
            <X size={20} />
          </IconButton>
        </Box>

        <Divider sx={{ mb: 3, opacity: 0.1 }} />

        <Box sx={{ mb: 4 }}>
           <Typography variant="h4" fontWeight={900}>{stock.symbol}</Typography>
           <Typography variant="body2" color="textSecondary" sx={{ fontWeight: 600 }}>{stock.name}</Typography>

           <Stack direction="row" spacing={2} sx={{ mt: 2 }} alignItems="center">
              <Typography variant="h5" fontWeight={800} sx={{ fontFamily: 'JetBrains Mono' }}>₹{stock.last_price?.toLocaleString()}</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: stock.change_pct >= 0 ? 'primary.main' : 'error.main' }}>
                 {stock.change_pct >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                 <Typography variant="body2" fontWeight="bold">{stock.change_pct?.toFixed(2)}%</Typography>
              </Box>
           </Stack>
        </Box>

        <Paper sx={{ p: 3, mb: 4, bgcolor: isBullish ? 'rgba(16, 185, 129, 0.05)' : isBearish ? 'rgba(244, 63, 94, 0.05)' : 'rgba(255,255,255,0.02)', border: '1px solid #334155' }}>
           <Stack direction="row" justifyContent="space-between" mb={1}>
              <Typography variant="caption" color="textSecondary" fontWeight={800}>AI RATING</Typography>
              <Typography variant="caption" color="primary.main" fontWeight={900}>{decision.timeframe}</Typography>
           </Stack>
           <Typography variant="h3" fontWeight={900} color={isBullish ? 'primary.main' : isBearish ? 'error.main' : 'warning.main'} sx={{ mb: 1 }}>
              {decision.rating}
           </Typography>
           <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="caption" fontWeight={800}>{decision.conviction}% CONVICTION</Typography>
              <Typography variant="caption" color="textSecondary" fontWeight={700}>Risk: {decision.riskLevel}</Typography>
           </Box>
           <LinearProgress
             variant="determinate"
             value={decision.conviction}
             color={isBullish ? 'primary' : isBearish ? 'error' : 'warning'}
             sx={{ height: 4, borderRadius: 2 }}
           />
        </Paper>

        <Stack spacing={3} sx={{ flexGrow: 1 }}>
           <Grid container spacing={2}>
              <Grid item xs={6}>
                 <QuickStat icon={<Target size={14} />} label="TARGET" value={decision.target ? `₹${decision.target.toLocaleString()}` : '---'} color="primary.main" />
              </Grid>
              <Grid item xs={6}>
                 <QuickStat icon={<ShieldCheck size={14} />} label="STOP LOSS" value={decision.stopLoss ? `₹${decision.stopLoss.toLocaleString()}` : '---'} color="error.main" />
              </Grid>
           </Grid>

           <Box>
              <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 800, mb: 1 }}>
                 <Activity size={14} /> FORENSIC THESIS
              </Typography>
              <Typography variant="body2" sx={{ lineHeight: 1.6, color: 'text.secondary', fontWeight: 500 }}>
                 {decision.thesis?.substring(0, 180)}...
              </Typography>
           </Box>
        </Stack>

        <Button
          fullWidth
          variant="contained"
          onClick={() => {
            onClose();
            navigate('/analysis', { state: { symbol: stock.symbol } });
          }}
          startIcon={<ExternalLink size={18} />}
          sx={{ mt: 4, py: 1.5, fontWeight: 900 }}
        >
          Institutional Intelligence
        </Button>
      </Box>
    </Drawer>
  );
}

function QuickStat({ icon, label, value, color }: any) {
  return (
    <Box>
       <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 800 }}>
          {icon} {label}
       </Typography>
       <Typography variant="body1" fontWeight={800} sx={{ color, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
    </Box>
  );
}
