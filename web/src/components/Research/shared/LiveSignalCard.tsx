import { Box, Typography, Paper, Grid, Stack, Chip, alpha, Divider, Button, Tooltip } from '@mui/material';
import { HelpCircle } from 'lucide-react';
// V2.3 Hardened Card
import { useNavigate } from 'react-router-dom';
import { AITradeDecision } from '../../../types/domain';

interface LiveSignalCardProps {
  stock: any;
  decision: AITradeDecision;
}

export default function LiveSignalCard({ stock, decision }: LiveSignalCardProps) {
  const navigate = useNavigate();

  if (!decision) return null;

  const isBuy = decision.rating?.includes('BUY');

  // authorative levels from decision
  const entry = decision.entry;
  const target = decision.target;
  const stop = decision.stopLoss;
  const current = decision.normalizedCurrentPrice || stock.last_price || stock.current_price;

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'UNAVAILABLE';
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return 'UNAVAILABLE';
      return `${date.getDate()} ${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][date.getMonth()]} ${date.getFullYear()} • ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} IST`;
    } catch {
      return 'UNAVAILABLE';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return '#3b82f6';
      case 'ENTRY_TRIGGERED': return '#00D1FF';
      case 'WAITING_FOR_ENTRY': return '#f59e0b';
      case 'TARGET_HIT': return '#10b981';
      case 'STOP_LOSS': return '#ef4444';
      default: return 'slategray';
    }
  };

  return (
    <Paper
      sx={{
        p: 0,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: 1,
        overflow: 'hidden',
        bgcolor: '#0f172a',
        transition: '0.2s',
        '&:hover': { borderColor: 'primary.main', bgcolor: '#111827', transform: 'translateY(-2px)' }
      }}
    >
      {/* 1. Primary Identity Area */}
      <Box sx={{ p: 2.5, bgcolor: alpha(isBuy ? '#10b981' : '#ef4444', 0.03) }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
           <Box>
              <Typography variant="h6" sx={{ fontWeight: 950, fontFamily: 'JetBrains Mono', letterSpacing: -0.5, color: '#fff' }}>{stock.symbol}</Typography>
              <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, textTransform: 'uppercase', display: 'block', mt: 0.2 }}>{stock.company_name || stock.name || 'INSTRUMENT'}</Typography>
           </Box>
           <Box sx={{ textAlign: 'right' }}>
              <Chip
                label={isBuy ? 'LONG ▲' : 'SHORT ▼'}
                size="small"
                sx={{
                  fontWeight: 950,
                  bgcolor: alpha(isBuy ? '#10b981' : '#ef4444', 0.1),
                  color: isBuy ? '#10b981' : '#ef4444',
                  borderRadius: 0.5,
                  height: 24,
                  px: 1
                }}
              />
           </Box>
        </Box>

        <Stack direction="row" spacing={1.5} sx={{ mt: 2.5 }}>
           <Box sx={{ borderLeft: `3px solid ${decision.timeframe === 'SWING' ? '#10b981' : '#00D1FF'}`, pl: 1.5 }}>
              <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, display: 'block', fontSize: '0.55rem' }}>HORIZON · CLASS</Typography>
              <Typography variant="caption" sx={{ fontWeight: 950, color: '#fff', letterSpacing: 0.5 }}>{decision.timeframe} · {decision.qualityClass}</Typography>
           </Box>
           <Box sx={{ borderLeft: '3px solid rgba(255,255,255,0.05)', pl: 1.5 }}>
              <Stack direction="row" spacing={0.5} alignItems="center">
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, display: 'block', fontSize: '0.55rem' }}>MODEL PROBABILITY</Typography>
                  <Tooltip title="Model-derived probability estimate based on the current model and evidence. It is not a guarantee of outcome.">
                     <HelpCircle size={10} color="slategray" style={{ cursor: 'help' }} />
                  </Tooltip>
              </Stack>
              <Typography variant="caption" sx={{ fontWeight: 950, color: 'primary.main', fontSize: '0.8rem' }}>{decision.conviction}%</Typography>
           </Box>
        </Stack>
      </Box>

      {/* 2. Trade Levels Area */}
      <Box sx={{ p: 2.5, flexGrow: 1 }}>
         <Grid container spacing={3}>
            <LevelItem label="ENTRY" value={entry} />
            <LevelItem label="CURRENT" value={current} color={(current && entry) ? (isBuy ? (current >= entry ? '#10b981' : '#ef4444') : (current <= entry ? '#10b981' : '#ef4444')) : '#fff'} />
            <LevelItem label="TARGET" value={target} color="#10b981" />
            <LevelItem label="STOP LOSS" value={stop} color="#ef4444" />
         </Grid>

         <Divider sx={{ my: 3, opacity: 0.05 }} />

         <Grid container spacing={3}>
            <Grid item xs={6}>
               <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.55rem', display: 'block' }}>EXPECTED VALUE</Typography>
               <Typography variant="body2" sx={{ fontWeight: 950, color: (decision.expectedValue || 0) > 0 ? '#10b981' : '#ef4444', fontFamily: 'JetBrains Mono' }}>
                  {decision.expectedValue !== undefined ? `₹${decision.expectedValue.toFixed(2)}` : 'UNAVAILABLE'}
               </Typography>
            </Grid>
            <Grid item xs={6} sx={{ textAlign: 'right' }}>
               <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.55rem', display: 'block' }}>RISK / REWARD</Typography>
               <Typography variant="body2" sx={{ fontWeight: 950, color: 'primary.main', fontFamily: 'JetBrains Mono' }}>{decision.riskReward}</Typography>
            </Grid>
         </Grid>
      </Box>

      {/* 3. Status & Timing Area */}
      <Box sx={{ px: 2.5, py: 2, bgcolor: 'rgba(255,255,255,0.01)', borderTop: '1px solid rgba(255,255,255,0.03)' }}>
         <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Chip
               label={decision.status?.replace(/_/g, ' ')}
               size="small"
               sx={{
                  height: 20,
                  fontSize: '0.55rem',
                  fontWeight: 950,
                  bgcolor: alpha(getStatusColor(decision.status), 0.1),
                  color: getStatusColor(decision.status),
                  borderRadius: 0.5
               }}
            />
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, fontSize: '0.55rem' }}>{stock.price_status || 'FRESH'} FEED</Typography>
         </Box>

         <Stack spacing={1.5}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
               <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.5rem' }}>CREATED AT</Typography>
               <Typography variant="caption" sx={{ color: '#e2e8f0', fontWeight: 800, fontSize: '0.5rem' }}>{formatDate(decision.generatedAt)}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
               <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.5rem' }}>DATA TIME</Typography>
               <Typography variant="caption" sx={{ color: '#e2e8f0', fontWeight: 800, fontSize: '0.5rem' }}>{formatDate(stock.data_timestamp || stock.timestamp)}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2 }}>
                {decision.signalAgeHours !== undefined && (
                    <Box sx={{ flex: 1 }}>
                        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.5rem' }}>SIGNAL AGE</Typography>
                        <Typography variant="caption" sx={{ color: decision.signalAgeHours > 24 ? '#ef4444' : '#10b981', fontWeight: 800, fontSize: '0.5rem', display: 'block' }}>
                            {decision.signalAgeHours.toFixed(1)} HOURS
                        </Typography>
                    </Box>
                )}
                {decision.dataAgeHours !== undefined && (
                    <Box sx={{ flex: 1, textAlign: 'right' }}>
                        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.5rem' }}>DATA AGE</Typography>
                        <Typography variant="caption" sx={{ color: decision.dataAgeHours > 24 ? '#ef4444' : '#10b981', fontWeight: 800, fontSize: '0.5rem', display: 'block' }}>
                            {decision.dataAgeHours.toFixed(1)} HOURS
                        </Typography>
                    </Box>
                )}
            </Box>
         </Stack>
      </Box>

      <Button
        fullWidth
        variant="text"
        onClick={() => navigate(`/signals/${decision.id}`)}
        sx={{
           py: 1.5,
           borderRadius: 0,
           color: 'primary.main',
           fontWeight: 950,
           fontSize: '0.65rem',
           letterSpacing: 1,
           textTransform: 'uppercase',
           borderTop: '1px solid rgba(255,255,255,0.03)',
           '&:hover': { bgcolor: alpha('#00D1FF', 0.05) }
        }}
      >
         View Details & Evidence
      </Button>
    </Paper>
  );
}

function LevelItem({ label, value, color = '#fff' }: { label: string, value?: number, color?: string }) {
   return (
      <Grid item xs={6}>
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.55rem', display: 'block', mb: 0.5 }}>{label}</Typography>
         <Typography variant="body1" sx={{ fontWeight: 950, fontFamily: 'JetBrains Mono', color }}>{value ? `₹${value.toLocaleString()}` : 'UNAVAILABLE'}</Typography>
      </Grid>
   );
}
