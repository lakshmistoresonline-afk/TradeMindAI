import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Grid } from '@mui/material';
import { getStocks } from '../../api/client';

export default function MarketHeatmap() {
  const [stocks, setStocks] = useState<any[]>([]);

  useEffect(() => {
    getStocks().then(setStocks);
  }, []);

  const getColor = (change: number) => {
    if (change > 3) return '#064e3b';
    if (change > 1.5) return '#059669';
    if (change > 0) return '#10b981';
    if (change === 0) return '#475569';
    if (change > -1.5) return '#f87171';
    if (change > -3) return '#ef4444';
    return '#7f1d1d';
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>Market Heatmap</Typography>
      <Grid container spacing={1}>
        {stocks.sort((a,b) => (b.change_pct || 0) - (a.change_pct || 0)).map(stock => (
          <Grid item key={stock.symbol} xs={4} sm={2} md={1.5} lg={1}>
            <Paper sx={{
              height: 80,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: getColor(stock.change_pct || 0),
              border: 'none',
              cursor: 'pointer',
              '&:hover': { opacity: 0.8 }
            }}>
              <Typography variant="subtitle2" fontWeight="bold">{stock.symbol}</Typography>
              <Typography variant="caption">{stock.change_pct?.toFixed(2)}%</Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
