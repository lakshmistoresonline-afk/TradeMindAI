import { Box, Typography, Paper, Grid, Stack, Chip, Divider, Tooltip } from '@mui/material';
import { LineChart, Target, Info } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

export default function TechnicalAnalysis({ data }: { data: any }) {
  const chartOption = {
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
    yAxis: { type: 'value' },
    series: [{
      data: data?.history || [2420, 2460, 2450, 2490, 2520],
      type: 'line',
      smooth: true,
      color: '#10b981',
      areaStyle: { opacity: 0.1 }
    }],
    grid: { top: 20, bottom: 20, left: 40, right: 10 }
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" fontWeight={800} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LineChart size={20} className="text-blue-500" /> Technical Analysis
        </Typography>
        <Chip label="LIVE" size="small" variant="outlined" sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900 }} color="primary" />
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 350 }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ fontWeight: 800 }}>PRICE ACTION & TREND ALIGNMENT</Typography>
            <ReactECharts option={chartOption} style={{ height: '280px' }} theme="dark" />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 350 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
               <Typography variant="subtitle2" color="textSecondary" sx={{ fontWeight: 800 }}>MOMENTUM SCORECARD</Typography>
               <Tooltip title="Real-time multi-timeframe momentum analysis.">
                  <Info size={14} className="text-slategray" />
               </Tooltip>
            </Box>
            <Stack spacing={2.5} sx={{ mt: 1 }}>
               <IndicatorRow label="RSI (14)" value={data?.rsi || "62.4"} status="BULLISH" />
               <IndicatorRow label="MACD" value={data?.macd || "POSITIVE"} status="STABLE" />
               <IndicatorRow label="EMA 20/50" value="CROSSOVER" status="CONFIRMED" />
               <IndicatorRow label="Volume" value="1.2M" status="ACCUMULATING" />
            </Stack>

            <Divider sx={{ my: 3, opacity: 0.1 }} />

            <Box sx={{ p: 1.5, bgcolor: 'rgba(59, 130, 246, 0.05)', borderRadius: 1, border: '1px solid rgba(59, 130, 246, 0.1)' }}>
               <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 800 }}>
                  <Target size={12} /> BIAS
               </Typography>
               <Typography variant="subtitle2" fontWeight={800}>{data?.bias || "Strongly Bullish above 2480"}</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function IndicatorRow({ label, value, status }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
       <Box>
          <Typography variant="body2" fontWeight={800}>{label}</Typography>
          <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600 }}>{value}</Typography>
       </Box>
       <Chip label={status} size="small" sx={{ height: 18, fontSize: '0.55rem', fontWeight: 900, bgcolor: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }} />
    </Box>
  );
}
