import { Box, Typography, Paper } from '@mui/material';
import ReactECharts from 'echarts-for-react';

export default function RadarComparison({ stock }: { stock: any }) {
  if (!stock || !stock.analysis) return null;

  const technical = stock.analysis?.technical_data || {};
  const indicators = technical.indicators || {};

  // Real-time Relative Strength Logic
  const score = stock.ai_investment_score || 50;
  const momentum = (indicators.RSI || 50);
  const valuation = stock.pe_ratio ? Math.max(0, 100 - (stock.pe_ratio / 50) * 100) : 50;
  const quality = stock.roe ? Math.min(100, (stock.roe * 100) * 4) : 60;
  const smc = technical.smc?.order_blocks?.length > 0 ? 85 : 40;

  const option = {
    legend: { data: [stock.symbol, 'Sector Avg'], textStyle: { color: '#94a3b8' }, bottom: 0 },
    radar: {
      indicator: [
        { name: 'Valuation', max: 100 },
        { name: 'Momentum', max: 100 },
        { name: 'Quality', max: 100 },
        { name: 'SMC Alignment', max: 100 },
        { name: 'AI Consensus', max: 100 },
      ],
      axisName: { color: '#94a3b8', fontSize: 10 },
      splitArea: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
    },
    series: [{
      type: 'radar',
      data: [
        {
          value: [valuation, momentum, quality, smc, score],
          name: stock.symbol,
          itemStyle: { color: '#10b981' },
          areaStyle: { opacity: 0.1 }
        },
        {
          value: [50, 50, 50, 50, 50],
          name: 'Sector Avg',
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
