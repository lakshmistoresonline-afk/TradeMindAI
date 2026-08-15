import { Box, Typography, Paper, Grid, Stack, Chip, alpha, Divider, IconButton, Collapse } from '@mui/material';
import { Clock, ChevronDown, ChevronUp, Info, CheckCircle2, ShieldAlert, XCircle } from 'lucide-react';
import { useState } from 'react';

interface HistoricalSignalCardProps {
  signal: any;
}

export default function HistoricalSignalCard({ signal }: HistoricalSignalCardProps) {
  const [expanded, setExpanded] = useState(false);

  const status = signal.status || signal.outcome || 'RESOLVED';
  const isHit = status === 'TARGET_HIT';
  const isStop = status === 'STOP_LOSS';
  const isExpired = status === 'EXPIRED';
  const assetClass = signal.asset_class || 'EQUITY';
  const isOptions = assetClass === 'OPTIONS';
  const isFutures = assetClass === 'FUTURES';

  // Ensure UTC enforcement
  const ensureUTC = (ts: any) => {
    if (!ts) return null;
    if (typeof ts !== 'string') return ts;
    if (!ts.includes('Z') && !ts.includes('+') && !ts.includes('-')) return `${ts}Z`;
    return ts;
  };

  const createdDate = new Date(ensureUTC(signal.timestamp || signal.date) || 0);
  const outcomeDate = signal.outcome_date ? new Date(ensureUTC(signal.outcome_date)!) : null;

  const entry = signal.entry_price || signal.entry || 0;
  const target = signal.target_price || signal.target || 0;
  const stop = signal.stop_loss_price || signal.stop_loss || 0;
  const profitPct = signal.profit_pct || 0;

  const outcomePrice = signal.outcome_price;

  // Date Formatting
  const formatDate = (date: Date) => {
    if (!date || isNaN(date.getTime())) return '—';
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()} • ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} IST`;
  };

  const getStatusColor = () => {
    if (isHit) return '#10b981';
    if (isStop) return '#ef4444';
    if (isExpired) return '#64748b';
    return '#3b82f6';
  };

  const getStatusIcon = () => {
    if (isHit) return <CheckCircle2 size={14} />;
    if (isStop) return <ShieldAlert size={14} />;
    if (isExpired) return <XCircle size={14} />;
    return <Clock size={14} />;
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
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
            bgcolor: '#111827',
            borderColor: alpha(getStatusColor(), 0.3)
        }
      }}
    >
      {/* Header Tier */}
      <Box sx={{ p: 2, display: 'grid', gridTemplateColumns: '1fr auto', gap: 1 }}>
         <Box sx={{ minWidth: 0 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: '#fff', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {isOptions ? `${signal.underlying_symbol || signal.symbol} ${signal.strike || ''} ${signal.option_type || ''}` : isFutures ? `${signal.underlying_symbol || signal.symbol} FUT` : signal.symbol}
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 800, color: 'slategray', display: 'block', mt: 0.2 }}>
                {signal.timeframe} • {assetClass}
            </Typography>
         </Box>
         <Box sx={{ textAlign: 'right' }}>
            <Typography variant="caption" sx={{ fontWeight: 900, color: profitPct >= 0 ? '#10b981' : '#ef4444', fontSize: '1rem', lineHeight: 1 }}>
                {profitPct >= 0 ? '+' : ''}{profitPct.toFixed(2)}%
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 800, color: 'slategray', display: 'block', mt: 0.5 }}>
                {signal.rating || 'BUY'}
            </Typography>
         </Box>
      </Box>

      <Box sx={{ px: 2, pb: 1.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Chip
              label={status.replace(/_/g, ' ')}
              size="small"
              icon={getStatusIcon()}
              sx={{
                  height: 18,
                  fontSize: '0.55rem',
                  fontWeight: 900,
                  borderRadius: 0.5,
                  bgcolor: alpha(getStatusColor(), 0.1),
                  color: getStatusColor(),
                  border: `1px solid ${alpha(getStatusColor(), 0.2)}`,
                  '& .MuiChip-icon': { color: 'inherit' }
              }}
           />
      </Box>

      <Divider sx={{ opacity: 0.05 }} />

      {/* Meta Audit Grid */}
      <Box sx={{ px: 2, py: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, bgcolor: 'rgba(255,255,255,0.01)' }}>
         <Box>
            <Typography variant="caption" sx={{ color: 'slategray', fontSize: '0.55rem', fontWeight: 800, display: 'block' }}>GENERATED</Typography>
            <Typography variant="caption" sx={{ fontWeight: 700, color: '#e2e8f0', fontSize: '0.65rem' }}>{formatDate(createdDate)}</Typography>
         </Box>
         <Box sx={{ textAlign: 'right' }}>
            <Typography variant="caption" sx={{ color: 'slategray', fontSize: '0.55rem', fontWeight: 800, display: 'block' }}>RESOLUTION</Typography>
            <Typography variant="caption" sx={{ fontWeight: 700, color: '#e2e8f0', fontSize: '0.65rem' }}>{outcomeDate ? formatDate(outcomeDate) : '—'}</Typography>
         </Box>
      </Box>

      <Box sx={{ p: 2, flexGrow: 1 }}>
         <Grid container spacing={2}>
            <Grid item xs={6}>
               <Typography variant="caption" sx={{ fontSize: '0.55rem', color: 'slategray', fontWeight: 800, display: 'block', mb: 0.5 }}>{isOptions ? 'ENTRY PREMIUM' : 'ENTRY PRICE'}</Typography>
               <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: 'JetBrains Mono', color: '#fff' }}>₹{entry ? entry.toLocaleString() : '—'}</Typography>
            </Grid>
            <Grid item xs={6} sx={{ textAlign: 'right' }}>
               <Typography variant="caption" sx={{ fontSize: '0.55rem', color: 'slategray', fontWeight: 800, display: 'block', mb: 0.5 }}>{isOptions ? 'EXIT PREMIUM' : 'EXIT PRICE'}</Typography>
               <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: 'JetBrains Mono', color: '#fff' }}>{outcomePrice ? `₹${outcomePrice.toLocaleString()}` : '—'}</Typography>
            </Grid>
            <Grid item xs={6}>
               <Typography variant="caption" sx={{ fontSize: '0.55rem', color: 'slategray', fontWeight: 800, display: 'block', mb: 0.5 }}>STOP LOSS</Typography>
               <Typography variant="body2" sx={{ fontWeight: 700, color: '#ef4444', fontFamily: 'JetBrains Mono', opacity: 0.7 }}>₹{stop ? stop.toLocaleString() : '—'}</Typography>
            </Grid>
            <Grid item xs={6} sx={{ textAlign: 'right' }}>
               <Typography variant="caption" sx={{ fontSize: '0.55rem', color: 'slategray', fontWeight: 800, display: 'block', mb: 0.5 }}>TARGET</Typography>
               <Typography variant="body2" sx={{ fontWeight: 700, color: '#10b981', fontFamily: 'JetBrains Mono', opacity: 0.7 }}>₹{target ? target.toLocaleString() : '—'}</Typography>
            </Grid>
         </Grid>

         <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Stack direction="row" spacing={0.6}>
                <AuditStep label="GEN" completed={true} />
                <AuditStep label="TRG" completed={!isExpired} />
                <AuditStep label="RES" completed={true} color={getStatusColor()} />
            </Stack>
            <IconButton size="small" onClick={() => setExpanded(!expanded)} sx={{ color: 'slategray', p: 0.5 }}>
                {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </IconButton>
         </Box>

         <Collapse in={expanded}>
            <Box sx={{ mt: 1.5, pt: 1.5, borderTop: '1px solid rgba(255,255,255,0.03)' }}>
                <Typography variant="caption" sx={{ fontWeight: 800, color: 'slategray', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                   <Info size={10} /> AUDIT METADATA
                </Typography>
                <Typography variant="body2" sx={{ fontSize: '0.7rem', color: 'slategray', mt: 0.5, lineHeight: 1.4, fontWeight: 500 }}>
                    Signal record preserved from {formatDate(createdDate).split(' • ')[0]}.
                    Historical resolution confirmed by TradeMind Auditor at ₹{outcomePrice ? outcomePrice.toLocaleString() : '—'}.
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
                width: 5,
                height: 5,
                borderRadius: '50%',
                bgcolor: completed ? color : 'rgba(255,255,255,0.1)',
                mx: 'auto',
                mb: 0.3
            }} />
            <Typography variant="caption" sx={{ fontSize: '0.45rem', fontWeight: 900, color: completed ? 'white' : 'slategray' }}>{label}</Typography>
        </Box>
    );
}
