import { Box, Typography, Paper } from '@mui/material';
import ReactECharts from 'echarts-for-react';
import { Activity } from 'lucide-react';

export default function VarianceMap() {
  const data = [
    { symbol: 'RELIANCE', variance: 0.12 },
    { symbol: 'TCS', variance: -0.05 },
    { symbol: 'HDFCBANK', variance: 0.21 },
    { symbol: 'INFY', variance: 0.08 },
    { symbol: 'ICICIBANK', variance: -0.15 },
  ];

  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'value', axisLabel: { formatter: '{value}%', color: '#64748b' } },
    yAxis: { type: 'category', data: data.map(d => d.symbol), axisLabel: { color: '#94a3b8', fontWeight: 800 } },
    series: [{
      name: 'Slippage/Variance',
      data: data.map(d => d.variance),
      type: 'bar',
      itemStyle: {
        color: (param: any) => param.data >= 0 ? '#10b981' : '#f43f5e'
      }
    }],
    grid: { top: 20, bottom: 40, left: 80, right: 30 }
  };

  return (
    <Paper sx={{ p: 3, border: '1px solid #1e293b', bgcolor: 'rgba(15, 23, 42, 0.3)' }}>
       <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
          <Activity size={18} className="text-emerald-500" />
          <Typography variant="subtitle2" fontWeight={900}>EXECUTION VARIANCE (SLIPPAGE)</Typography>
       </Box>
       <ReactECharts option={option} style={{ height: 250 }} />
       <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block', textAlign: 'center' }}>
          Measures the difference between **AI Optimal Entry** and **Actual Production Trigger**.
       </Typography>
    </Paper>
  );
}
