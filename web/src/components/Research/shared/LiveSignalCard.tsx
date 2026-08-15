import { Box, Typography, Paper, Grid, Stack, Chip, Button, alpha, LinearProgress, Divider, IconButton, Collapse, Tooltip } from '@mui/material';
import { Zap, ArrowRight, Star, ChevronDown, ChevronUp, Clock, Info } from 'lucide-react';
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

  // Authoritative Trade Levels (Section 35 Audit)
  const entry = decision.entry || 0;
  const current = stock.last_price || entry;
  const target = decision.target || 0;
  const stop = decision.stopLoss || 0;

  // Status-aware Progress calculation
  let progress = 0;
  const isTradeActive = decision.status === 'ACTIVE' || decision.status === 'ENTRY_TRIGGERED';

  if (isTradeActive && target && target !== entry) {
    if (isBuy) {
      progress = ((current - entry) / (target - entry)) * 100;
    } else {
      progress = ((entry - current) / (entry - target)) * 100;
    }
  }
  progress = Math.max(0, Math.min(100, progress));

  // Risk/Reward ratio
  let rrRatio = '---';
  if (entry && target && stop) {
    const risk = Math.abs(entry - stop);
    const reward = Math.abs(target - entry);
    rrRatio = risk > 0 ? `1 : ${(reward / risk).toFixed(2)}` : '---';
  }

  // Consistent Date Formatting (Section 12 & 17)
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '---';
    const date = new Date(dateStr);
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${date.getDate()} ${monthNames[date.getMonth()]} ${date.getFullYear()} • ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} IST`;
  };

  return (
    <Paper
      elevation={0}
      sx={{
        p: 0,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        border: '1px solid rgba(255,255,255,0.05)',
        borderRadius: 2,
        overflow: 'hidden',
        bgcolor: '#0C1118',
        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'relative',
        '&:hover': {
          borderColor: 'primary.main',
          bgcolor: '#111821',
          transform: 'translateY(-4px)',
          boxShadow: '0 12px 32px rgba(0,0,0,0.5)'
        }
      }}
    >
      {/* Header Tier (Section 49) */}
      <Box sx={{ p: 2.5, pb: 2, display: 'grid', gridTemplateColumns: '1fr auto', gap: 2 }}>
        <Box sx={{ minWidth: 0 }}>
          <Stack direction="row" spacing={1} alignItems="center">
            <Typography variant="h5" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {stock.symbol}
            </Typography>
            {isHighConviction && <Star size={16} className="text-yellow-400" fill="currentColor" />}
          </Stack>
          <Typography
            variant="caption"
            sx={{
                fontWeight: 700,
                color: 'text.secondary',
                display: 'block',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                mt: 0.5,
                textTransform: 'uppercase'
            }}
          >
            {stock.name || stock.industry || 'MARKET ASSET'}
          </Typography>
          <Typography variant="caption" sx={{ fontWeight: 800, color: 'primary.main', letterSpacing: 1, mt: 0.5, display: 'block' }}>
            {decision.assetClass === 'OPTIONS' ? `${decision.underlyingSymbol} ${decision.strike} ${decision.optionType}` : decision.assetClass === 'FUTURES' ? `${decision.underlyingSymbol} FUT` : decision.timeframe}
          </Typography>
        </Box>

        <Box sx={{ textAlign: 'right' }}>
           <Chip
              label={decision.status?.replace('_', ' ')}
              size="small"
              sx={{
                height: 20,
                fontSize: '0.55rem',
                fontWeight: 900,
                mb: 1,
                bgcolor: alpha(isBuy ? '#10b981' : '#ef4444', 0.1),
                color: isBuy ? '#10b981' : '#ef4444',
                border: `1px solid ${alpha(isBuy ? '#10b981' : '#ef4444', 0.2)}`
              }}
           />
           <Typography variant="h6" sx={{ fontWeight: 900, color: isBuy ? '#10b981' : '#ef4444', lineHeight: 1 }}>
              {decision.rating} {isBuy ? '▲' : '▼'}
           </Typography>
           <Typography variant="caption" sx={{ fontWeight: 800, fontSize: '0.65rem', color: 'primary.main', display: 'block', mt: 0.5 }}>
              {decision.conviction}% CONVICTION
           </Typography>
        </Box>
      </Box>

      <Divider sx={{ opacity: 0.05 }} />

      {/* Meta Audit (Section 17) */}
      <Box sx={{ px: 2.5, py: 1.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
         <Box>
            <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.55rem', display: 'flex', alignItems: 'center', gap: 0.5 }}>
               <Clock size={10} /> CREATED
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 800, color: 'white' }}>{formatDate(decision.generatedAt)}</Typography>
         </Box>
         {decision.expiry && (
            <Box sx={{ textAlign: 'right' }}>
                <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.55rem', display: 'block' }}>EXPIRY</Typography>
                <Typography variant="caption" sx={{ fontWeight: 800, color: 'secondary.main' }}>{new Date(decision.expiry).toLocaleDateString(undefined, { day: 'numeric', month: 'short' })}</Typography>
            </Box>
         )}
         {!decision.expiry && (
            <Tooltip title={`Internal ID Hidden • Status: ${decision.status}`}>
                <IconButton size="small" sx={{ opacity: 0.3 }}><Info size={12} /></IconButton>
            </Tooltip>
         )}
      </Box>

      {/* Trade Levels Grid (Section 54 & 55) */}
      <Box sx={{ px: 2.5, py: 2, bgcolor: 'rgba(255,255,255,0.01)', borderTop: '1px solid rgba(255,255,255,0.03)', borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
        <Grid container spacing={2}>
           <Grid item xs={6}>
              <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.6rem', display: 'block', mb: 0.5 }}>ENTRY PRICE</Typography>
              <Typography variant="body1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: 'white' }}>₹{Math.round(entry).toLocaleString()}</Typography>
           </Grid>
           <Grid item xs={6} sx={{ textAlign: 'right' }}>
              <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.6rem', display: 'block', mb: 0.5 }}>CURRENT PRICE</Typography>
              <Typography variant="body1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: current >= entry ? '#10b981' : '#ef4444' }}>₹{Math.round(current).toLocaleString()}</Typography>
           </Grid>
           <Grid item xs={6}>
              <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.6rem', display: 'block', mb: 0.5 }}>STOP LOSS</Typography>
              <Typography variant="body1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: '#ef4444' }}>₹{Math.round(stop).toLocaleString()}</Typography>
           </Grid>
           <Grid item xs={6} sx={{ textAlign: 'right' }}>
              <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.6rem', display: 'block', mb: 0.5 }}>TARGET</Typography>
              <Typography variant="body1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: '#10b981' }}>₹{Math.round(target).toLocaleString()}</Typography>
           </Grid>
        </Grid>
      </Box>

      {/* Analytics Summary */}
      <Box sx={{ p: 2.5, flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
           <Typography variant="caption" sx={{ fontWeight: 800, color: 'text.secondary' }}>TARGET PROGRESS</Typography>
           <Typography variant="caption" sx={{ fontWeight: 900, color: isTradeActive ? 'primary.main' : 'text.disabled' }}>
              {isTradeActive ? `${Math.round(progress)}%` : 'WAITING FOR ENTRY'}
           </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={isTradeActive ? progress : 0}
          sx={{
            height: 6,
            borderRadius: 3,
            bgcolor: 'rgba(255,255,255,0.05)',
            '& .MuiLinearProgress-bar': {
              background: isTradeActive ? `linear-gradient(90deg, ${isBuy ? '#10b981' : '#ef4444'}, #00D1FF)` : 'transparent'
            }
          }}
        />

        <Stack direction="row" justifyContent="space-between" sx={{ mt: 2.5 }}>
           <Box>
              <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.55rem', fontWeight: 800, display: 'block' }}>RISK/REWARD</Typography>
              <Typography variant="body2" sx={{ fontWeight: 900, color: '#00D1FF' }}>{rrRatio}</Typography>
           </Box>
           <Box sx={{ textAlign: 'right' }}>
              <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.55rem', fontWeight: 800, display: 'block' }}>SIGNAL SCORE</Typography>
              <Chip
                label={isHighConviction ? "PREMIUM" : "STANDARD"}
                size="small"
                sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900, bgcolor: 'rgba(255,255,255,0.05)' }}
              />
           </Box>
        </Stack>

        <Divider sx={{ my: 2, opacity: 0.05 }} />

        {/* Canonical Lifecycle (Section 33) */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Stack direction="row" spacing={0.8}>
                <LifecycleStep label="GEN" completed={true} />
                <LifecycleStep label="VAL" completed={true} />
                <LifecycleStep label="TRG" active={decision.status !== 'WAITING_FOR_ENTRY'} completed={['ACTIVE', 'TARGET_HIT', 'STOP_LOSS', 'ENTRY_TRIGGERED'].includes(decision.status)} />
                <LifecycleStep label="ACT" active={decision.status === 'ACTIVE'} completed={['TARGET_HIT', 'STOP_LOSS'].includes(decision.status)} />
                <LifecycleStep label="RES" active={false} completed={['TARGET_HIT', 'STOP_LOSS', 'EXPIRED'].includes(decision.status)} color={isBuy ? '#10b981' : '#ef4444'} />
            </Stack>
            <IconButton size="small" onClick={() => setExpanded(!expanded)} sx={{ color: 'primary.main', bgcolor: 'rgba(0, 209, 255, 0.05)' }}>
                {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </IconButton>
        </Box>

        <Collapse in={expanded}>
            <Box sx={{ mt: 2, p: 1.5, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1 }}>
                <Typography variant="caption" sx={{ fontWeight: 900, color: 'secondary.main', display: 'flex', alignItems: 'center', gap: 0.5, mb: 1, letterSpacing: 1 }}>
                    <Zap size={10} /> FORENSIC EVIDENCE
                </Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary', fontSize: '0.75rem', lineHeight: 1.5 }}>
                    {decision.thesis || 'Institutional order flow alignment detected on multiple timeframes.'}
                </Typography>
                <Stack direction="row" spacing={1} sx={{ mt: 1.5, flexWrap: 'wrap', gap: 1 }}>
                   {decision.drivers?.slice(0, 2).map((d: string, i: number) => (
                      <Chip key={i} label={d.toUpperCase()} size="small" sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900, bgcolor: 'rgba(124, 58, 237, 0.1)', color: '#7C3AED', border: '1px solid rgba(124, 58, 237, 0.2)' }} />
                   ))}
                </Stack>
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
           '&:hover': { bgcolor: 'rgba(0, 209, 255, 0.08)' }
        }}
      >
         VIEW SIGNAL DETAILS
      </Button>
    </Paper>
  );
}

function LifecycleStep({ label, active, completed, color = '#3b82f6' }: { label: string, active?: boolean, completed?: boolean, color?: string }) {
    return (
        <Box sx={{ textAlign: 'center' }}>
            <Box sx={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                bgcolor: completed ? '#10b981' : active ? color : 'rgba(255,255,255,0.1)',
                mx: 'auto',
                mb: 0.5,
                boxShadow: active ? `0 0 8px ${color}` : 'none'
            }} />
            <Typography variant="caption" sx={{ fontSize: '0.45rem', fontWeight: 900, color: (active || completed) ? 'white' : 'text.disabled' }}>{label}</Typography>
        </Box>
    );
}
