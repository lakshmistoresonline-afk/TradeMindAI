import { Box, Typography, Paper, Grid, Stack, Chip, Button, alpha, LinearProgress, Divider, IconButton, Collapse } from '@mui/material';
import { Zap, ArrowRight, Star, ChevronDown, ChevronUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { AITradeDecision } from '../../../types/domain';
import { useState } from 'react';

interface LiveSignalCardProps {
  stock: any;
  decision: AITradeDecision;
}

export default function LiveSignalCard({ stock, decision }: LiveSignalCardProps) {
  const navigate = useNavigate();
  const [expanded, setExpanded] = useState(false);

  if (!decision) return null;

  const isBuy = decision.rating?.includes('BUY');
  const isHighConviction = decision.conviction > 80;
  const assetClass = decision.assetClass || 'EQUITY';
  const isOptions = assetClass === 'OPTIONS';
  const isFutures = assetClass === 'FUTURES';

  // Authoritative Trade Levels
  const entry = decision.entry;
  const current = stock.last_price;
  const target = decision.target;
  const stop = decision.stopLoss;

  // Status-aware Progress calculation
  let progress = 0;
  const isTradeActive = ['ACTIVE', 'ENTRY_TRIGGERED'].includes(decision.status);

  if (isTradeActive && target && entry && current) {
    if (isBuy) {
      progress = ((current - entry) / (target - entry)) * 100;
    } else {
      progress = ((entry - current) / (entry - target)) * 100;
    }
  }
  progress = Math.max(0, Math.min(100, progress));

  // Risk/Reward ratio
  let rrRatio = '—';
  if (entry && target && stop) {
    const risk = Math.abs(entry - stop);
    const reward = Math.abs(target - entry);
    rrRatio = risk > 0 ? `1 : ${(reward / risk).toFixed(2)}` : '—';
  }

  // Consistent Date Formatting
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '—';
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return '—';
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()} • ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} IST`;
    } catch {
      return '—';
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
      elevation={0}
      sx={{
        p: 0,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: 1,
        overflow: 'hidden',
        bgcolor: '#0f172a',
        transition: '0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          borderColor: isBuy ? alpha('#10b981', 0.4) : alpha('#ef4444', 0.4),
          bgcolor: '#111827',
          transform: 'translateY(-2px)'
        }
      }}
    >
      {/* 1. Header Area */}
      <Box sx={{ p: 2, display: 'grid', gridTemplateColumns: '1fr auto', gap: 1 }}>
        <Box sx={{ minWidth: 0 }}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Typography variant="h6" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: '#fff' }}>
              {isOptions ? `${decision.underlyingSymbol} ${decision.strike} ${decision.optionType}` : isFutures ? `${decision.underlyingSymbol} FUT` : stock.symbol}
            </Typography>
            {isHighConviction && <Star size={14} fill="#fbbf24" color="#fbbf24" />}
          </Stack>
          <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, textTransform: 'uppercase', display: 'block', mt: 0.2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {stock.name || 'INSTRUMENT'} • {assetClass}
          </Typography>
        </Box>

        <Box sx={{ textAlign: 'right' }}>
           <Typography variant="h6" sx={{ fontWeight: 900, color: isBuy ? '#10b981' : '#ef4444', lineHeight: 1 }}>
              {isBuy ? 'BUY ▲' : 'SELL ▼'}
           </Typography>
           <Typography variant="caption" sx={{ fontWeight: 900, color: 'primary.main', display: 'block', mt: 0.5, letterSpacing: 0.5 }}>
              {decision.conviction}% CONVICTION
           </Typography>
        </Box>
      </Box>

      <Box sx={{ px: 2, pb: 1.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Chip
              label={decision.status?.replace(/_/g, ' ')}
              size="small"
              sx={{
                height: 18,
                fontSize: '0.55rem',
                fontWeight: 900,
                borderRadius: 0.5,
                bgcolor: alpha(getStatusColor(decision.status), 0.1),
                color: getStatusColor(decision.status),
                border: `1px solid ${alpha(getStatusColor(decision.status), 0.2)}`
              }}
           />
           <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700, fontSize: '0.65rem' }}>
              {decision.timeframe}
           </Typography>
      </Box>

      <Divider sx={{ opacity: 0.05 }} />

      {/* 2. Metadata Area */}
      <Box sx={{ px: 2, py: 1.5, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, bgcolor: 'rgba(255,255,255,0.01)' }}>
         <Box>
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.55rem', display: 'block' }}>CREATED</Typography>
            <Typography variant="caption" sx={{ fontWeight: 700, color: '#e2e8f0' }}>{formatDate(decision.generatedAt)}</Typography>
         </Box>
         {decision.expiry && (
            <Box sx={{ textAlign: 'right' }}>
                <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.55rem', display: 'block' }}>EXPIRY</Typography>
                <Typography variant="caption" sx={{ fontWeight: 700, color: '#e2e8f0' }}>{formatDate(decision.expiry).split(' • ')[0]}</Typography>
            </Box>
         )}
      </Box>

      {/* 3. Trade Levels Area */}
      <Box sx={{ px: 2, py: 2, borderTop: '1px solid rgba(255,255,255,0.03)', borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
        <Grid container spacing={2}>
           <Grid item xs={6}>
              <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.55rem', display: 'block', mb: 0.5 }}>{isOptions ? 'ENTRY PREMIUM' : 'ENTRY PRICE'}</Typography>
              <Typography variant="body2" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: '#fff' }}>{entry ? `₹${entry.toLocaleString()}` : '—'}</Typography>
           </Grid>
           <Grid item xs={6} sx={{ textAlign: 'right' }}>
              <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.55rem', display: 'block', mb: 0.5 }}>{isOptions ? 'CURRENT PREMIUM' : 'CURRENT PRICE'}</Typography>
              <Typography variant="body2" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: (current && entry) ? (isBuy ? (current >= entry ? '#10b981' : '#ef4444') : (current <= entry ? '#10b981' : '#ef4444')) : '#fff' }}>
                {current ? `₹${current.toLocaleString()}` : 'Data unavailable'}
              </Typography>
           </Grid>
           <Grid item xs={6}>
              <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.55rem', display: 'block', mb: 0.5 }}>STOP LOSS</Typography>
              <Typography variant="body2" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: '#ef4444' }}>{stop ? `₹${stop.toLocaleString()}` : '—'}</Typography>
           </Grid>
           <Grid item xs={6} sx={{ textAlign: 'right' }}>
              <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.55rem', display: 'block', mb: 0.5 }}>TARGET</Typography>
              <Typography variant="body2" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: '#10b981' }}>{target ? `₹${target.toLocaleString()}` : '—'}</Typography>
           </Grid>
        </Grid>
      </Box>

      {/* 4. Analytics Area */}
      <Box sx={{ p: 2, flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.8 }}>
           <Typography variant="caption" sx={{ fontWeight: 800, color: 'slategray', fontSize: '0.6rem' }}>TARGET PROGRESS</Typography>
           <Typography variant="caption" sx={{ fontWeight: 900, color: isTradeActive ? 'primary.main' : 'slategray', fontSize: '0.6rem' }}>
              {isTradeActive ? `${Math.round(progress)}%` : 'WAITING FOR TRIGGER'}
           </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={isTradeActive ? progress : 0}
          sx={{
            height: 4,
            borderRadius: 1,
            bgcolor: 'rgba(255,255,255,0.03)',
            '& .MuiLinearProgress-bar': {
              background: isTradeActive ? `linear-gradient(90deg, ${isBuy ? '#10b981' : '#ef4444'}, #00D1FF)` : 'transparent'
            }
          }}
        />

        <Stack direction="row" justifyContent="space-between" sx={{ mt: 2 }}>
           <Box>
              <Typography variant="caption" sx={{ color: 'slategray', fontSize: '0.55rem', fontWeight: 800, display: 'block' }}>RISK/REWARD</Typography>
              <Typography variant="body2" sx={{ fontWeight: 900, color: '#00D1FF', fontSize: '0.75rem' }}>{rrRatio}</Typography>
           </Box>
           {isOptions && stock.last_price && (
             <Box sx={{ textAlign: 'center' }}>
                <Typography variant="caption" sx={{ color: 'slategray', fontSize: '0.55rem', fontWeight: 800, display: 'block' }}>SPOT PRICE</Typography>
                <Typography variant="body2" sx={{ fontWeight: 900, color: '#fff', fontSize: '0.75rem' }}>₹{Math.round(stock.last_price).toLocaleString()}</Typography>
             </Box>
           )}
           <Box sx={{ textAlign: 'right' }}>
              <Typography variant="caption" sx={{ color: 'slategray', fontSize: '0.55rem', fontWeight: 800, display: 'block' }}>SIGNAL TYPE</Typography>
              <Chip
                label={assetClass === 'EQUITY' ? 'CASH' : assetClass}
                size="small"
                sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 0.5 }}
              />
           </Box>
        </Stack>

        <Divider sx={{ my: 2, opacity: 0.05 }} />

        {/* 5. Simplified Lifecycle View */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Stack direction="row" spacing={1}>
                <LifecycleStep label="GEN" completed={true} />
                <LifecycleStep label="TRG" active={decision.status === 'ENTRY_TRIGGERED'} completed={['ACTIVE', 'TARGET_HIT', 'STOP_LOSS'].includes(decision.status)} />
                <LifecycleStep label="RES" active={false} completed={['TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'CANCELLED'].includes(decision.status)} color={isBuy ? '#10b981' : '#ef4444'} />
            </Stack>
            <IconButton size="small" onClick={() => setExpanded(!expanded)} sx={{ color: expanded ? 'primary.main' : 'slategray', p: 0.5 }}>
                {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </IconButton>
        </Box>

        <Collapse in={expanded}>
            <Box sx={{ mt: 2, p: 1.5, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.03)' }}>
                <Typography variant="caption" sx={{ fontWeight: 900, color: 'secondary.main', display: 'flex', alignItems: 'center', gap: 0.5, mb: 1, letterSpacing: 1 }}>
                    <Zap size={10} /> AI THESIS
                </Typography>
                <Typography variant="body2" sx={{ color: 'slategray', fontSize: '0.75rem', lineHeight: 1.5, fontWeight: 500 }}>
                    {decision.thesis || 'Analyzing institutional order flow dynamics...'}
                </Typography>
                {decision.drivers && decision.drivers.length > 0 && (
                  <Stack direction="row" spacing={1} sx={{ mt: 1.5, flexWrap: 'wrap', gap: 1 }}>
                    {decision.drivers.slice(0, 2).map((d: string, i: number) => (
                        <Chip key={i} label={d.toUpperCase()} size="small" sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900, bgcolor: 'rgba(124, 58, 237, 0.1)', color: '#7C3AED', border: '1px solid rgba(124, 58, 237, 0.2)', borderRadius: 0.5 }} />
                    ))}
                  </Stack>
                )}
            </Box>
        </Collapse>
      </Box>

      <Button
        fullWidth
        variant="text"
        onClick={() => navigate('/analysis', { state: { symbol: stock.symbol } })}
        endIcon={<ArrowRight size={14} />}
        sx={{
           py: 1.5,
           borderRadius: 0,
           color: 'primary.main',
           fontWeight: 800,
           fontSize: '0.7rem',
           letterSpacing: 1,
           borderTop: '1px solid rgba(255,255,255,0.03)',
           textTransform: 'none',
           '&:hover': { bgcolor: 'rgba(0, 209, 255, 0.05)' }
        }}
      >
         View Details & Evidence
      </Button>
    </Paper>
  );
}

function LifecycleStep({ label, active, completed, color = '#3b82f6' }: { label: string, active?: boolean, completed?: boolean, color?: string }) {
    return (
        <Box sx={{ textAlign: 'center' }}>
            <Box sx={{
                width: 5,
                height: 5,
                borderRadius: '50%',
                bgcolor: completed ? color : active ? '#00D1FF' : 'rgba(255,255,255,0.1)',
                mx: 'auto',
                mb: 0.5,
                boxShadow: active ? `0 0 8px ${color}` : 'none'
            }} />
            <Typography variant="caption" sx={{ fontSize: '0.45rem', fontWeight: 900, color: (active || completed) ? 'white' : 'slategray' }}>{label}</Typography>
        </Box>
    );
}
