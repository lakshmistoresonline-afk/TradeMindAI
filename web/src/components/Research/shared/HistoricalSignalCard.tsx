import { Box, Typography, Paper, Grid, Stack, Chip, alpha, Divider, IconButton, Collapse } from '@mui/material';
import { Clock, ChevronDown, ChevronUp, Info, Activity } from 'lucide-react';
import { useState } from 'react';

interface HistoricalSignalCardProps {
  signal: any;
}

export default function HistoricalSignalCard({ signal }: HistoricalSignalCardProps) {
  const [expanded, setExpanded] = useState(false);

  const isHit = signal.status === 'TARGET_HIT' || signal.outcome === 'TARGET_HIT';
  const isStop = signal.status === 'STOP_LOSS' || signal.outcome === 'STOP_LOSS';
  const isExpired = signal.status === 'EXPIRED' || signal.outcome === 'EXPIRED';
  const isDerivative = signal.asset_class === 'FUTURES' || signal.asset_class === 'OPTIONS';

  // Ensure UTC enforcement for naive backend strings
  const ensureUTC = (ts: any) => {
    if (!ts) return null;
    if (typeof ts !== 'string') return ts;
    if (!ts.includes('Z') && !ts.includes('+') && !ts.includes('-')) return `${ts}Z`;
    return ts;
  };

  const createdDate = new Date(ensureUTC(signal.timestamp || signal.date) || Date.now());
  const outcomeDate = signal.outcome_date ? new Date(ensureUTC(signal.outcome_date)!) : null;

  const entry = signal.entry_price || signal.entry || 0;
  const target = signal.target_price || signal.target || 0;
  const stop = signal.stop_loss_price || signal.stop_loss || 0;
  const profitPct = signal.profit_pct || 0;

  // Derive P&L per share
  const profitPerShare = entry * (profitPct / 100);
  const outcomePrice = signal.outcome_price || (entry * (1 + profitPct / 100));

  // Date Formatting
  const formatDate = (date: Date) => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()} • ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} IST`;
  };

  const getStatusColor = () => {
    if (isHit) return '#10b981';
    if (isStop) return '#ef4444';
    if (isExpired) return '#64748b';
    return '#3b82f6';
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
        '&:hover': {
            bgcolor: '#111821',
            borderColor: alpha(getStatusColor(), 0.3)
        }
      }}
    >
      {/* Header Tier */}
      <Box sx={{ p: 2, pb: 1.5, display: 'grid', gridTemplateColumns: '1fr auto', gap: 2 }}>
         <Box sx={{ minWidth: 0 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {signal.asset_class === 'OPTIONS' ? `${signal.underlying_symbol} ${signal.strike} ${signal.option_type}` : signal.asset_class === 'FUTURES' ? `${signal.underlying_symbol} FUT` : signal.symbol}
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 700, color: 'text.secondary', display: 'block', mt: 0.5 }}>
                {signal.timeframe} • {signal.asset_class || 'EQUITY'}
            </Typography>
         </Box>
         <Box sx={{ textAlign: 'right' }}>
            <Chip
              label={(signal.status || signal.outcome || 'RESOLVED').replace('_', ' ')}
              size="small"
              sx={{ height: 18, fontSize: '0.55rem', fontWeight: 900, color: getStatusColor(), border: `1px solid ${alpha(getStatusColor(), 0.2)}`, bgcolor: alpha(getStatusColor(), 0.05) }}
            />
            <Typography variant="caption" sx={{ fontWeight: 800, color: 'text.secondary', display: 'block', mt: 0.5 }}>
                {signal.rating || 'BUY'}
            </Typography>
         </Box>
      </Box>

      <Divider sx={{ opacity: 0.03 }} />

      {/* Audit Meta Grid */}
      <Box sx={{ px: 2, py: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, bgcolor: 'rgba(255,255,255,0.01)' }}>
         <Box>
            <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.55rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 0.5 }}>
               <Clock size={10} /> GENERATED
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 800, color: 'white', fontSize: '0.65rem' }}>{formatDate(createdDate)}</Typography>
         </Box>
         <Box sx={{ textAlign: 'right' }}>
            <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.55rem', fontWeight: 800, display: 'block' }}>
                {signal.expiry ? `EXPIRY: ${new Date(ensureUTC(signal.expiry)!).toLocaleDateString(undefined, { day: 'numeric', month: 'short' })}` : 'RESOLUTION'}
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 800, fontSize: '0.65rem', color: 'text.secondary' }}>{outcomeDate ? formatDate(outcomeDate) : '---'}</Typography>
         </Box>
      </Box>

      <Box sx={{ p: 2, flexGrow: 1 }}>
         <Grid container spacing={2}>
            <Grid item xs={6}>
               <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.6rem', fontWeight: 800 }}>
                   {signal.asset_class === 'OPTIONS' ? 'ENTRY PREMIUM' : 'ENTRY PRICE'}
               </Typography>
               <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: 'JetBrains Mono' }}>₹{entry.toLocaleString()}</Typography>
            </Grid>
            <Grid item xs={6} sx={{ textAlign: 'right' }}>
               <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.6rem', fontWeight: 800 }}>
                   {signal.asset_class === 'OPTIONS' ? 'OUTCOME PREMIUM' : 'OUTCOME PRICE'}
               </Typography>
               <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: 'JetBrains Mono', color: isHit ? '#10b981' : isStop ? '#ef4444' : 'white' }}>
                   ₹{outcomePrice.toLocaleString()}
               </Typography>
            </Grid>
            <Grid item xs={6}>
               <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.6rem', fontWeight: 800 }}>STOP LOSS</Typography>
               <Typography variant="body2" sx={{ fontWeight: 700, color: '#ef4444', fontFamily: 'JetBrains Mono', opacity: 0.7 }}>₹{stop.toLocaleString()}</Typography>
            </Grid>
            <Grid item xs={6} sx={{ textAlign: 'right' }}>
               <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.6rem', fontWeight: 800 }}>TARGET</Typography>
               <Typography variant="body2" sx={{ fontWeight: 700, color: '#10b981', fontFamily: 'JetBrains Mono', opacity: 0.7 }}>₹{target.toLocaleString()}</Typography>
            </Grid>
         </Grid>

         {isDerivative && signal.underlying_price && (
            <Box sx={{ mt: 1.5, p: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center', bgcolor: 'rgba(0, 209, 255, 0.02)', borderRadius: 1 }}>
                <Typography variant="caption" sx={{ fontWeight: 800, color: 'primary.main', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Activity size={10} /> {signal.underlying_symbol} SPOT AT RES
                </Typography>
                <Typography variant="caption" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono' }}>
                    ₹{Math.round(signal.underlying_price).toLocaleString()}
                </Typography>
            </Box>
         )}

         <Box sx={{ mt: 2, p: 1.5, bgcolor: 'rgba(0,0,0,0.2)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.03)' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
               <Box>
                  <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.55rem', fontWeight: 800 }}>FINAL P&L</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 900, color: profitPct >= 0 ? '#10b981' : '#ef4444' }}>
                     {profitPct >= 0 ? '+' : ''}{profitPct.toFixed(2)}%
                  </Typography>
               </Box>
               <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="caption" color="textSecondary" display="block" sx={{ fontSize: '0.55rem', fontWeight: 800 }}>P/L PER UNIT</Typography>
                  <Typography variant="body2" sx={{ fontWeight: 900, color: profitPerShare >= 0 ? '#10b981' : '#ef4444', fontFamily: 'JetBrains Mono' }}>
                     {profitPerShare >= 0 ? '+' : '-'}₹{Math.abs(Math.round(profitPerShare)).toLocaleString()}
                  </Typography>
               </Box>
            </Box>
         </Box>

         {/* Audit Lifecycle */}
         <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Stack direction="row" spacing={0.6}>
                <AuditStep label="GEN" completed={true} />
                <AuditStep label="TRG" completed={!isExpired} />
                <AuditStep label="RES" completed={true} color={getStatusColor()} />
            </Stack>
            <IconButton size="small" onClick={() => setExpanded(!expanded)} sx={{ color: 'text.secondary', bgcolor: 'rgba(255,255,255,0.03)' }}>
                {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </IconButton>
         </Box>

         <Collapse in={expanded}>
            <Box sx={{ mt: 1.5, pt: 1.5, borderTop: '1px solid rgba(255,255,255,0.03)' }}>
                <Typography variant="caption" sx={{ fontWeight: 800, color: 'slategray', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                   <Info size={10} /> SYSTEM AUDIT TRAIL
                </Typography>
                <Typography variant="body2" sx={{ fontSize: '0.7rem', color: 'text.secondary', mt: 0.5, lineHeight: 1.4 }}>
                    Signal record preserved from {createdDate.toLocaleDateString()}. Resolution achieved at ₹{outcomePrice.toLocaleString()} with verified metadata.
                </Typography>
            </Box>
         </Collapse>
      </Box>
    </Paper>
  );
}

function AuditStep({ label, completed, color = '#10b981' }: { label: string, completed: boolean, color?: string }) {
    return (
        <Box sx={{ textAlign: 'center' }}>
            <Box sx={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                bgcolor: completed ? color : 'rgba(255,255,255,0.1)',
                mx: 'auto',
                mb: 0.3
            }} />
            <Typography variant="caption" sx={{ fontSize: '0.45rem', fontWeight: 900, color: completed ? 'white' : 'text.disabled' }}>{label}</Typography>
        </Box>
    );
}
