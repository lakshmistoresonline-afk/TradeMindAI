import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Table, TableBody, TableCell, TableHead, TableRow, CircularProgress, Stack } from '@mui/material';
import { Activity, ShieldCheck } from 'lucide-react';
import { getCorrelations, getPortfolioHedge } from '../../../api/client';

export default function CorrelationEngine({ symbol }: { symbol: string }) {
  const [correlations, setCorrelations] = useState<any[]>([]);
  const [hedge, setHedge] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (symbol) {
      setLoading(true);
      Promise.all([
        getCorrelations(symbol),
        getPortfolioHedge()
      ]).then(([corrData, hedgeData]) => {
        setCorrelations(corrData);
        setHedge(hedgeData);
      })
      .catch(err => console.error("Correlation Error:", err))
      .finally(() => setLoading(false));
    }
  }, [symbol]);

  const getHeatmapColor = (val: number) => {
    if (val > 0.7) return '#064e3b';
    if (val > 0.4) return '#065f46';
    if (val < -0.3) return '#7f1d1d';
    return '#1e293b';
  };

  if (loading) return <Box sx={{ py: 4, textAlign: 'center' }}><CircularProgress size={24} /></Box>;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Activity size={20} className="text-purple-400" /> AI Correlation Engine
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 0, overflow: 'hidden' }}>
            <Table size="small">
              <TableHead sx={{ bgcolor: 'rgba(255,255,255,0.02)' }}>
                <TableRow>
                  <TableCell>Asset / Index</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell align="right">Correlation</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {correlations.map((c) => (
                  <TableRow key={c.target} hover>
                    <TableCell sx={{ py: 2, fontWeight: 'bold' }}>{c.target}</TableCell>
                    <TableCell sx={{ color: 'text.secondary' }}>{c.type}</TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'inline-block', px: 1.5, py: 0.5, borderRadius: 1, bgcolor: getHeatmapColor(c.value), fontWeight: 'bold' }}>
                         {c.value.toFixed(2)}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Grid>

        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, height: '100%', bgcolor: 'rgba(15, 23, 42, 0.3)' }}>
             <Typography variant="subtitle2" color="textSecondary" gutterBottom>CO-MOVEMENT ANALYSIS</Typography>
             {correlations.length > 0 ? (
               <Typography variant="body2" sx={{ lineHeight: 1.7, mt: 2 }}>
                  {symbol} shows a **{correlations[0].value > 0.7 ? 'very high' : 'moderate'} positive correlation ({correlations[0].value.toFixed(2)})** with {correlations[0].target}.
                  This suggests it acts as a {correlations[0].value > 0.8 ? 'beta leader' : 'market follower'} in current session.
               </Typography>
             ) : (
               <Typography variant="body2" sx={{ mt: 2, color: 'slategray' }}>Gathering cross-asset covariance data...</Typography>
             )}

             {hedge && hedge.recommendation !== "NONE" ? (
                <Box sx={{ mt: 3, p: 2, bgcolor: 'rgba(16, 185, 129, 0.05)', border: '1px dashed #10b981', borderRadius: 2 }}>
                   <Stack direction="row" spacing={1} alignItems="center" mb={1}>
                      <ShieldCheck size={16} className="text-emerald-500" />
                      <Typography variant="caption" color="primary" fontWeight="bold">DYNAMIC HEDGING ACTIVE</Typography>
                   </Stack>
                   <Typography variant="body2" sx={{ fontWeight: 600 }}>{hedge.recommendation.replace('_', ' ')}</Typography>
                   <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'text.secondary' }}>
                      Suggested: **{hedge.suggested_lots} Lots** of **{hedge.hedge_asset} Puts**.
                   </Typography>
                   <Typography variant="caption" sx={{ display: 'block', mt: 0.5, fontStyle: 'italic' }}>
                      {hedge.reasoning}
                   </Typography>
                </Box>
             ) : (
                <Box sx={{ mt: 3, p: 2, border: '1px dashed #334155', borderRadius: 2, opacity: 0.6 }}>
                   <Typography variant="caption" color="primary" fontWeight="bold">HEDGING TIP</Typography>
                   <Typography variant="body2">Current portfolio beta suggests no immediate tail-risk protection is required.</Typography>
                </Box>
             )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
