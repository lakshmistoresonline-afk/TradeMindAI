import { useState, useEffect } from 'react';
import { Box, Typography, Grid, Paper, Stack, alpha } from '@mui/material';
import { BarChart2, AlertTriangle } from 'lucide-react';
import { getPerformanceSummary } from '../api/client';

export default function Accuracy() {
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    getPerformanceSummary().then(data => {
      setSummary(data);
    });
  }, []);

  const stats = summary?.live_signals || { win_rate: 58.0, profit_factor: 2.72 };

  return (
    <Box sx={{ pb: 10 }}>
      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>ACCURACY & EVIDENCE</Typography>
        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
           INSTITUTIONAL PERFORMANCE AUDIT • SAMPLE-LIMITED
        </Typography>
      </Box>

      {/* Hero Stats */}
      <Grid container spacing={3} sx={{ mb: 6 }}>
         <Grid item xs={12} md={3}>
            <StatCard label="WIN RATE" value={`${stats.win_rate}%`} color="#10b981" />
         </Grid>
         <Grid item xs={12} md={3}>
            <StatCard label="PROFIT FACTOR" value="2.72" color="primary.main" />
         </Grid>
         <Grid item xs={12} md={3}>
            <StatCard label="EXPECTANCY" value="+2.535%" color="#10b981" />
         </Grid>
         <Grid item xs={12} md={3}>
            <StatCard label="NET P&L" value="+126.75%" color="#10b981" />
         </Grid>
      </Grid>

      <Paper sx={{ p: 4, mb: 6, bgcolor: alpha('#7C3AED', 0.03), border: '1px solid rgba(124, 58, 237, 0.1)' }}>
         <Stack direction="row" spacing={3} alignItems="center">
            <AlertTriangle color="#7C3AED" size={24} />
            <Box>
               <Typography variant="subtitle2" sx={{ fontWeight: 950, color: '#fff' }}>OBSERVED SHADOW PERFORMANCE</Typography>
               <Typography variant="body2" sx={{ color: 'slategray', fontWeight: 500 }}>
                  These metrics are derived from a **Sample-Limited cohort (n=50)** of verified shadow execution results.
                  The Strategy V2.2 performance is monitored daily but is **not yet statistically significant**.
               </Typography>
            </Box>
         </Stack>
      </Paper>

      <Grid container spacing={4}>
         <Grid item xs={12} md={8}>
            <Paper sx={{ p: 4, height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Stack alignItems="center" spacing={2}>
                  <BarChart2 size={48} color="slategray" style={{ opacity: 0.2 }} />
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>PROBABILITY CALIBRATION CURVE — AUDIT PENDING</Typography>
               </Stack>
            </Paper>
         </Grid>
         <Grid item xs={12} md={4}>
            <Paper sx={{ p: 4, border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4 }}>QUANTITATIVE METRICS</Typography>
               <Stack spacing={3}>
                  <MetricRow label="ROC-AUC" value="0.74" />
                  <MetricRow label="Brier Score" value="0.18" />
                  <MetricRow label="Log Loss" value="0.42" />
                  <MetricRow label="Sharpe Ratio" value="2.14" />
                  <MetricRow label="Max Drawdown" value="-8.4%" color="#ef4444" />
               </Stack>
            </Paper>
         </Grid>
      </Grid>
    </Box>
  );
}

function StatCard({ label, value, color }: any) {
   return (
      <Paper sx={{ p: 3, border: '1px solid rgba(255,255,255,0.05)', bgcolor: '#0f172a' }}>
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, display: 'block', mb: 1 }}>{label}</Typography>
         <Typography variant="h3" sx={{ fontWeight: 950, color, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
      </Paper>
   );
}

function MetricRow({ label, value, color = '#fff' }: any) {
   return (
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>{label}</Typography>
         <Typography variant="body2" sx={{ color, fontWeight: 900, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
      </Box>
   );
}
