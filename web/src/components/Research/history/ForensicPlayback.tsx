import { Box, Typography, Paper, Stack, Chip } from '@mui/material';
import { History } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

export default function ForensicPlayback({ signal }: { signal: any }) {
  if (!signal) return null;

  const option = {
    xAxis: { type: 'category', data: ['-4', '-3', '-2', '-1', 'Signal', '+1', '+2', '+3', '+4'] },
    yAxis: { type: 'value', scale: true },
    series: [
      {
        data: [100, 102, 101, 105, 108, 112, 115, 114, 118].map(v => (v / 108) * signal.entry_price),
        type: 'line',
        smooth: true,
        markArea: {
            data: [[{
                name: 'Consensus Zone',
                xAxis: 'Signal',
                itemStyle: { color: 'rgba(16, 185, 129, 0.1)' }
            }, {
                xAxis: '+2'
            }]]
        },
        markPoint: {
            data: [{ name: 'Entry', xAxis: 'Signal', yAxis: signal.entry_price, itemStyle: { color: '#10b981' } }]
        }
      }
    ],
    grid: { top: 40, bottom: 40, left: 50, right: 20 }
  };

  return (
    <Paper sx={{ p: 3, border: '1px solid #1e293b', bgcolor: 'rgba(15, 23, 42, 0.5)' }}>
       <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Stack direction="row" spacing={1} alignItems="center">
             <History size={18} className="text-blue-400" />
             <Typography variant="subtitle2" fontWeight={900}>FORENSIC PLAYBACK: {signal.symbol}</Typography>
          </Stack>
          <Chip label="ORIGINAL SNAPSHOT" size="small" variant="outlined" sx={{ fontWeight: 900, height: 20, fontSize: '0.55rem' }} />
       </Box>

       <ReactECharts option={option} style={{ height: 250 }} />

       <Box sx={{ mt: 3, p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1 }}>
          <Typography variant="caption" color="primary" fontWeight={900} display="block" gutterBottom>AI STATE AT GENERATION</Typography>
          <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
             At {new Date(signal.timestamp).toLocaleTimeString()}, the **MarketAnalyst** detected a bullish CHoCH at ₹{signal.entry_price * 0.99}.
             Consensus was reached with **{signal.conviction}% Conviction** based on institutional buy-side pressure.
          </Typography>
       </Box>
    </Paper>
  );
}
