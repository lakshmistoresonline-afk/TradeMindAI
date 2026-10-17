import { useState, useEffect } from 'react';
import { Box, Typography, Grid, Paper, Stack, Divider, Button, Chip, alpha } from '@mui/material';
import { TrendingUp, AlertTriangle, ShieldAlert } from 'lucide-react';
import { getEquityAccuracy } from '../api/client';
import { MONO_FONT, COLORS, GLASS_PANEL_STYLE } from '../theme/institutionalTheme';

const EMPTY_PERFORMANCE = {
  verified_benchmark: {
    n: 0,
    verified_n: 0,
    unverified_shadow_n: 0,
    win_rate: null,
    profit_factor: null,
    net_pnl: null,
    status: 'INSUFFICIENT_EVIDENCE'
  },
  horizons: {
    SWING: { sample_size: 0, win_rate: null, profit_factor: null, net_pnl: null, status: 'INSUFFICIENT_EVIDENCE' },
    LONG:  { sample_size: 0, win_rate: null, profit_factor: null, net_pnl: null, status: 'INSUFFICIENT_EVIDENCE' },
    SHORT: { sample_size: 0, win_rate: null, profit_factor: null, net_pnl: null, status: 'INSUFFICIENT_EVIDENCE' }
  }
};

export default function Performance() {
  const [summary, setSummary] = useState<any>(EMPTY_PERFORMANCE);
  const [error, setError] = useState(false);

  useEffect(() => {
    getEquityAccuracy()
      .then((data: any) => {
        if (data && data.verified_benchmark && (data.verified_benchmark.n > 0 || data.verified_benchmark.verified_n > 0)) {
          setSummary(data);
        } else {
          setSummary(EMPTY_PERFORMANCE);
        }
      })
      .catch((err) => {
        console.error("Failed to fetch authoritative performance:", err);
        setError(true);
        setSummary(EMPTY_PERFORMANCE);
      });
  }, []);

  const benchmark = summary.verified_benchmark || EMPTY_PERFORMANCE.verified_benchmark;
  const horizons = summary.horizons || EMPTY_PERFORMANCE.horizons;
  const verifiedCount = benchmark.verified_n ?? 0;
  const totalCount = benchmark.n ?? 0;
  const benchmarkStatus = benchmark.status || 'INSUFFICIENT_EVIDENCE';
  const isVerified = benchmarkStatus === 'VERIFIED' && verifiedCount > 0;

  return (
    <Box sx={{ pb: { xs: 14, md: 10 }, bgcolor: '#020617', minHeight: '100vh', px: { xs: 2, sm: 4 }, pt: 2, boxSizing: 'border-box' }}>
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1, color: COLORS.textBright, fontFamily: MONO_FONT }}>
            HISTORICAL SIGNAL PERFORMANCE LEDGER
          </Typography>
          <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 800, letterSpacing: 1.5, display: 'block', mt: 0.5, fontFamily: MONO_FONT }}>
             HISTORICAL SIMULATION & PROVENANCE AUDIT • STRATEGY V2.2 (BUY-ONLY)
          </Typography>
        </Box>
        <Chip
           icon={<ShieldAlert size={14} />}
           label={isVerified ? "VERIFIED TRACK RECORD" : benchmarkStatus}
           color={isVerified ? "success" : "warning"}
           sx={{ fontWeight: 950, fontSize: '0.675rem' }}
        />
      </Box>

      {error || totalCount === 0 ? (
        <Paper sx={{ p: 6, textAlign: 'center', bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2 }}>
          <AlertTriangle size={40} color="#f59e0b" style={{ margin: '0 auto 16px' }} />
          <Typography variant="h6" sx={{ color: '#fff', fontWeight: 900, mb: 1 }}>Insufficient Evidence or Unverified State</Typography>
          <Typography variant="body2" sx={{ color: '#94a3b8', mb: 3 }}>Zero eligible verified live records found. Historical shadow simulations are unverified.</Typography>
          <Button variant="outlined" onClick={() => window.location.reload()} sx={{ color: '#00D1FF', borderColor: '#00D1FF' }}>Retry Connection</Button>
        </Paper>
      ) : (
        <Box sx={{ mb: 8 }}>
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
            <TrendingUp size={20} color={COLORS.cyan} />
            <Typography variant="h6" sx={{ fontWeight: 950, color: COLORS.cyan, letterSpacing: 0.5, fontFamily: MONO_FONT }}>
              BENCHMARK PERFORMANCE SUMMARY
            </Typography>
            <Divider sx={{ flexGrow: 1, opacity: 0.08, bgcolor: COLORS.cyan }} />
         </Stack>
         <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ ...GLASS_PANEL_STYLE, p: 3 }}>
                <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 950, letterSpacing: 1 }}>TOTAL EXAMINED (n)</Typography>
                <Typography variant="h4" sx={{ fontWeight: 950, color: COLORS.textBright, mt: 1, fontFamily: MONO_FONT }}>
                  {totalCount.toLocaleString()}
                </Typography>
                <Typography variant="caption" sx={{ color: verifiedCount > 0 ? COLORS.green : '#f59e0b', display: 'block', mt: 0.5, fontWeight: 800 }}>
                   Verified: {verifiedCount} | Unverified Shadow: {totalCount - verifiedCount}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ ...GLASS_PANEL_STYLE, p: 3 }}>
                <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 950, letterSpacing: 1 }}>WIN RATE</Typography>
                <Typography variant="h4" sx={{ fontWeight: 950, color: isVerified ? COLORS.green : '#f59e0b', mt: 1, fontFamily: MONO_FONT }}>
                  {benchmark.win_rate !== null && benchmark.win_rate !== undefined ? `${benchmark.win_rate}%` : 'N/A'}
                </Typography>
                <Typography variant="caption" sx={{ color: COLORS.slateMuted, display: 'block', mt: 0.5, fontWeight: 800 }}>
                   {isVerified ? 'Verified Win Rate' : 'Unverified Simulation'}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ ...GLASS_PANEL_STYLE, p: 3 }}>
                <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 950, letterSpacing: 1 }}>PROFIT FACTOR</Typography>
                <Typography variant="h4" sx={{ fontWeight: 950, color: COLORS.cyan, mt: 1, fontFamily: MONO_FONT }}>
                  {benchmark.profit_factor ?? 'N/A'}
                </Typography>
                <Typography variant="caption" sx={{ color: COLORS.slateMuted, display: 'block', mt: 0.5, fontWeight: 800 }}>
                   {isVerified ? 'Verified Profit Factor' : 'Unverified Simulation'}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ ...GLASS_PANEL_STYLE, p: 3 }}>
                <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 950, letterSpacing: 1 }}>CUMULATIVE RETURN</Typography>
                <Typography variant="h4" sx={{ fontWeight: 950, color: (benchmark.net_pnl ?? 0) >= 0 ? COLORS.green : COLORS.red, mt: 1, fontFamily: MONO_FONT }}>
                  {benchmark.net_pnl !== null && benchmark.net_pnl !== undefined ? `${benchmark.net_pnl >= 0 ? '+' : ''}${benchmark.net_pnl}%` : 'N/A'}
                </Typography>
                <Typography variant="caption" sx={{ color: '#f59e0b', display: 'block', mt: 0.5, fontWeight: 800 }}>
                   Arithmetic Sum (Not Portfolio Return)
                </Typography>
              </Paper>
            </Grid>
         </Grid>

         {!isVerified && (
           <Box sx={{ mt: 3, p: 2.5, bgcolor: alpha('#f59e0b', 0.05), border: `1px dashed ${alpha('#f59e0b', 0.4)}`, borderRadius: 2 }}>
              <Typography variant="caption" sx={{ color: '#f59e0b', display: 'block', fontWeight: 800, lineHeight: 1.5 }}>
                 ⚠️ PROVENANCE NOTICE: Eligible verified records = {verifiedCount} (insufficient live evidence). All {totalCount} evaluated records are classified as {benchmarkStatus}. Metrics are derived from unverified historical shadow simulations and arithmetic sum trade returns, not observed live forward performance.
              </Typography>
           </Box>
         )}

         {/* Horizon Breakdown */}
         <Box sx={{ mt: 6 }}>
            <Typography variant="h6" sx={{ fontWeight: 950, color: COLORS.textBright, mb: 3, fontFamily: MONO_FONT }}>
              HORIZON PERFORMANCE BREAKDOWN
            </Typography>
            <Grid container spacing={3}>
              {Object.entries(horizons).map(([hName, hData]: [string, any]) => (
                <Grid item xs={12} md={4} key={hName}>
                   <Paper sx={{ ...GLASS_PANEL_STYLE, p: 3, height: '100%' }}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                         <Typography variant="subtitle1" sx={{ fontWeight: 950, color: COLORS.cyan, fontFamily: MONO_FONT }}>
                            {hName} HORIZON
                         </Typography>
                         <Chip
                            label={hData.status || 'UNVERIFIED'}
                            size="small"
                            sx={{
                               bgcolor: hData.status === 'VERIFIED' ? alpha(COLORS.green, 0.12) : alpha('#f59e0b', 0.12),
                               color: hData.status === 'VERIFIED' ? COLORS.green : '#f59e0b',
                               fontWeight: 950,
                               fontSize: '0.6rem'
                            }}
                         />
                      </Stack>
                      <Stack spacing={2}>
                         <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" sx={{ color: COLORS.slateMuted, fontWeight: 800 }}>Sample Size:</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 950, fontFamily: MONO_FONT }}>{hData.sample_size ?? hData.n ?? 'N/A'}</Typography>
                         </Box>
                         <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" sx={{ color: COLORS.slateMuted, fontWeight: 800 }}>Win Rate:</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 950, color: COLORS.green, fontFamily: MONO_FONT }}>{hData.win_rate !== null && hData.win_rate !== undefined ? `${hData.win_rate}%` : 'N/A'}</Typography>
                         </Box>
                         <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" sx={{ color: COLORS.slateMuted, fontWeight: 800 }}>Profit Factor:</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 950, color: COLORS.cyan, fontFamily: MONO_FONT }}>{hData.profit_factor ?? 'N/A'}</Typography>
                         </Box>
                         <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" sx={{ color: COLORS.slateMuted, fontWeight: 800 }}>Net P&L Return:</Typography>
                            <Typography variant="body2" sx={{ fontWeight: 950, color: COLORS.green, fontFamily: MONO_FONT }}>{hData.net_pnl !== null && hData.net_pnl !== undefined ? `+${hData.net_pnl}%` : 'N/A'}</Typography>
                         </Box>
                      </Stack>
                   </Paper>
                </Grid>
              ))}
            </Grid>
         </Box>
        </Box>
      )}
    </Box>
  );
}
