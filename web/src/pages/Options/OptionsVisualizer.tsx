import { Box, Typography, Paper, Grid, Chip, Card, CardContent } from '@mui/material';
import ReactECharts from 'echarts-for-react';

export default function OptionsVisualizer() {

  const oiOption = {
    xAxis: { type: 'category', data: ['23000', '23100', '23200', '23300', '23400', '23500', '23600'] },
    yAxis: { type: 'value' },
    series: [
      { name: 'Calls', type: 'bar', data: [120, 200, 150, 80, 70, 110, 130], color: '#f43f5e' },
      { name: 'Puts', type: 'bar', data: [80, 110, 130, 200, 150, 80, 70], color: '#10b981' }
    ],
    legend: { show: true, textStyle: { color: '#fff' } }
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>Options Analytics</Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <MetricCard title="PCR (Volume)" value="0.92" status="NEUTRAL" />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard title="Max Pain" value="23,450" status="SUPPORT" />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard title="IV Rank" value="14.2%" status="LOW" />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard title="Gamma Flip" value="23,520" status="RESISTANCE" />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>Open Interest Distribution</Typography>
            <ReactECharts option={oiOption} style={{ height: '300px' }} theme="dark" />
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 400, overflowY: 'auto' }}>
            <Typography variant="h6" gutterBottom>Top Greek Exposure</Typography>
            <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
              <GreekBar label="Delta" value={0.65} color="#10b981" />
              <GreekBar label="Gamma" value={0.12} color="#2979FF" />
              <GreekBar label="Theta" value={-0.45} color="#f43f5e" />
              <GreekBar label="Vega" value={0.28} color="#fbbf24" />
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function MetricCard({ title, value, status }: any) {
  return (
    <Card>
      <CardContent>
        <Typography variant="caption" color="textSecondary">{title}</Typography>
        <Typography variant="h5" fontWeight="bold" sx={{ my: 1 }}>{value}</Typography>
        <Chip label={status} size="small" variant="outlined" color="primary" />
      </CardContent>
    </Card>
  );
}

function GreekBar({ label, value, color }: any) {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="body2" fontWeight="bold">{label}</Typography>
        <Typography variant="caption">{value}</Typography>
      </Box>
      <Box sx={{ width: '100%', height: 4, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 2 }}>
        <Box sx={{ width: `${Math.abs(value)*100}%`, height: '100%', bgcolor: color, borderRadius: 2 }} />
      </Box>
    </Box>
  );
}
