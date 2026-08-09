import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Card, CardContent, CircularProgress, Stack } from '@mui/material';
import { TrendingUp, ArrowUpRight, CheckCircle, XCircle, History, Activity } from 'lucide-react';
import { apiClient } from '../../api/client';

export default function SignalValidation() {
  const [signals, setSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>({
    avgWinRate: 0,
    avgProfit: 0,
    totalSignals: 0,
    targetHitRate: 0,
    stopLossRate: 0
  });

  useEffect(() => {
    const fetchPerformance = async () => {
      try {
        const response = await apiClient.get('/analysis/performance/audit');
        const data = response.data;
        setSignals(data);

        const total = data.length;
        if (total > 0) {
          const successCount = data.filter((s: any) => s.outcome === 'TARGET_HIT').length;
          const stopLossCount = data.filter((s: any) => s.outcome === 'STOP_LOSS').length;
          const avgProfit = data.reduce((acc: number, s: any) => acc + s.profit_pct, 0) / total;

          setStats({
            avgWinRate: (successCount / total) * 100,
            avgProfit: avgProfit,
            totalSignals: total,
            targetHitRate: (successCount / total) * 100,
            stopLossRate: (stopLossCount / total) * 100
          });
        }
      } catch (error) {
        console.error("Error fetching performance audit:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchPerformance();
  }, []);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 8 }}><CircularProgress /></Box>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
         <Typography variant="h4" sx={{ fontWeight: 900 }}>Signal Validation</Typography>
         <Chip icon={<Activity size={14} />} label="LIVE PERFORMANCE AUDIT" color="primary" variant="outlined" sx={{ fontWeight: 800 }} />
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ bgcolor: 'primary.main', color: 'black' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 800 }}>VALIDATED SIGNALS</Typography>
                <History size={20} />
              </Box>
              <Typography variant="h4" fontWeight={900}>{stats.totalSignals}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle2">AVERAGE VALIDATED P&L</Typography>
                <TrendingUp size={20} className="text-emerald-500" />
              </Box>
              <Typography variant="h4" fontWeight={900} color="primary">+{stats.avgProfit.toFixed(2)}%</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle2">VALIDATION ACCURACY</Typography>
                <ArrowUpRight size={20} className="text-blue-500" />
              </Box>
              <Typography variant="h4" fontWeight={900}>{stats.avgWinRate.toFixed(1)}%</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="textSecondary">HIT/STOP RATIO</Typography>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1 }}>
                 <Typography variant="h5" fontWeight={900} color="primary">{Math.round(stats.targetHitRate)}%</Typography>
                 <Typography variant="caption" color="textSecondary">/</Typography>
                 <Typography variant="h5" fontWeight={900} color="error">{Math.round(stats.stopLossRate)}%</Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" fontWeight={800} gutterBottom>Historical Signal Validation Log</Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3, fontWeight: 500 }}>
          Every signal below is cross-referenced with actual price action to verify model prediction accuracy.
        </Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Symbol</TableCell>
                <TableCell align="right">Entry</TableCell>
                <TableCell align="right">Target</TableCell>
                <TableCell align="right">Stop Loss</TableCell>
                <TableCell align="right">Outcome P&L</TableCell>
                <TableCell align="center">Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {signals.length > 0 ? signals.map((sig, idx) => (
                <TableRow key={`${sig.symbol}-${idx}`} hover>
                  <TableCell sx={{ color: 'text.secondary', fontWeight: 600 }}>{sig.date}</TableCell>
                  <TableCell sx={{ fontWeight: 900 }}>{sig.symbol}</TableCell>
                  <TableCell align="right" sx={{ fontFamily: 'JetBrains Mono' }}>₹{sig.entry?.toLocaleString()}</TableCell>
                  <TableCell align="right" sx={{ color: 'primary.main', fontWeight: 700, fontFamily: 'JetBrains Mono' }}>₹{sig.target?.toLocaleString()}</TableCell>
                  <TableCell align="right" sx={{ color: 'error.main', fontWeight: 700, fontFamily: 'JetBrains Mono' }}>₹{sig.stop_loss?.toLocaleString()}</TableCell>
                  <TableCell align="right" sx={{ color: sig.profit_pct >= 0 ? 'primary.main' : 'error.main', fontWeight: 900, fontFamily: 'JetBrains Mono' }}>
                    {sig.profit_pct >= 0 ? '+' : ''}{sig.profit_pct.toFixed(2)}%
                  </TableCell>
                  <TableCell align="center">
                    {sig.outcome === 'TARGET_HIT' ? (
                      <Chip icon={<CheckCircle size={14} />} label="TARGET HIT" color="success" size="small" sx={{ fontWeight: 900, borderRadius: 1 }} />
                    ) : sig.outcome === 'STOP_LOSS' ? (
                      <Chip icon={<XCircle size={14} />} label="STOP LOSS" color="error" size="small" sx={{ fontWeight: 900, borderRadius: 1 }} />
                    ) : (
                      <Chip label="EXPIRED" size="small" sx={{ fontWeight: 900, borderRadius: 1 }} />
                    )}
                  </TableCell>
                </TableRow>
              )) : (
                <TableRow>
                   <TableCell colSpan={7} align="center" sx={{ py: 8 }}>
                      <Typography variant="body2" color="textSecondary">No signals have been validated yet. Run adhoc analysis to generate data.</Typography>
                   </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
