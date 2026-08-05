import { Box, Typography, Paper, Grid, Chip } from '@mui/material';
import { Activity, Zap, Percent } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

export default function OptionsAnalytics({ data }: { data: any }) {
  const oiOption = {
    xAxis: { type: 'category', data: ['2400', '2450', '2500', '2550', '2600', '2650', '2700'] },
    yAxis: { type: 'value' },
    series: [
      { name: 'Calls', type: 'bar', data: [12, 45, 89, 120, 56, 32, 10], color: '#f43f5e' },
      { name: 'Puts', type: 'bar', data: [8, 23, 67, 45, 98, 110, 45], color: '#10b981' }
    ],
    legend: { show: true, textStyle: { color: '#fff' } },
    grid: { top: 40, bottom: 40, left: 40, right: 20 }
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Activity size={20} className="text-purple-500" /> Options & Derivatives Intel
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ mb: 3 }}>
               <Typography variant="caption" color="textSecondary">PCR (OPEN INTEREST)</Typography>
               <Typography variant="h5" fontWeight="bold">0.86 <Chip label="NEUTRAL" size="small" sx={{ ml: 1 }} /></Typography>
            </Box>
            <Box sx={{ mb: 3 }}>
               <Typography variant="caption" color="textSecondary">MAX PAIN</Typography>
               <Typography variant="h5" fontWeight="bold">₹2,500</Typography>
            </Box>
            <Box>
               <Typography variant="caption" color="textSecondary">IV RANK</Typography>
               <Typography variant="h5" fontWeight="bold">12.4% <Chip label="LOW" size="small" color="primary" variant="outlined" sx={{ ml: 1 }} /></Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 260 }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>OPEN INTEREST DISTRIBUTION (CURRENT EXPIRY)</Typography>
            <ReactECharts option={oiOption} style={{ height: '200px' }} theme="dark" />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
