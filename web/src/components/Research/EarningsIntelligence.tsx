import { Box, Typography, Paper, Grid, Divider } from '@mui/material';
import { Clock } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

export default function EarningsIntelligence() {
  const chartOption = {
    xAxis: { type: 'category', data: ['Q1', 'Q2', 'Q3', 'Q4'] },
    yAxis: { type: 'value' },
    series: [
      { name: 'Actual EPS', type: 'bar', data: [12.5, 14.2, 11.8, 15.6], color: '#10b981' },
      { name: 'Estimate', type: 'line', data: [12.0, 13.5, 12.2, 14.8], color: '#94a3b8' }
    ],
    legend: { show: true, textStyle: { color: '#fff' } },
    grid: { top: 40, bottom: 40, left: 40, right: 20 }
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Clock size={20} className="text-amber-500" /> Earnings Intelligence
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 300 }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>HISTORICAL EPS SURPRISES</Typography>
            <ReactECharts option={chartOption} style={{ height: '240px' }} theme="dark" />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 300, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <Typography variant="subtitle2" color="textSecondary" align="center" gutterBottom>NEXT EARNINGS DATE</Typography>
            <Typography variant="h4" fontWeight="bold" align="center">OCT 24, 2026</Typography>
            <Typography variant="body2" color="textSecondary" align="center">Estimated EPS: ₹16.42</Typography>

            <Divider sx={{ my: 3, opacity: 0.1 }} />

            <Box sx={{ p: 2, bgcolor: 'rgba(16, 185, 129, 0.05)', borderRadius: 2, border: '1px solid #10b981' }}>
               <Typography variant="caption" fontWeight="bold" color="primary">AI GROWTH BIAS</Typography>
               <Typography variant="h6" fontWeight="bold">POSITIVE</Typography>
               <Typography variant="caption" color="textSecondary">Expected surprise: +2.4%</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
