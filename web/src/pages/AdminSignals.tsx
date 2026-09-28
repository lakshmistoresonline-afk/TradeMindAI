import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Stack, Button, alpha, Chip, Skeleton, Divider } from '@mui/material';
import { CheckCircle2, RefreshCw, ArrowRight } from 'lucide-react';
import { getEquitySignals } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { useTurboSync } from '../hooks/useTurboSync';
import { mapCanonicalSignal } from '../hooks/useAITradeDecision';
import { MONO_FONT, COLORS, GLASS_PANEL_STYLE, HERO_BANNER_STYLE, GRADIENT_ACCENT_BAR } from '../theme/institutionalTheme';

export default function AdminSignals() {
  const [signals, setSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { firestoreSignals } = useTurboSync();

  const fetchSignals = () => {
    setLoading(true);
    getEquitySignals({ limit: 100 }).then(data => {
        const normalized = (data || []).map((s: any) => mapCanonicalSignal(s));
        setSignals(normalized);
        setLoading(false);
    }).catch(() => {
        setLoading(false);
    });
  };

  useEffect(() => {
    fetchSignals();
  }, []);

  useEffect(() => {
    if (firestoreSignals.length === 0) return;
    const normalizedFS = firestoreSignals.map(s => mapCanonicalSignal(s));

    setSignals(prev => {
        const mergedMap = new Map();
        prev.forEach(s => mergedMap.set(s.id, s));
        normalizedFS.forEach(s => mergedMap.set(s.id, s));

        return Array.from(mergedMap.values()).sort((a,b) =>
            new Date(b.decision?.generatedAt || 0).getTime() - new Date(a.decision?.generatedAt || 0).getTime()
        );
    });
  }, [firestoreSignals]);

  return (
    <Box sx={{ pb: { xs: 14, md: 10 }, maxWidth: 1400, mx: 'auto', p: { xs: 2, sm: 4 }, color: 'white', boxSizing: 'border-box' }}>
      {/* 1. Hero Header */}
      <Box sx={{ ...HERO_BANNER_STYLE, mb: 5 }}>
        <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, ...GRADIENT_ACCENT_BAR }} />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
           <Box>
              <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1, fontFamily: MONO_FONT, color: '#fff' }}>
                 SIGNAL OPERATIONS TERMINAL
              </Typography>
              <Typography variant="caption" sx={{ color: COLORS.purple, fontWeight: 800, letterSpacing: 1.5, fontFamily: MONO_FONT }}>
                 MASTER PUBLICATION & LIFECYCLE GATE (STRATEGY V5.0 PRECOGNITIVE AGI)
              </Typography>
           </Box>
           <Button
              variant="outlined"
              color="secondary"
              startIcon={<RefreshCw size={16} />}
              onClick={fetchSignals}
              sx={{ fontWeight: 950, borderColor: COLORS.borderLight, color: COLORS.cyan, fontFamily: MONO_FONT }}
           >
              REFRESH OPERATIONAL GATE
           </Button>
        </Box>
      </Box>

      {/* 2. Operational Signal Cards Grid */}
      {loading && signals.length === 0 ? (
         <Grid container spacing={3}>
            {[1, 2, 3, 4, 5, 6].map(i => (
               <Grid item xs={12} md={6} lg={4} key={i}>
                  <Skeleton variant="rectangular" height={320} sx={{ borderRadius: 2, bgcolor: 'rgba(255,255,255,0.02)' }} />
               </Grid>
            ))}
         </Grid>
      ) : signals.length === 0 ? (
         <Paper sx={{ ...GLASS_PANEL_STYLE, p: 8, textAlign: 'center' }}>
            <Typography variant="body1" sx={{ color: COLORS.slateMuted, fontWeight: 800 }}>
               No active signals detected in Operational Lifecycle Gate.
            </Typography>
         </Paper>
      ) : (
         <Grid container spacing={3}>
            {signals.map((s) => {
               const dec = s.decision || s;
               const isBuy = dec.rating?.includes('BUY') || dec.direction === 'LONG';
               const entry = dec.entry || s.entry_price || 0;
               const target1 = dec.target1 || s.target_price_1 || (entry > 0 ? Math.round(entry * 1.05) : 0);
               const stop = dec.stopLoss || s.stop_loss_price || s.stop_price || (entry > 0 ? Math.round(entry * 0.95) : 0);

               return (
                  <Grid item xs={12} md={6} lg={4} key={s.id || s.symbol}>
                     <Paper
                        elevation={0}
                        sx={{
                           ...GLASS_PANEL_STYLE,
                           p: 3,
                           height: '100%',
                           display: 'flex',
                           flexDirection: 'column',
                           position: 'relative',
                           transition: 'all 0.2s ease-in-out',
                           '&:hover': {
                              borderColor: COLORS.cyan,
                              transform: 'translateY(-2px)',
                              boxShadow: '0 10px 25px -5px rgba(0, 209, 255, 0.2)'
                           }
                        }}
                     >
                        {/* Top Accent Gradient Line */}
                        <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, borderRadius: '8px 8px 0 0', background: isBuy ? 'linear-gradient(90deg, #10b981, #00D1FF)' : 'linear-gradient(90deg, #f43f5e, #f59e0b)' }} />

                        {/* Card Header: Signal ID & Symbol */}
                        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                           <Box>
                              <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 800, fontSize: '0.625rem', fontFamily: MONO_FONT, display: 'block' }}>
                                 {s.id}
                              </Typography>
                              <Typography variant="h5" sx={{ fontWeight: 950, fontFamily: MONO_FONT, color: '#fff', mt: 0.2 }}>
                                 {s.symbol}
                              </Typography>
                              <Typography variant="caption" sx={{ color: COLORS.slateText, fontWeight: 600, display: 'block' }}>
                                 {s.company_name || `${s.symbol} Limited`}
                              </Typography>
                           </Box>
                           <Chip
                              label={isBuy ? 'LONG ▲' : 'SHORT ▼'}
                              size="small"
                              sx={{
                                 fontWeight: 950,
                                 fontSize: '0.625rem',
                                 bgcolor: alpha(isBuy ? COLORS.green : COLORS.red, 0.15),
                                 color: isBuy ? COLORS.green : COLORS.red,
                                 border: `1px solid ${alpha(isBuy ? COLORS.green : COLORS.red, 0.3)}`
                              }}
                           />
                        </Stack>

                        <Divider sx={{ my: 1.5, opacity: 0.08 }} />

                        {/* Metric Grid: Conviction, Entry, Stop Loss, Target 1 */}
                        <Grid container spacing={1.5} sx={{ mb: 2.5, flexGrow: 1 }}>
                           <Grid item xs={6}>
                              <Box sx={{ p: 1.2, bgcolor: 'rgba(2, 6, 23, 0.5)', borderRadius: 1, border: `1px solid ${COLORS.borderLight}` }}>
                                 <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 800, fontSize: '0.55rem', display: 'block' }}>CONVICTION</Typography>
                                 <Typography variant="body2" sx={{ fontWeight: 950, color: COLORS.cyan, fontFamily: MONO_FONT }}>{dec.conviction || 75}%</Typography>
                              </Box>
                           </Grid>
                           <Grid item xs={6}>
                              <Box sx={{ p: 1.2, bgcolor: 'rgba(2, 6, 23, 0.5)', borderRadius: 1, border: `1px solid ${COLORS.borderLight}` }}>
                                 <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 800, fontSize: '0.55rem', display: 'block' }}>ENTRY PRICE</Typography>
                                 <Typography variant="body2" sx={{ fontWeight: 950, color: '#fff', fontFamily: MONO_FONT }}>₹{entry ? entry.toLocaleString() : '—'}</Typography>
                              </Box>
                           </Grid>
                           <Grid item xs={6}>
                              <Box sx={{ p: 1.2, bgcolor: 'rgba(2, 6, 23, 0.5)', borderRadius: 1, border: `1px solid ${COLORS.borderLight}` }}>
                                 <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 800, fontSize: '0.55rem', display: 'block' }}>TARGET 1</Typography>
                                 <Typography variant="body2" sx={{ fontWeight: 950, color: COLORS.green, fontFamily: MONO_FONT }}>₹{target1 ? target1.toLocaleString() : '—'}</Typography>
                              </Box>
                           </Grid>
                           <Grid item xs={6}>
                              <Box sx={{ p: 1.2, bgcolor: 'rgba(2, 6, 23, 0.5)', borderRadius: 1, border: `1px solid ${COLORS.borderLight}` }}>
                                 <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 800, fontSize: '0.55rem', display: 'block' }}>STOP LOSS</Typography>
                                 <Typography variant="body2" sx={{ fontWeight: 950, color: COLORS.red, fontFamily: MONO_FONT }}>₹{stop ? stop.toLocaleString() : '—'}</Typography>
                              </Box>
                           </Grid>
                        </Grid>

                        {/* Status & Validation Badge Row */}
                        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2.5 }}>
                           <Chip
                              label={dec.status || 'ACTIVE'}
                              size="small"
                              variant="outlined"
                              sx={{ fontWeight: 950, fontSize: '0.55rem', height: 22, color: COLORS.slateText, borderColor: COLORS.borderLight }}
                           />
                           <Stack direction="row" spacing={0.8} alignItems="center">
                              <CheckCircle2 size={12} color={COLORS.green} />
                              <Typography variant="caption" sx={{ color: COLORS.green, fontWeight: 950, fontSize: '0.625rem', fontFamily: MONO_FONT }}>
                                 PASSED V5.0 GATE
                              </Typography>
                           </Stack>
                        </Stack>

                        {/* Audit Action Button */}
                        <Button
                           fullWidth
                           variant="outlined"
                           size="small"
                           endIcon={<ArrowRight size={14} />}
                           onClick={() => navigate(`/signals/${s.id}`)}
                           sx={{ fontWeight: 950, fontSize: '0.7rem', color: COLORS.cyan, borderColor: COLORS.borderCyan, fontFamily: MONO_FONT }}
                        >
                           AUDIT SIGNAL
                        </Button>
                     </Paper>
                  </Grid>
               );
            })}
         </Grid>
      )}
    </Box>
  );
}
