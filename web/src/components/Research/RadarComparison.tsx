import { Box, Typography, Paper } from '@mui/material';
import ReactECharts from 'echarts-for-react';

export default function RadarComparison({ symbol }: { symbol: string }) {
  const option = {
    legend: { data: [symbol, 'Sector Average'], textStyle: { color: '#fff' }, bottom: 0 },
    radar: {
      indicator: [
        { name: 'Valuation', max: 100 },
        { name: 'Momentum', max: 100 },
        { name: 'Growth', max: 100 },
        { name: 'Quality', max: 100 },
        { name: 'SMC Alignment', max: 100 },
      ],
      axisName: { color: '#94a3b8' },
      splitArea: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
    },
    series: [{
      type: 'radar',
      data: [
        {
          value: [82, 75, 90, 88, 65],
          name: symbol,
          itemStyle: { color: '#10b981' },
          areaStyle: { opacity: 0.1 }
        },
        {
          value: [60, 62, 55, 70, 50],
          name: 'Sector Average',
          itemStyle: { color: '#3b82f6' },
          areaStyle: { opacity: 0.1 }
        }
      ]
    }]
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom>Institutional Relative Strength</Typography>
      <Paper sx={{ p: 3, height: 350 }}>
        <ReactECharts option={option} style={{ height: '100%' }} theme="dark" />
      </Paper>
    </Box>
  );
}
