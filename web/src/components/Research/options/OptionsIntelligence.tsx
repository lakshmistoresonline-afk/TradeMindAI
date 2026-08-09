import { Box, Typography, Paper, Grid, Chip, Stack, Tab, Tabs } from '@mui/material';
import { Activity, TrendingUp } from 'lucide-react';
import { useState } from 'react';
import ReactECharts from 'echarts-for-react';

interface OptionsIntelligenceProps {
  data?: any;
}

export default function OptionsIntelligence({ data }: OptionsIntelligenceProps) {
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
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Activity size={20} className="text-purple-500" /> Options Intelligence {data?.symbol}
      </Typography>

      <Paper sx={{ p: 0, overflow: 'hidden' }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ px: 2, pt: 1, borderBottom: '1px solid #334155' }}>
           <Tab label="Overview" />
           <Tab label="Open Interest" />
           <Tab label="Greeks" />
           <Tab label="Volatility" />
        </Tabs>

        <Box sx={{ p: 3 }}>
           {tab === 0 && (
             <Grid container spacing={3}>
               <Grid item xs={12} md={4}>
                  <Stack spacing={3}>
                    <MetricItem label="PCR (OI)" value="0.86" status="NEUTRAL" color="warning" />
                    <MetricItem label="MAX PAIN" value="₹2,500" status="SUPPORT" color="primary" />
                    <MetricItem label="IV RANK" value="12.4%" status="LOW" color="primary" />
                    <MetricItem label="GAMMA FLIP" value="2,520" status="RESISTANCE" color="error" />
                  </Stack>
               </Grid>
               <Grid item xs={12} md={8}>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>OI DISTRIBUTION (STRIKE)</Typography>
                  <ReactECharts option={oiOption} style={{ height: '280px' }} theme="dark" />
               </Grid>
             </Grid>
           )}

           {tab === 1 && (
             <Box sx={{ height: 350 }}>
                <Typography variant="subtitle2" color="textSecondary" gutterBottom>DETAILED OPEN INTEREST ANALYSIS</Typography>
                <ReactECharts option={oiOption} style={{ height: '300px' }} theme="dark" />
             </Box>
           )}

           {tab === 2 && (
             <Grid container spacing={4}>
                <Grid item xs={12} md={6}>
                   <GreekProgress label="Delta" value={0.65} color="#10b981" desc="Price Sensitivity" />
                   <GreekProgress label="Gamma" value={0.12} color="#3b82f6" desc="Delta Sensitivity" />
                </Grid>
                <Grid item xs={12} md={6}>
                   <GreekProgress label="Theta" value={-0.45} color="#f43f5e" desc="Time Decay" />
                   <GreekProgress label="Vega" value={0.28} color="#fbbf24" desc="Volatility Sensitivity" />
                </Grid>
             </Grid>
           )}

           {tab === 3 && (
             <Box sx={{ p: 4, textAlign: 'center' }}>
                <TrendingUp size={48} color="#94a3b8" />
                <Typography color="textSecondary" sx={{ mt: 2 }}>IV Analytics Engine Active. Syncing latest volatility surface...</Typography>
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

function GreekProgress({ label, value, color, desc }: any) {
  return (
    <Box sx={{ mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Box>
           <Typography variant="body2" fontWeight={800}>{label}</Typography>
           <Typography variant="caption" color="textSecondary">{desc}</Typography>
        </Box>
        <Typography variant="body2" fontWeight={900}>{value}</Typography>
      </Box>
      <Box sx={{ width: '100%', height: 6, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 1 }}>
        <Box sx={{ width: `${Math.min(Math.abs(value) * 100, 100)}%`, height: '100%', bgcolor: color, borderRadius: 1 }} />
      </Box>
    </Box>
  );
}
