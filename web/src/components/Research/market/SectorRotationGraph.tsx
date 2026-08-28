import { Box, Typography, Paper } from '@mui/material';
import ReactECharts from 'echarts-for-react';
import { Target } from 'lucide-react';

export default function SectorRotationGraph() {
  const sectors = [
    { name: 'Nifty IT', x: 102.5, y: 101.2, status: 'LEADING' },
    { name: 'Nifty Bank', x: 98.4, y: 99.1, status: 'LAGGING' },
    { name: 'Nifty Auto', x: 101.2, y: 98.5, status: 'WEAKENING' },
    { name: 'Nifty FMCG', x: 99.5, y: 102.1, status: 'IMPROVING' },
    { name: 'Nifty Pharma', x: 100.8, y: 100.5, status: 'LEADING' },
  ];

  const option = {
    title: { text: 'Sector Relative Rotation (RRG)', left: 'center', textStyle: { color: '#94a3b8', fontSize: 12, fontWeight: 800 } },
    tooltip: { trigger: 'item', formatter: '{b}' },
    xAxis: {
        name: 'RS-Ratio',
        min: 95, max: 105,
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
        axisLabel: { color: '#64748b' }
    },
    yAxis: {
        name: 'RS-Momentum',
        min: 95, max: 105,
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
        axisLabel: { color: '#64748b' }
    },
    series: [{
      data: sectors.map(s => [s.x, s.y, s.name]),
      type: 'scatter',
      symbolSize: 12,
      label: { show: true, position: 'top', color: '#fff', fontSize: 10, formatter: (param: any) => param.data[2] },
      itemStyle: {
        color: (param: any) => {
            const x = param.data[0];
            const y = param.data[1];
            if (x >= 100 && y >= 100) return '#10b981'; // Leading
            if (x < 100 && y >= 100) return '#3b82f6'; // Improving
            if (x < 100 && y < 100) return '#f43f5e'; // Lagging
            return '#fbbf24'; // Weakening
        }
      }
    }],
    grid: { top: 60, bottom: 40, left: 50, right: 30 }
  };

  return (
    <Paper sx={{ p: 3, border: '1px solid #1e293b', bgcolor: 'rgba(15, 23, 42, 0.3)' }}>
       <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
          <Target size={18} className="text-emerald-500" />
          <Typography variant="subtitle2" fontWeight={900}>RELATIVE ROTATION VELOCITY</Typography>
       </Box>
       <ReactECharts option={option} style={{ height: 350 }} />

       <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between', px: 4 }}>
          <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 800 }}>LEADING</Typography>
          <Typography variant="caption" sx={{ color: '#3b82f6', fontWeight: 800 }}>IMPROVING</Typography>
          <Typography variant="caption" sx={{ color: '#f43f5e', fontWeight: 800 }}>LAGGING</Typography>
          <Typography variant="caption" sx={{ color: '#fbbf24', fontWeight: 800 }}>WEAKENING</Typography>
       </Box>
    </Paper>
  );
}
