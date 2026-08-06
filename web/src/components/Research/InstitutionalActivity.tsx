import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Stack, Divider, CircularProgress, Chip } from '@mui/material';
import { Landmark, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import ReactECharts from 'echarts-for-react';
import { getInstitutionalFlow } from '../../api/client';

export default function InstitutionalActivity() {
  const [flow, setFlow] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getInstitutionalFlow()
      .then(setFlow)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress size={20} />;

  const flowOption = {
    xAxis: { type: 'category', data: ['Apr', 'May', 'Jun', 'Jul'] },
    yAxis: { type: 'value' },
    series: [
      { name: 'FII Flow', type: 'line', data: [1200, -450, 800, flow?.FII_Net || 2100], color: '#10b981', smooth: true },
      { name: 'DII Flow', type: 'line', data: [500, 1100, 200, flow?.DII_Net || 650], color: '#3b82f6', smooth: true }
    ],
    legend: { show: true, textStyle: { color: '#fff' } },
    grid: { top: 40, bottom: 40, left: 40, right: 20 }
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Landmark size={20} className="text-blue-500" /> Institutional Activity Deep Dive
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 300 }}>
             <Typography variant="subtitle2" color="textSecondary" gutterBottom>FII / DII ACCUMULATION TREND (4 MONTHS)</Typography>
             <ReactECharts option={flowOption} style={{ height: '240px' }} theme="dark" />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 300 }}>
             <Typography variant="subtitle2" color="textSecondary" gutterBottom>INSTITUTIONAL CONFIDENCE</Typography>
             <Box sx={{ textAlign: 'center', mt: 4 }}>
                <Typography variant="h3" fontWeight="bold" color="primary">{flow?.Market_Sentiment?.toUpperCase() || 'STRONG'}</Typography>
                <Typography variant="body2" color="textSecondary">Accumulation Phase Detected</Typography>

                <Divider sx={{ my: 3, opacity: 0.1 }} />

                <Stack spacing={2}>
                   <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="caption">Mutual Fund Holdings</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                         <Typography variant="caption" fontWeight="bold">+1.2% QoQ</Typography>
                         <ArrowUpRight size={12} className="text-emerald-500" />
                      </Box>
                   </Box>
                   <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="caption">Promoter Pledging</Typography>
                      <Typography variant="caption" fontWeight="bold" color="success.main">NONE</Typography>
                   </Box>
                   <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="caption">FII Net Cash</Typography>
                      <Typography variant="caption" fontWeight="bold" color={flow?.FII_Net >= 0 ? "primary.main" : "error.main"}>
                         ₹{flow?.FII_Net} Cr
                      </Typography>
                   </Box>
                </Stack>
             </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
