import { Box, Typography, Paper, Grid, Stack, Chip, Button, alpha, LinearProgress, Divider } from '@mui/material';
import { Zap, Clock, ArrowRight, Star } from 'lucide-react';
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
  const isHighConviction = decision.conviction > 80;

  // Derived Analytics (Section 15)
  const entry = decision.entry || 0;
  const current = stock.last_price || entry;
  const target = decision.target || (isBuy ? entry * 1.05 : entry * 0.95);
  const stop = decision.stopLoss || (isBuy ? entry * 0.97 : entry * 1.03);

  // Target Progress calculation
  let progress = 0;
  if (isBuy) {
    progress = ((current - entry) / (target - entry)) * 100;
  } else {
    progress = ((entry - current) / (entry - target)) * 100;
  }
  progress = Math.max(0, Math.min(100, progress));

  // Risk/Reward ratio
  const risk = Math.abs(entry - stop);
  const reward = Math.abs(target - entry);
  const rrRatio = risk > 0 ? (reward / risk).toFixed(1) : '1:2.0';

  const createdDate = decision.generatedAt ? new Date(decision.generatedAt) : new Date();
  const thesisText = decision.thesis || 'Analyzing session dynamics...';

  return (
    <Paper
      elevation={0}
      sx={{
        p: 0,
        height: '100%',
        border: '1px solid rgba(255,255,255,0.05)',
        borderRadius: 3,
        overflow: 'hidden',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        cursor: 'pointer',
        bgcolor: '#0C1118',
        position: 'relative',
        '&:hover': {
          borderColor: isBuy ? alpha('#10b981', 0.3) : alpha('#ef4444', 0.3),
          bgcolor: '#111821',
          transform: 'translateY(-4px)',
          boxShadow: `0 12px 24px -10px ${isBuy ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`
        },
        ...(isHighConviction && {
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0, left: 0, right: 0, height: 2,
            background: 'linear-gradient(90deg, #00D1FF, #7C3AED)'
          }
        })
      }}
      onClick={() => navigate('/analysis', { state: { symbol: stock.symbol } })}
    >
      {/* Header Tier */}
      <Box sx={{ p: 3, pb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Stack direction="row" spacing={1} alignItems="center">
               <Typography variant="h5" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', display: 'flex', alignItems: 'center', gap: 1 }}>
                  {stock.symbol}
                  {isHighConviction && <Star size={16} className="text-yellow-400" fill="currentColor" />}
               </Typography>
               <Chip
                  label={decision.status}
                  size="small"
                  sx={{
                    height: 16,
                    fontSize: '0.55rem',
                    fontWeight: 900,
                    bgcolor: alpha(isBuy ? '#10b981' : '#ef4444', 0.1),
                    color: isBuy ? '#10b981' : '#ef4444',
                    border: `1px solid ${alpha(isBuy ? '#10b981' : '#ef4444', 0.2)}`
                  }}
               />
            </Stack>
            <Typography variant="caption" sx={{ fontWeight: 700, color: 'text.secondary', textTransform: 'uppercase', mt: 0.5, display: 'block' }}>
               {stock.industry || 'NSE Asset'} • {decision.timeframe}
            </Typography>
          </Box>
          <Stack direction="column" spacing={0.5} alignItems="flex-end">
             <Typography
               variant="h6"
               sx={{
                 fontWeight: 900,
                 color: isBuy ? '#10b981' : '#ef4444',
                 lineHeight: 1
               }}
             >
                {decision.rating}
             </Typography>
             <Typography variant="caption" sx={{ fontWeight: 800, fontSize: '0.65rem', color: 'primary.main' }}>
                {decision.conviction}% CONFIDENCE
             </Typography>
          </Stack>
        </Box>
      </Box>

      {/* Timing Tier (Section 9) */}
      <Box sx={{ px: 3, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
         <Clock size={12} className="text-slategray" />
         <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700, fontSize: '0.65rem' }}>
            CREATED: {createdDate.toLocaleDateString()} • {createdDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
         </Typography>
      </Box>

      {/* Trade Levels Grid (Section 9) */}
      <Box sx={{ px: 3, py: 2, bgcolor: 'rgba(0,0,0,0.2)', borderTop: '1px solid rgba(255,255,255,0.03)', borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.6rem' }}>ENTRY PRICE</Typography>
            <Typography variant="body1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: 'white' }}>
               ₹{Math.round(entry).toLocaleString()}
            </Typography>
          </Grid>
          <Grid item xs={6} sx={{ textAlign: 'right' }}>
            <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.6rem' }}>CURRENT PRICE</Typography>
            <Typography variant="body1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: current >= entry ? '#10b981' : '#ef4444' }}>
               ₹{Math.round(current).toLocaleString()}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.6rem' }}>STOP LOSS</Typography>
            <Typography variant="body1" sx={{ fontWeight: 900, color: '#ef4444', fontFamily: 'JetBrains Mono' }}>
               ₹{Math.round(stop).toLocaleString()}
            </Typography>
          </Grid>
          <Grid item xs={6} sx={{ textAlign: 'right' }}>
            <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.6rem' }}>TARGET</Typography>
            <Typography variant="body1" sx={{ fontWeight: 900, color: '#10b981', fontFamily: 'JetBrains Mono' }}>
               ₹{Math.round(target).toLocaleString()}
            </Typography>
          </Grid>
        </Grid>
      </Box>

      {/* Derived Analytics Tier (Section 15) */}
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
           <Typography variant="caption" sx={{ fontWeight: 800, color: 'text.secondary' }}>TARGET PROGRESS</Typography>
           <Typography variant="caption" sx={{ fontWeight: 900, color: 'primary.main' }}>{Math.round(progress)}%</Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={progress}
          sx={{
            height: 6,
            borderRadius: 3,
            bgcolor: alpha('#fff', 0.05),
            '& .MuiLinearProgress-bar': {
              background: `linear-gradient(90deg, ${isBuy ? '#10b981' : '#ef4444'}, #00D1FF)`
            }
          }}
        />

        <Stack direction="row" justifyContent="space-between" sx={{ mt: 2 }}>
           <Box>
              <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.55rem', fontWeight: 800 }}>RISK/REWARD</Typography>
              <Typography variant="body2" sx={{ fontWeight: 900, color: '#00D1FF' }}>1 : {rrRatio}</Typography>
           </Box>
           <Box sx={{ textAlign: 'right' }}>
              <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.55rem', fontWeight: 800 }}>SIGNAL QUALITY</Typography>
              <Chip
                label={isHighConviction ? "HIGH" : "MEDIUM"}
                size="small"
                sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900, bgcolor: 'rgba(255,255,255,0.05)' }}
              />
           </Box>
        </Stack>

        <Divider sx={{ my: 2, opacity: 0.05 }} />

        {/* Evidence Digest (Section 18) */}
        <Typography variant="caption" sx={{ fontWeight: 900, color: 'secondary.main', display: 'flex', alignItems: 'center', gap: 0.5, mb: 1, letterSpacing: 1 }}>
           <Zap size={12} /> FORENSIC EVIDENCE
        </Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 500, fontSize: '0.75rem', lineHeight: 1.5, minHeight: 44 }}>
           {thesisText.length > 120 ? thesisText.substring(0, 117) + '...' : thesisText}
        </Typography>

        <Stack direction="row" spacing={1} sx={{ mt: 2, flexWrap: 'wrap', gap: 1 }}>
           {decision.drivers?.slice(0, 2).map((d: string, i: number) => (
              <Chip
                key={i}
                label={d.toUpperCase()}
                size="small"
                sx={{ height: 18, fontSize: '0.55rem', fontWeight: 800, bgcolor: alpha('#7C3AED', 0.05), color: '#7C3AED', border: `1px solid ${alpha('#7C3AED', 0.1)}` }}
              />
           ))}
        </Stack>

        <Button
          fullWidth
          variant="outlined"
          endIcon={<ArrowRight size={14} />}
          sx={{
             mt: 3,
             py: 1,
             justifyContent: 'space-between',
             color: 'text.primary',
             borderColor: 'rgba(255,255,255,0.05)',
             '&:hover': { borderColor: 'primary.main', bgcolor: alpha('#00D1FF', 0.05) }
          }}
        >
           OPEN SIGNAL LAB
        </Button>
      </Box>
    </Paper>
  );
}
