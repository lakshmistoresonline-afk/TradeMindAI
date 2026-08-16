import { Box, Typography, Paper, Grid, Chip, Stack, Tab, Tabs } from '@mui/material';
import { Activity, TrendingUp } from 'lucide-react';
import { useState } from 'react';
import ReactECharts from 'echarts-for-react';

interface OptionsIntelligenceProps {
  stock?: any;
}

export default function OptionsIntelligence({ stock }: OptionsIntelligenceProps) {
  const [tab, setTab] = useState(0);

  // Vision 2.2: Real Options Data from Backend
  const options = stock?.options_data || {};
  const isSample = !options.available;

  const oiOption = {
    xAxis: {
      type: 'category',
      data: options.oi_distribution?.strikes || ['2400', '2450', '2500', '2550', '2600', '2650', '2700']
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: 'Calls',
        type: 'bar',
        data: options.oi_distribution?.calls || [12, 45, 89, 120, 56, 32, 10],
        color: '#f43f5e'
      },
      {
        name: 'Puts',
        type: 'bar',
        data: options.oi_distribution?.puts || [8, 23, 67, 45, 98, 110, 45],
        color: '#10b981'
      }
    ],
    legend: { show: true, textStyle: { color: '#94a3b8' }, top: 0 },
    grid: { top: 40, bottom: 40, left: 40, right: 20 }
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" fontWeight={800} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Activity size={20} className="text-purple-500" /> Options Intelligence
        </Typography>
        <Stack direction="row" spacing={1} alignItems="center">
           {isSample && <Chip label="SAMPLE MODEL" size="small" variant="filled" color="warning" sx={{ height: 16, fontSize: '0.55rem', fontWeight: 900 }} />}
           <Chip label={options.expiry || "EXPIRY: --"} size="small" variant="outlined" sx={{ height: 16, fontSize: '0.55rem', fontWeight: 800 }} />
        </Stack>
      </Box>

      <Paper sx={{ p: 0, overflow: 'hidden', border: '1px solid #1e293b' }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ px: 2, pt: 1, borderBottom: '1px solid #334155' }} variant="scrollable" scrollButtons="auto">
           <Tab label="Overview" sx={{ fontWeight: 800 }} />
           <Tab label="Open Interest" sx={{ fontWeight: 800 }} />
           <Tab label="Greeks" sx={{ fontWeight: 800 }} />
           <Tab label="Volatility" sx={{ fontWeight: 800 }} />
        </Tabs>

        <Box sx={{ p: 3 }}>
           {tab === 0 && (
             <Grid container spacing={3}>
               <Grid item xs={12} md={4}>
                  <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                     <Typography variant="subtitle2" color="textSecondary" sx={{ fontWeight: 800 }}>SENSITIVITY ANALYSIS</Typography>
                     {isSample && <Chip label="SAMPLE" size="small" sx={{ height: 14, fontSize: '0.5rem' }} />}
                  </Box>
                  <Stack spacing={3}>
                    <MetricItem
                      label="PCR (OI)"
                      value={options.pcr || "0.86"}
                      status={options.pcr > 1.2 ? "BEARISH" : options.pcr < 0.8 ? "BULLISH" : "NEUTRAL"}
                      color={options.pcr > 1.2 ? "error" : options.pcr < 0.8 ? "primary" : "warning"}
                    />
                    <MetricItem label="MAX PAIN" value={options.max_pain ? `₹${options.max_pain.toLocaleString()}` : "---"} status="SUPPORT" color="primary" />
                    <MetricItem label="IV RANK" value="---" status="LOW" color="primary" />
                    <MetricItem label="GAMMA FLIP" value="---" status="RESISTANCE" color="error" />
                  </Stack>
               </Grid>
               <Grid item xs={12} md={8}>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ fontWeight: 800 }}>OI DISTRIBUTION (STRIKE)</Typography>
                  <ReactECharts option={oiOption} style={{ height: '280px' }} theme="dark" />
               </Grid>
             </Grid>
           )}

           {tab === 1 && (
             <Box sx={{ height: 350 }}>
                <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ fontWeight: 800 }}>DETAILED OPEN INTEREST ANALYSIS</Typography>
                <ReactECharts option={oiOption} style={{ height: '300px' }} theme="dark" />
             </Box>
           )}

           {(tab === 2 || tab === 3) && (
             <Box sx={{ p: 8, textAlign: 'center', opacity: 0.3 }}>
                <TrendingUp size={48} color="#94a3b8" style={{ margin: '0 auto 16px' }} />
                <Typography variant="body2" sx={{ fontWeight: 600 }}>Deep {tab === 2 ? 'Greek' : 'Volatility'} Analytics syncing from Institutional Hub...</Typography>
             </Box>
           )}
        </Box>
      </Paper>
    </Box>
  );
}

function MetricItem({ label, value, status, color }: any) {
  return (
    <Box>
       <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>{label}</Typography>
       <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mt: 0.5 }}>
          <Typography variant="h5" fontWeight={900}>{value}</Typography>
          <Chip label={status} size="small" variant="outlined" color={color} sx={{ height: 18, fontSize: '0.6rem', fontWeight: 800 }} />
       </Box>
    </Box>
  );
}
