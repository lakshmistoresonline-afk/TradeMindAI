import { useState, useEffect } from 'react';
import { Box, Typography, Grid, Paper, Stack, Divider, Button } from '@mui/material';
import { TrendingUp, AlertTriangle } from 'lucide-react';
import { getEquityAccuracy } from '../api/client';

const EMPTY_PERFORMANCE = {
  verified_benchmark: {
    n: 0,
    win_rate: 0.0,
    profit_factor: 0.0,
    net_pnl: 0.0
  },
  horizons: {
    SWING: { sample_size: 0, win_rate: 0.0, auc: 0.0, brier: 0.0, logloss: 0.0, ece: 0.0 },
    LONG:  { sample_size: 0, win_rate: 0.0, auc: 0.0, brier: 0.0, logloss: 0.0, ece: 0.0 },
    SHORT: { sample_size: 0, win_rate: 0.0, auc: 0.0, brier: 0.0, logloss: 0.0, ece: 0.0 }
  }
};

export default function Performance() {
  const [summary, setSummary] = useState<any>(EMPTY_PERFORMANCE);
  const [error, setError] = useState(false);

  useEffect(() => {
    getEquityAccuracy()
      .then((data: any) => {
        if (data && data.verified_benchmark) {
          setSummary(data);
        } else {
          setError(true);
        }
      })
      .catch((err) => {
        console.error("Failed to fetch authoritative performance:", err);
        setError(true);
      });
  }, []);

  return (
    <Box sx={{ pb: { xs: 14, md: 10 }, bgcolor: '#020617', minHeight: '100vh', px: { xs: 2, sm: 4 }, pt: 2, boxSizing: 'border-box' }}>
      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1, color: '#fff' }}>OBSERVED SIGNAL PERFORMANCE</Typography>
        <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 800, letterSpacing: 1.5, display: 'block', mt: 0.5 }}>
           AUTHORITATIVE HISTORICAL PERFORMANCE • STRATEGY V3.3
        </Typography>
      </Box>

      {error || summary.verified_benchmark.n === 0 ? (
        <Paper sx={{ p: 6, textAlign: 'center', bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)' }}>
          <AlertTriangle size={40} color="#f59e0b" style={{ margin: '0 auto 16px' }} />
          <Typography variant="h6" sx={{ color: '#fff', fontWeight: 900, mb: 1 }}>Insufficient Evidence or Backend Unavailable</Typography>
          <Typography variant="body2" sx={{ color: '#94a3b8', mb: 3 }}>Authoritative backend performance metrics are currently unavailable or sample size is zero.</Typography>
          <Button variant="outlined" onClick={() => window.location.reload()} sx={{ color: '#00D1FF', borderColor: '#00D1FF' }}>Retry Connection</Button>
        </Paper>
      ) : (
        <Box sx={{ mb: 8 }}>
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
            <TrendingUp size={20} color="#00D1FF" />
            <Typography variant="h6" sx={{ fontWeight: 950, color: '#00D1FF', letterSpacing: 0.5 }}>PRODUCTION SIGNAL BENCHMARK</Typography>
            <Divider sx={{ flexGrow: 1, opacity: 0.08, bgcolor: '#00D1FF' }} />
         </Stack>
         <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.06)' }}>
                <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 800 }}>VERIFIED SAMPLE SIZE (n)</Typography>
                <Typography variant="h4" sx={{ fontWeight: 950, color: '#fff', mt: 1 }}>{summary.verified_benchmark.n}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.06)' }}>
                <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 800 }}>WIN RATE</Typography>
                <Typography variant="h4" sx={{ fontWeight: 950, color: '#10b981', mt: 1 }}>{summary.verified_benchmark.win_rate}%</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.06)' }}>
                <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 800 }}>PROFIT FACTOR</Typography>
                <Typography variant="h4" sx={{ fontWeight: 950, color: '#00D1FF', mt: 1 }}>{summary.verified_benchmark.profit_factor}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.06)' }}>
                <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 800 }}>NET RETURN</Typography>
                <Typography variant="h4" sx={{ fontWeight: 950, color: summary.verified_benchmark.net_pnl >= 0 ? '#10b981' : '#ef4444', mt: 1 }}>
                  {summary.verified_benchmark.net_pnl >= 0 ? '+' : ''}{summary.verified_benchmark.net_pnl}%
                </Typography>
              </Paper>
            </Grid>
         </Grid>
        </Box>
      )}
    </Box>
  );
}
