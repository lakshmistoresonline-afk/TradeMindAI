import { Box, Typography, Paper, Grid, Stack, Divider } from '@mui/material';
import { Target, TrendingUp, Clock, Activity } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

export default function HistoricalAIPerformance() {
  const performanceOption = {
    xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] },
    yAxis: { type: 'value', axisLabel: { formatter: '{value}%' } },
    series: [{
      name: 'Win Rate',
      type: 'line',
      data: [68, 72, 65, 82, 78, 85],
      color: '#10b981',
      smooth: true,
      areaStyle: { opacity: 0.1 }
    }],
    grid: { top: 30, bottom: 30, left: 40, right: 20 }
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Activity size={20} className="text-emerald-500" /> Historical AI Performance
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 300 }}>
             <Typography variant="subtitle2" color="textSecondary" gutterBottom>6-MONTH SIGNAL ACCURACY TREND</Typography>
             <ReactECharts option={performanceOption} style={{ height: '240px' }} theme="dark" />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 300, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
             <Stack spacing={3}>
                <PerformanceStat label="LTM Win Rate" value="72.4%" icon={<Target size={16} />} />
                <PerformanceStat label="Avg. Return / Signal" value="+4.8%" icon={<TrendingUp size={16} />} />
                <PerformanceStat label="Avg. Holding Period" value="12 Days" icon={<Clock size={16} />} />
             </Stack>

             <Divider sx={{ my: 3, opacity: 0.1 }} />

             <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, textAlign: 'center' }}>
                <Typography variant="caption" color="textSecondary">
                   Based on 4,200 institutional setups scanned.
                </Typography>
             </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function PerformanceStat({ label, value, icon }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
       <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'text.secondary' }}>
          {icon}
          <Typography variant="body2">{label}</Typography>
       </Box>
       <Typography variant="h6" fontWeight="bold" color="primary">{value}</Typography>
    </Box>
  );
}
