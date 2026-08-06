import { Box, Typography, Paper } from '@mui/material';
import ReactECharts from 'echarts-for-react';

export default function RadarComparison({ stock }: { stock: any }) {
  if (!stock) return null;

  const score = stock.ai_investment_score || 50;
  const momentum = stock.analysis?.technical_data?.indicators?.momentum_rsi * 100 || 50;
  const valuation = stock.pe_ratio < 30 ? 80 : 40;
  const growth = 75; // Mock logic
  const smc = stock.analysis?.technical_data?.smc?.order_blocks?.length > 0 ? 90 : 30;

  const option = {
    legend: { data: [stock.symbol, 'Sector Average'], textStyle: { color: '#fff' }, bottom: 0 },
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
          value: [valuation, momentum, growth, score, smc],
          name: stock.symbol,
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
