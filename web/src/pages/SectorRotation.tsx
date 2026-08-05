import { useEffect, useState } from 'react';
import { Box, Typography, Grid, Paper, LinearProgress } from '@mui/material';
import { getStocks } from '../api/client';

export default function SectorRotation() {
  const [sectorPerformance, setSectorPerformance] = useState<any>({});

  useEffect(() => {
    const calculatePerformance = async () => {
      const stocks = await getStocks();
      const sectors: any = {};

      stocks.forEach((stock: any) => {
        if (!stock.sector) return;
        if (!sectors[stock.sector]) sectors[stock.sector] = { count: 0, bullish: 0 };

        sectors[stock.sector].count += 1;
        if (stock.analysis?.consensus?.toUpperCase().includes('BUY')) {
          sectors[stock.sector].bullish += 1;
        }
      });

      setSectorPerformance(sectors);
    };
    calculatePerformance();
  }, []);

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>Sector Rotation (AI Bias)</Typography>

      <Grid container spacing={3}>
        {Object.keys(sectorPerformance).map((sector) => {
          const strength = (sectorPerformance[sector].bullish / sectorPerformance[sector].count) * 100;
          return (
            <Grid item xs={12} md={6} key={sector}>
              <Paper sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="h6">{sector}</Typography>
                  <Typography variant="h6" color="primary">{strength.toFixed(0)}% Bullish</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={strength}
                  sx={{ height: 10, borderRadius: 5 }}
                />
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                  Based on {sectorPerformance[sector].count} AI-analyzed symbols
                </Typography>
              </Paper>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
}
