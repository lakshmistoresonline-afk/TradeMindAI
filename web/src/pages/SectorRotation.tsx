import { useEffect, useState } from 'react';
import { Box, Typography, Grid, Paper, LinearProgress, Chip } from '@mui/material';
import ReactECharts from 'echarts-for-react';
import { getStocks } from '../api/client';

export default function SectorRotation() {
  const [sectorPerformance, setSectorPerformance] = useState<any>({});

  useEffect(() => {
    getStocks().then(data => {
      const sectors: any = {};
      data.forEach((stock: any) => {
        if (!stock.sector) return;
        if (!sectors[stock.sector]) sectors[stock.sector] = { count: 0, bullish: 0, change: [] };
        sectors[stock.sector].count += 1;
        if (stock.analysis?.consensus?.toUpperCase().includes('BUY')) sectors[stock.sector].bullish += 1;
        if (stock.change_pct) sectors[stock.sector].change.push(stock.change_pct);
      });
      setSectorPerformance(sectors);
    });
  }, []);

  const chartOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { textStyle: { color: '#fff' } },
    xAxis: { type: 'category', data: Object.keys(sectorPerformance), axisLabel: { color: '#94a3b8' } },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8' } },
    series: [
      {
        name: 'AI Bullish Strength (%)',
        type: 'bar',
        data: Object.keys(sectorPerformance).map(k => (sectorPerformance[k].bullish / sectorPerformance[k].count) * 100),
        color: '#10b981'
      },
      {
        name: 'Avg Daily Return (%)',
        type: 'line',
        data: Object.keys(sectorPerformance).map(k => {
           const changes = sectorPerformance[k].change;
           return changes.length > 0 ? changes.reduce((a:any, b:any) => a + b, 0) / changes.length : 0;
        }),
        color: '#3b82f6'
      }
    ]
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
         <Box>
            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>Institutional Sector Rotation</Typography>
            <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 'bold' }}>
               SESSION ANALYSIS: {new Date().toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}
            </Typography>
         </Box>
         <Chip label="Real-time Animated Feed" color="primary" variant="outlined" />
      </Box>

      <Paper sx={{ p: 4, mb: 4, height: 400 }}>
         <ReactECharts option={chartOption} style={{ height: '100%' }} theme="dark" />
      </Paper>

      <Grid container spacing={3}>
        {Object.keys(sectorPerformance).map((sector) => {
          const strength = (sectorPerformance[sector].bullish / sectorPerformance[sector].count) * 100;
          return (
            <Grid item xs={12} md={4} key={sector}>
              <Paper sx={{ p: 3, border: '1px solid #334155' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle1" fontWeight="bold">{sector}</Typography>
                  <Typography variant="subtitle1" color="primary" fontWeight="bold">{strength.toFixed(0)}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={strength}
                  sx={{ height: 6, borderRadius: 5, mb: 2 }}
                />
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                   <Typography variant="caption" color="textSecondary">{sectorPerformance[sector].count} Symbols</Typography>
                   <Typography variant="caption" color="primary" fontWeight="bold">
                      {strength > 60 ? 'LEADING' : strength < 40 ? 'LAGGING' : 'IMPROVING'}
                   </Typography>
                </Box>
              </Paper>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
}
