import { Box, Typography, Paper, Grid, Stack, Chip, alpha, Divider } from '@mui/material';
import { Clock, ShieldAlert, CheckCircle2, XCircle } from 'lucide-react';

interface HistoricalSignalCardProps {
  signal: any;
}

export default function HistoricalSignalCard({ signal }: HistoricalSignalCardProps) {
  const isHit = signal.status === 'TARGET_HIT';
  const isStop = signal.status === 'STOP_LOSS';
  const isExpired = signal.status === 'EXPIRED';

  const createdDate = signal.timestamp ? new Date(signal.timestamp) : (signal.date ? new Date(signal.date) : new Date());
  const outcomeDate = signal.outcome_date ? new Date(signal.outcome_date) : null;

  const entry = signal.entry_price || signal.entry || 0;
  const target = signal.target_price || signal.target || 0;
  const stop = signal.stop_loss_price || signal.stop_loss || 0;
  const profitPct = signal.profit_pct || 0;

  // Holding duration calculation
  let durationStr = '---';
  if (outcomeDate) {
    const diffMs = outcomeDate.getTime() - createdDate.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    durationStr = `${diffHours}h ${diffMins}m`;
  }

  const getStatusColor = () => {
    if (isHit) return '#10b981';
    if (isStop) return '#ef4444';
    if (isExpired) return '#64748b';
    return '#3b82f6';
  };

  const getStatusIcon = () => {
    if (isHit) return <CheckCircle2 size={16} />;
    if (isStop) return <ShieldAlert size={16} />;
    if (isExpired) return <XCircle size={16} />;
    return <Clock size={16} />;
  };

  return (
    <Paper
      elevation={0}
      sx={{
        p: 0,
        border: '1px solid rgba(255,255,255,0.05)',
        borderRadius: 2,
        overflow: 'hidden',
        bgcolor: '#0C1118',
        '&:hover': {
            bgcolor: '#111821',
            borderColor: alpha(getStatusColor(), 0.3)
        }
      }}
    >
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
         <Stack direction="row" spacing={1.5} alignItems="center">
            <Typography variant="subtitle1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono' }}>{signal.symbol}</Typography>
            <Chip
              label={signal.rating || 'BUY'}
              size="small"
              sx={{ height: 16, fontSize: '0.55rem', fontWeight: 900, bgcolor: 'rgba(255,255,255,0.05)' }}
            />
         </Stack>
         <Stack direction="row" spacing={1} alignItems="center">
            <Typography variant="caption" sx={{ fontWeight: 800, color: getStatusColor(), display: 'flex', alignItems: 'center', gap: 0.5 }}>
               {getStatusIcon()} {signal.status?.replace('_', ' ')}
            </Typography>
         </Stack>
      </Box>

      <Box sx={{ p: 2 }}>
         <Grid container spacing={2}>
            <Grid item xs={6}>
               <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.6rem', fontWeight: 800 }}>ENTRY</Typography>
               <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: 'JetBrains Mono' }}>₹{Math.round(entry).toLocaleString()}</Typography>
            </Grid>
            <Grid item xs={6} sx={{ textAlign: 'right' }}>
               <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.6rem', fontWeight: 800 }}>OUTCOME PRICE</Typography>
               <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: 'JetBrains Mono' }}>₹{Math.round(signal.outcome_price || target).toLocaleString()}</Typography>
            </Grid>
            <Grid item xs={4}>
               <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.6rem', fontWeight: 800 }}>STOP LOSS</Typography>
               <Typography variant="body2" sx={{ fontWeight: 700, color: '#ef4444', fontFamily: 'JetBrains Mono' }}>₹{Math.round(stop).toLocaleString()}</Typography>
            </Grid>
            <Grid item xs={4} sx={{ textAlign: 'center' }}>
               <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.6rem', fontWeight: 800 }}>TARGET</Typography>
               <Typography variant="body2" sx={{ fontWeight: 700, color: '#10b981', fontFamily: 'JetBrains Mono' }}>₹{Math.round(target).toLocaleString()}</Typography>
            </Grid>
            <Grid item xs={4} sx={{ textAlign: 'right' }}>
               <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.6rem', fontWeight: 800 }}>RESULT %</Typography>
               <Typography variant="body2" sx={{ fontWeight: 900, color: profitPct >= 0 ? '#10b981' : '#ef4444' }}>
                  {profitPct >= 0 ? '+' : ''}{profitPct.toFixed(2)}%
               </Typography>
            </Grid>
         </Grid>

         <Divider sx={{ my: 1.5, opacity: 0.05 }} />

         <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
               <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.55rem', fontWeight: 700 }}>GENERATED</Typography>
               <Typography variant="caption" sx={{ fontWeight: 800 }}>{createdDate.toLocaleDateString()} {createdDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</Typography>
            </Box>
            {outcomeDate && (
               <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.55rem', fontWeight: 700 }}>OUTCOME REACHED</Typography>
                  <Typography variant="caption" sx={{ fontWeight: 800 }}>{outcomeDate.toLocaleDateString()} {outcomeDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</Typography>
               </Box>
            )}
         </Box>

         <Box sx={{ mt: 1.5, p: 1, bgcolor: 'rgba(0,0,0,0.2)', borderRadius: 1, display: 'flex', justifyContent: 'center' }}>
            <Typography variant="caption" sx={{ fontWeight: 800, color: 'text.secondary', display: 'flex', alignItems: 'center', gap: 0.5 }}>
               <Clock size={10} /> DURATION: {durationStr}
            </Typography>
         </Box>
      </Box>
    </Paper>
  );
}
