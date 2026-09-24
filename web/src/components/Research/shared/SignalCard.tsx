import { useState } from 'react';
import { Box, Typography, Paper, Grid, Stack, Chip, alpha, LinearProgress, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, InputAdornment, Divider, IconButton, Tooltip } from '@mui/material';
import { ArrowUpRight, ArrowDownRight, Clock, Calculator, Share2, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { AITradeDecision } from '../../../types/domain';

interface SignalCardProps {
  stock: any;
  decision: AITradeDecision;
}

export default function SignalCard({ stock, decision }: SignalCardProps) {
  const navigate = useNavigate();
  const [isCalcOpen, setIsCalcOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [accountCapital, setAccountCapital] = useState<number>(100000);
  const [riskPct, setRiskPct] = useState<number>(1.0);

  const handleCopyLink = () => {
    const url = `${window.location.origin}/signals/${decision.id}`;
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!decision) return null;

  const isBuy = decision.rating?.includes('BUY');
  const entry = decision.entry;
  const target = decision.target;
  const stop = decision.stopLoss;
  const current = decision.normalizedCurrentPrice;
  const conviction = decision.conviction || 75;

  return (
    <Paper
      elevation={0}
      sx={{
        p: 0,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'rgba(15, 23, 42, 0.95)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: 2,
        overflow: 'hidden',
        transition: 'all 0.2s ease-in-out',
        backdropFilter: 'blur(12px)',
        position: 'relative',
        '&:hover': {
          borderColor: isBuy ? '#10b981' : '#f43f5e',
          bgcolor: 'rgba(15, 23, 42, 0.98)',
          transform: 'translateY(-2px)',
          boxShadow: isBuy ? '0 10px 25px -5px rgba(16, 185, 129, 0.15)' : '0 10px 25px -5px rgba(244, 63, 94, 0.15)'
        }
      }}
    >
      {/* Top Accent Gradient Bar */}
      <Box sx={{
        height: 3,
        width: '100%',
        background: isBuy
          ? 'linear-gradient(90deg, #10b981, #00D1FF)'
          : 'linear-gradient(90deg, #f43f5e, #f59e0b)'
      }} />

      {/* 1. Header Zone */}
      <Box sx={{ p: 2.5, borderBottom: '1px solid rgba(255,255,255,0.05)', bgcolor: alpha(isBuy ? '#10b981' : '#f43f5e', 0.03) }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 950, color: '#f8fafc', letterSpacing: -0.5, fontFamily: 'JetBrains Mono, monospace' }}>
              {stock.symbol}
            </Typography>
            <Typography variant="caption" sx={{ color: '#cbd5e1', fontWeight: 600, display: 'block', mt: 0.2 }}>
              {stock.company_name || stock.name || 'INSTRUMENT'}
            </Typography>
          </Box>
          <Chip
            icon={isBuy ? <ArrowUpRight size={14} color="#10b981" /> : <ArrowDownRight size={14} color="#f43f5e" />}
            label={isBuy ? 'LONG ▲' : 'SHORT ▼'}
            size="small"
            sx={{
              fontWeight: 950,
              bgcolor: alpha(isBuy ? '#10b981' : '#f43f5e', 0.12),
              color: isBuy ? '#10b981' : '#f43f5e',
              border: `1px solid ${alpha(isBuy ? '#10b981' : '#f43f5e', 0.3)}`,
              borderRadius: 1,
              px: 0.5
            }}
          />
        </Box>

        {/* Confidence Progress Gauge */}
        <Box sx={{ mt: 2.5 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.8 }}>
            <Typography variant="caption" sx={{ color: '#cbd5e1', fontWeight: 700, fontSize: '0.65rem', letterSpacing: 0.8 }}>
              MODEL CONFIDENCE
            </Typography>
            <Typography variant="caption" sx={{ color: '#06b6d4', fontWeight: 950, fontFamily: 'JetBrains Mono, monospace', fontSize: '0.75rem' }}>
              {conviction}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={conviction}
            sx={{
              height: 6,
              borderRadius: 3,
              bgcolor: 'rgba(255,255,255,0.08)',
              '& .MuiLinearProgress-bar': {
                borderRadius: 3,
                bgcolor: conviction >= 80 ? '#10b981' : conviction >= 65 ? '#06b6d4' : '#f59e0b'
              }
            }}
          />
        </Box>
      </Box>

      {/* 2. Metric Price 2x2 Grid Zone */}
      <Box sx={{ p: 2.5, flexGrow: 1 }}>
        <Grid container spacing={2}>
          <PriceTile label="ENTRY" value={entry} />
          <PriceTile label="CURRENT" value={current} color={(current && entry) ? (current >= entry ? '#10b981' : '#f43f5e') : '#f8fafc'} />
          <PriceTile label="TARGET" value={target} color="#10b981" />
          <PriceTile label="STOP LOSS" value={stop} color="#f43f5e" />
        </Grid>

        {/* Execution Guidance Banner */}
        <Box sx={{ mt: 2.5 }}>
          {decision.status === 'ENTRY_TRIGGERED' ? (
            <Box sx={{ p: 1.2, bgcolor: alpha('#10b981', 0.1), borderRadius: 1, border: '1px solid rgba(16, 185, 129, 0.25)' }}>
              <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 950, display: 'flex', alignItems: 'center', gap: 0.8, fontSize: '0.65rem' }}>
                🟢 ENTRY TRIGGERED — BUY NOW
              </Typography>
            </Box>
          ) : decision.status === 'WAITING_FOR_ENTRY' ? (
            <Box sx={{ p: 1.2, bgcolor: alpha('#f59e0b', 0.1), borderRadius: 1, border: '1px solid rgba(245, 158, 11, 0.25)' }}>
              <Typography variant="caption" sx={{ color: '#f59e0b', fontWeight: 950, display: 'flex', alignItems: 'center', gap: 0.8, fontSize: '0.65rem' }}>
                🟡 WAITING FOR ENTRY — DO NOT BUY YET
              </Typography>
            </Box>
          ) : (
            <Box sx={{ p: 1.2, bgcolor: alpha('#06b6d4', 0.1), borderRadius: 1, border: '1px solid rgba(6, 182, 212, 0.25)' }}>
              <Typography variant="caption" sx={{ color: '#06b6d4', fontWeight: 950, display: 'flex', alignItems: 'center', gap: 0.8, fontSize: '0.65rem' }}>
                🔵 TRADE IN PROGRESS — ACTIVE
              </Typography>
            </Box>
          )}
        </Box>

        {/* Evidence Summary Clamped Text Block */}
        <Box sx={{ mt: 2, p: 1.8, bgcolor: 'rgba(2, 6, 23, 0.6)', borderRadius: 1, border: '1px solid rgba(255, 255, 255, 0.05)' }}>
          <Typography variant="caption" sx={{ color: '#cbd5e1', fontWeight: 800, display: 'block', mb: 0.5, fontSize: '0.6rem', letterSpacing: 0.5 }}>
            EVIDENCE SUMMARY
          </Typography>
          <Typography variant="caption" sx={{ color: '#f8fafc', fontWeight: 600, fontSize: '0.7rem', lineHeight: 1.4, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'orient', overflow: 'hidden' }}>
            {decision.formattedThesis?.trend || 'Bullish structure detected'} · {decision.formattedThesis?.momentum || 'Strong directional momentum'}
          </Typography>
        </Box>
      </Box>

      {/* 3. Card Footer Zone */}
      <Box sx={{ px: 2.5, py: 1.8, bgcolor: 'rgba(2, 6, 23, 0.4)', borderTop: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Stack direction="row" spacing={1} alignItems="center">
          <Clock size={12} color="#cbd5e1" />
          <Typography variant="caption" sx={{ color: '#cbd5e1', fontWeight: 700, fontSize: '0.65rem' }}>
            AGE: {decision.signalAgeHours ? `${decision.signalAgeHours.toFixed(1)}H` : 'FRESH'}
          </Typography>
        </Stack>

        <Stack direction="row" spacing={1.5} alignItems="center">
          <Tooltip title={copied ? "Signal Link Copied!" : "Copy Signal Link"}>
            <IconButton size="small" onClick={handleCopyLink} sx={{ color: copied ? '#10b981' : '#708090', p: 0.5, '&:hover': { color: '#00D1FF' } }}>
              {copied ? <Check size={13} /> : <Share2 size={13} />}
            </IconButton>
          </Tooltip>
          <Button
            size="small"
            startIcon={<Calculator size={12} color="#00D1FF" />}
            onClick={() => setIsCalcOpen(true)}
            sx={{ color: '#00D1FF', fontWeight: 800, fontSize: '0.65rem', textTransform: 'none', p: 0 }}
          >
            Sizer
          </Button>
          <Button
            size="small"
            onClick={() => navigate(`/signals/${decision.id}`, { state: { signal: stock, decision } })}
            sx={{
              color: '#06b6d4',
              fontWeight: 950,
              fontSize: '0.65rem',
              textTransform: 'none',
              p: 0,
              '&:hover': { bgcolor: 'transparent', color: '#38bdf8' }
            }}
          >
            View Evidence →
          </Button>
        </Stack>
      </Box>

      {/* 4. Position Sizer Risk Calculator Modal */}
      <Dialog open={isCalcOpen} onClose={() => setIsCalcOpen(false)} maxWidth="xs" fullWidth PaperProps={{ sx: { bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', color: '#fff' } }}>
         <DialogTitle sx={{ fontWeight: 950, color: '#fff', fontSize: '0.95rem' }}>
            POSITION RISK SIZER — {stock.symbol}
         </DialogTitle>
         <DialogContent>
            <Stack spacing={2.5} sx={{ mt: 1 }}>
               <TextField
                  label="Account Capital (₹)"
                  type="number"
                  size="small"
                  value={accountCapital}
                  onChange={(e) => setAccountCapital(Number(e.target.value) || 0)}
                  InputProps={{ startAdornment: <InputAdornment position="start" sx={{ color: '#708090' }}>₹</InputAdornment> }}
                  sx={{ bgcolor: 'rgba(0,0,0,0.2)' }}
               />
               <TextField
                  label="Max Trade Risk (%)"
                  type="number"
                  size="small"
                  value={riskPct}
                  onChange={(e) => setRiskPct(Number(e.target.value) || 0)}
                  InputProps={{ endAdornment: <InputAdornment position="end" sx={{ color: '#708090' }}>%</InputAdornment> }}
                  sx={{ bgcolor: 'rgba(0,0,0,0.2)' }}
               />

               <Paper sx={{ p: 2, bgcolor: 'rgba(0, 209, 255, 0.03)', border: '1px solid rgba(0, 209, 255, 0.15)', borderRadius: 1 }}>
                  <Stack spacing={1.2}>
                     <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption" sx={{ color: '#708090', fontWeight: 800 }}>Max Rupee Risk</Typography>
                        <Typography variant="caption" sx={{ fontWeight: 950, color: '#ef4444', fontFamily: 'JetBrains Mono' }}>
                           ₹{((accountCapital * riskPct) / 100.0).toLocaleString()}
                        </Typography>
                     </Box>
                     <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption" sx={{ color: '#708090', fontWeight: 800 }}>Risk / Share</Typography>
                        <Typography variant="caption" sx={{ fontWeight: 950, color: '#fff', fontFamily: 'JetBrains Mono' }}>
                           ₹{Math.abs((entry || 1000) - (stop || 950)).toFixed(2)}
                        </Typography>
                     </Box>
                     <Divider sx={{ opacity: 0.1, my: 0.5 }} />
                     <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="subtitle2" sx={{ color: '#00D1FF', fontWeight: 950 }}>SUGGESTED QTY</Typography>
                        <Typography variant="h6" sx={{ fontWeight: 950, color: '#10b981', fontFamily: 'JetBrains Mono' }}>
                           {Math.abs((entry || 1000) - (stop || 950)) > 0
                              ? Math.floor(((accountCapital * riskPct) / 100.0) / Math.abs((entry || 1000) - (stop || 950))).toLocaleString()
                              : '0'} SHS
                        </Typography>
                     </Box>
                     <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption" sx={{ color: '#708090', fontWeight: 800 }}>Trade Value Required</Typography>
                        <Typography variant="caption" sx={{ fontWeight: 950, color: '#fff', fontFamily: 'JetBrains Mono' }}>
                           ₹{(
                              (Math.abs((entry || 1000) - (stop || 950)) > 0
                                 ? Math.floor(((accountCapital * riskPct) / 100.0) / Math.abs((entry || 1000) - (stop || 950)))
                                 : 0) * (entry || 1000)
                           ).toLocaleString()}
                        </Typography>
                     </Box>
                  </Stack>
               </Paper>
            </Stack>
         </DialogContent>
         <DialogActions sx={{ p: 2.5 }}>
            <Button onClick={() => setIsCalcOpen(false)} sx={{ color: '#00D1FF', fontWeight: 950 }}>Close</Button>
         </DialogActions>
      </Dialog>
    </Paper>
  );
}

function PriceTile({ label, value, color = '#f8fafc' }: { label: string; value?: number; color?: string }) {
  return (
    <Grid item xs={6}>
      <Box sx={{ p: 1.5, bgcolor: 'rgba(2, 6, 23, 0.5)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.03)' }}>
        <Typography variant="caption" sx={{ color: '#cbd5e1', fontWeight: 700, fontSize: '0.6rem', display: 'block', mb: 0.3, letterSpacing: 0.5 }}>
          {label}
        </Typography>
        <Typography variant="body2" sx={{ fontWeight: 950, fontFamily: 'JetBrains Mono, monospace', color, fontSize: '0.85rem' }}>
          {value ? `₹${value.toLocaleString()}` : '—'}
        </Typography>
      </Box>
    </Grid>
  );
}
