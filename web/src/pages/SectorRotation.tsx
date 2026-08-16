import { useEffect, useState } from 'react';
import { Box, Typography, Grid, Paper, LinearProgress, Chip, Stack } from '@mui/material';
import { PieChart, TrendingUp, TrendingDown, Users } from 'lucide-react';
import ReactECharts from 'echarts-for-react';
import { getStocks } from '../api/client';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';

export default function SectorRotation() {
  const [sectorPerformance, setSectorPerformance] = useState<any>({});

  useEffect(() => {
    getStocks().then(data => {
      const sectors: any = {};
      data.forEach((stock: any) => {
        if (!stock.sector) return;
        const decision = normalizeAITradeDecision(stock);
        if (!sectors[stock.sector]) sectors[stock.sector] = { count: 0, bullish: 0, change: [], conviction: [] };
        sectors[stock.sector].count += 1;
        if (decision.rating.includes('BUY')) sectors[stock.sector].bullish += 1;
        if (stock.change_pct) sectors[stock.sector].change.push(stock.change_pct);
        sectors[stock.sector].conviction.push(decision.conviction);
      });
      setSectorPerformance(sectors);
    });
  }, []);

  const chartOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { textStyle: { color: '#fff' }, top: 0 },
    xAxis: { type: 'category', data: Object.keys(sectorPerformance), axisLabel: { color: '#94a3b8', rotate: 30 } },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8' } },
    grid: { bottom: 80, top: 40 },
    series: [
      {
        name: 'AI Bullish Strength (%)',
        type: 'bar',
        data: Object.keys(sectorPerformance).map(k => (sectorPerformance[k].bullish / sectorPerformance[k].count) * 100),
        color: '#10b981'
      },
      {
        name: 'Institutional Flow Bias',
        type: 'line',
        data: Object.keys(sectorPerformance).map(k => {
           const changes = sectorPerformance[k].change;
           return changes.length > 0 ? (changes.reduce((a:any, b:any) => a + b, 0) / changes.length) * 10 : 0;
        }),
        color: '#3b82f6',
        smooth: true
      }
    ]
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
         <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <PieChart size={32} className="text-emerald-500" />
            <Typography variant="h4" sx={{ fontWeight: 900 }}>Sector Rotation</Typography>
         </Box>
         <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>
            INSTITUTIONAL FLOW MAP: {new Date().toLocaleDateString(undefined, { month: 'short', year: 'numeric' }).toUpperCase()}
         </Typography>
      </Box>

      <Paper sx={{ p: 4, mb: 4, height: 450, border: '1px solid #1e293b' }}>
         <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ fontWeight: 800 }}>CROSS-SECTOR STRENGTH ANALYSIS</Typography>
         <ReactECharts option={chartOption} style={{ height: '90%' }} theme="dark" />
      </Paper>

      <Grid container spacing={3}>
        {Object.keys(sectorPerformance).sort((a,b) => (sectorPerformance[b].bullish/sectorPerformance[b].count) - (sectorPerformance[a].bullish/sectorPerformance[a].count)).map((sector) => {
          const strength = (sectorPerformance[sector].bullish / sectorPerformance[sector].count) * 100;
          const avgConviction = sectorPerformance[sector].conviction.reduce((a:any,b:any)=>a+b,0) / sectorPerformance[sector].count;
          const avgReturn = sectorPerformance[sector].change.reduce((a:any,b:any)=>a+b,0) / sectorPerformance[sector].count;

          return (
            <Grid item xs={12} md={4} key={sector}>
              <Paper sx={{ p: 3, border: '1px solid #1e293b', transition: '0.2s', '&:hover': { borderColor: 'primary.main', bgcolor: 'rgba(16, 185, 129, 0.02)' } }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box>
                     <Typography variant="h6" fontWeight={900}>{sector}</Typography>
                     <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>{sectorPerformance[sector].count} ASSETS ANALYZED</Typography>
                  </Box>
                  <Chip
                    label={strength > 60 ? 'LEADERSHIP' : strength < 30 ? 'LAGGING' : 'ACCUMULATING'}
                    size="small"
                    color={strength > 60 ? 'primary' : strength < 30 ? 'error' : 'default'}
                    sx={{ fontWeight: 900, fontSize: '0.6rem' }}
                  />
                </Box>

                <Stack spacing={2}>
                   <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="caption" color="textSecondary">AI BIAS STRENGTH</Typography>
                        <Typography variant="caption" fontWeight="bold" color="primary">{strength.toFixed(0)}%</Typography>
                      </Box>
                      <LinearProgress variant="determinate" value={strength} sx={{ height: 4, borderRadius: 2 }} />
                   </Box>

                   <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                         <Users size={14} className="text-slategray" />
                         <Typography variant="caption" color="textSecondary">AVG CONVICTION</Typography>
                      </Box>
                      <Typography variant="body2" fontWeight="bold">{avgConviction.toFixed(1)}%</Typography>
                   </Box>

                   <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                         {avgReturn >= 0 ? <TrendingUp size={14} className="text-emerald-500" /> : <TrendingDown size={14} className="text-rose-500" />}
                         <Typography variant="caption" color="textSecondary">RELATIVE RETURN</Typography>
                      </Box>
                      <Typography variant="body2" fontWeight="bold" color={avgReturn >= 0 ? 'primary.main' : 'error.main'}>
                         {avgReturn >= 0 ? '+' : ''}{avgReturn.toFixed(2)}%
                      </Typography>
                   </Box>
                </Stack>
              </Paper>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
}
