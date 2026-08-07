import { Box, Typography, Paper, Rating, Stack, Divider } from '@mui/material';
import { Award } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

export default function AIScoreCard({ score, grade, confidence }: any) {
  const gaugeOption = {
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      radius: '100%',
      center: ['50%', '75%'],
      itemStyle: { color: score > 70 ? '#10b981' : score > 40 ? '#fbbf24' : '#f43f5e' },
      progress: { show: true, width: 14 },
      pointer: { show: false },
      axisLine: { lineStyle: { width: 14, color: [[1, 'rgba(255,255,255,0.05)']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      detail: { show: false },
      data: [{ value: score }]
    }]
  };

  return (
    <Paper sx={{ p: 2.5, height: '100%', border: '1px solid #1e293b' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle2" color="textSecondary">INVESTMENT SCORE</Typography>
        <Typography variant="h6" fontWeight={900} color="primary" sx={{ fontFamily: 'JetBrains Mono' }}>{grade}</Typography>
      </Box>

      <Box sx={{ height: 110, position: 'relative' }}>
         <ReactECharts option={gaugeOption} style={{ height: '100%' }} />
         <Box sx={{ position: 'absolute', bottom: 5, left: '50%', transform: 'translateX(-50%)', textAlign: 'center' }}>
            <Typography variant="h4" fontWeight={900} sx={{ fontFamily: 'JetBrains Mono' }}>{Math.round(score)}</Typography>
         </Box>
      </Box>

      <Stack spacing={1.5} sx={{ mt: 2 }}>
         <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="caption" color="textSecondary">AI Star Rating</Typography>
            <Rating value={(score/100)*5} precision={0.5} readOnly size="small" />
         </Box>
         <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="caption" color="textSecondary">AI Conviction</Typography>
            <Typography variant="caption" fontWeight={800} color="primary">{confidence?.score || 82}%</Typography>
         </Box>
      </Stack>

      <Divider sx={{ my: 2, opacity: 0.05 }} />

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
         <Award size={14} className="text-amber-500" />
         <Typography variant="caption" fontWeight={700}>TOP 8% IN SECTOR</Typography>
      </Box>
    </Paper>
  );
}
