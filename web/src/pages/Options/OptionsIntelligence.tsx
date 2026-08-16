import { useState } from 'react';
import { Box, Typography, Paper, Grid, Tab, Tabs, Chip } from '@mui/material';
import { Activity, TrendingUp } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

export default function OptionsIntelligence() {
  const [tab, setTab] = useState(0);

  const oiOption = {
    xAxis: { type: 'category', data: ['2400', '2450', '2500', '2550', '2600', '2650', '2700'] },
    yAxis: { type: 'value' },
    series: [
      { name: 'Calls', type: 'bar', data: [12, 45, 89, 120, 56, 32, 10], color: '#f43f5e' },
      { name: 'Puts', type: 'bar', data: [8, 23, 67, 45, 98, 110, 45], color: '#10b981' }
    ],
    legend: { show: true, textStyle: { color: '#94a3b8' } },
    grid: { top: 40, bottom: 40, left: 40, right: 20 }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
           <Activity size={32} className="text-purple-500" />
           <Typography variant="h4" sx={{ fontWeight: 900 }}>Options Intelligence</Typography>
        </Box>
        <Chip label="NIFTY 50 • 28 AUG EXPIRY" color="secondary" variant="outlined" sx={{ fontWeight: 800 }} />
      </Box>

      <Paper sx={{ p: 0, overflow: 'hidden', mb: 4 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ px: 2, pt: 1, borderBottom: '1px solid #334155' }}>
           <Tab label="Open Interest" sx={{ fontWeight: 800 }} />
           <Tab label="Greek Analytics" sx={{ fontWeight: 800 }} />
           <Tab label="Max Pain" sx={{ fontWeight: 800 }} />
           <Tab label="Volatility Surface" sx={{ fontWeight: 800 }} />
        </Tabs>

        <Box sx={{ p: 4 }}>
           {tab === 0 && (
             <Grid container spacing={4}>
                <Grid item xs={12} md={8}>
                   <Typography variant="subtitle2" color="textSecondary" gutterBottom>STRIKE-WISE OI DISTRIBUTION</Typography>
                   <ReactECharts option={oiOption} style={{ height: '400px' }} theme="dark" />
                </Grid>
                <Grid item xs={12} md={4}>
                   <Typography variant="subtitle2" color="textSecondary" gutterBottom>SENSITIVITY ANALYSIS</Typography>
                   <Box sx={{ mt: 3 }}>
                      <MetricItem label="PCR (Volume)" value="0.94" status="NEUTRAL" />
                      <MetricItem label="PCR (OI)" value="0.86" status="BULLISH" color="primary" />
                      <MetricItem label="Gamma Flip" value="25,240" status="RESISTANCE" color="error" />
                      <MetricItem label="Max Pain" value="25,000" status="SUPPORT" color="primary" />
                   </Box>
                </Grid>
             </Grid>
           )}

           {tab === 1 && (
              <Box sx={{ p: 8, textAlign: 'center', opacity: 0.5 }}>
                 <TrendingUp size={48} style={{ margin: '0 auto 16px' }} />
                 <Typography variant="h6">Greeks Engine Syncing...</Typography>
                 <Typography variant="body2">Calculating Delta, Gamma, Theta, Vega for entire option chain.</Typography>
              </Box>
           )}
        </Box>
      </Paper>
    </Box>
  );
}

function MetricItem({ label, value, status, color }: any) {
  return (
    <Box sx={{ mb: 3 }}>
       <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>{label}</Typography>
       <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 0.5 }}>
          <Typography variant="h5" fontWeight={900}>{value}</Typography>
          <Chip label={status} size="small" variant="outlined" color={color || 'default'} sx={{ fontWeight: 900, height: 18, fontSize: '0.6rem' }} />
       </Box>
    </Box>
  );
}
