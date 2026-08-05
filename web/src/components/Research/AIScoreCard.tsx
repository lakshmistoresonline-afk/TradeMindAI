import { Box, Typography, Paper, Grid, Rating, Chip, Stack } from '@mui/material';
import { TrendingUp, Award, Zap, Info } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

export default function AIScoreCard({ score, grade, confidence }: any) {
  const gaugeOption = {
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      splitNumber: 5,
      itemStyle: { color: score > 70 ? '#10b981' : score > 40 ? '#fbbf24' : '#f43f5e' },
      progress: { show: true, width: 12 },
      pointer: { show: false },
      axisLine: { lineStyle: { width: 12, color: [[1, 'rgba(255,255,255,0.05)']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      detail: { show: false },
      data: [{ value: score }]
    }]
  };

  return (
    <Paper sx={{ p: 3, height: '100%', position: 'relative', overflow: 'hidden' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="subtitle2" color="textSecondary" sx={{ fontWeight: 'bold' }}>AI INVESTMENT SCORE</Typography>
        <Chip label={grade} color="primary" size="small" sx={{ fontWeight: 'bold', fontSize: '1rem', height: 28 }} />
      </Box>

      <Grid container spacing={2} alignItems="center">
        <Grid item xs={6}>
          <Box sx={{ height: 120, mt: -2 }}>
            <ReactECharts option={gaugeOption} style={{ height: '100%' }} />
            <Box sx={{ position: 'absolute', top: '55%', left: '25%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
                <Typography variant="h3" fontWeight="bold">{Math.round(score)}</Typography>
                <Typography variant="caption" color="textSecondary">POINT SCALE</Typography>
            </Box>
          </Box>
        </Grid>
        <Grid item xs={6}>
           <Stack spacing={1}>
              <Box>
                 <Typography variant="caption" color="textSecondary">AI Star Rating</Typography>
                 <Rating value={(score/100)*5} precision={0.5} readOnly size="small" />
              </Box>
              <Box>
                 <Typography variant="caption" color="textSecondary">Confidence Level</Typography>
                 <Typography variant="h6" fontWeight="bold">{confidence?.score}%</Typography>
              </Box>
           </Stack>
        </Grid>
      </Grid>

      <Box sx={{ mt: 3, p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 2 }}>
         <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Award size={14} className="text-emerald-500" /> INSTITUTIONAL RANKING
         </Typography>
         <Typography variant="body2" fontWeight="bold" sx={{ mt: 0.5 }}>Top 8% in IT Sector</Typography>
      </Box>
    </Paper>
  );
}
