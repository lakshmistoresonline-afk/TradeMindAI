import { Box, Typography, Paper, Grid, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';
import { Activity } from 'lucide-react';

export default function CorrelationEngine({ symbol }: { symbol: string }) {
  const correlations = [
    { target: 'Nifty 50', value: 0.82, type: 'MARKET' },
    { target: 'USDINR', value: -0.45, type: 'CURRENCY' },
    { target: 'IT Sector', value: 0.94, type: 'SECTOR' },
    { target: 'Crude Oil', value: 0.12, type: 'COMMODITY' },
  ];

  const getHeatmapColor = (val: number) => {
    if (val > 0.8) return '#064e3b';
    if (val > 0.5) return '#065f46';
    if (val < -0.3) return '#7f1d1d';
    return '#1e293b';
  };

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
             <Typography variant="body2" sx={{ lineHeight: 1.7, mt: 2 }}>
                {symbol} shows a **very high positive correlation (0.94)** with its sector, indicating it moves in lockstep with industry trends.
                The **negative USDINR correlation** suggests the company benefits from INR appreciation (or is sensitive to depreciation).
             </Typography>
             <Box sx={{ mt: 3, p: 2, border: '1px dashed #334155', borderRadius: 2 }}>
                <Typography variant="caption" color="primary" fontWeight="bold">HEDGING TIP</Typography>
                <Typography variant="body2">Consider hedging with Nifty 50 Puts during high macro volatility due to the 0.82 Beta coupling.</Typography>
             </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
