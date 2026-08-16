import { useEffect, useState } from 'react';
import { Box, Typography, Paper, ToggleButton, ToggleButtonGroup } from '@mui/material';
import ReactECharts from 'echarts-for-react';
import { getStocks } from '../../api/client';

export default function MarketTreemap() {
  const [stocks, setStocks] = useState<any[]>([]);
  const [mode, setMode] = useState('change'); // 'change' or 'market_cap'

  useEffect(() => {
    getStocks().then(setStocks);
  }, []);

  const formatData = () => {
    const sectors: any = {};
    stocks.forEach(s => {
      if (!s.sector) return;
      if (!sectors[s.sector]) sectors[s.sector] = [];
      sectors[s.sector].push({
        name: s.symbol,
        value: mode === 'market_cap' ? s.market_cap : Math.abs(s.change_pct || 0),
        change: s.change_pct || 0
      });
    });

    return Object.keys(sectors).map(name => ({
      name,
      children: sectors[name]
    }));
  };

  const option = {
    tooltip: {
      formatter: (info: any) => {
        const { data } = info;
        return `
          <div style="font-weight:bold">${data.name}</div>
          Change: <span style="color:${data.change >= 0 ? '#10b981' : '#ef4444'}">${data.change}%</span>
        `;
      }
    },
    series: [{
      type: 'treemap',
      data: formatData(),
      breadcrumb: { show: false },
      label: {
        show: true,
        formatter: '{b}'
      },
      itemStyle: {
        borderColor: '#0f172a',
        gapWidth: 2
      },
      levels: [
        {
          itemStyle: { borderColor: '#1e293b', borderWidth: 2, gapWidth: 2 }
        },
        {
          colorSaturation: [0.35, 0.5],
          itemStyle: { borderWidth: 1, gapWidth: 1, borderColorSaturation: 0.6 }
        }
      ]
    }]
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4 }}>
        <Typography variant="h4" fontWeight="bold">Market Treemap</Typography>
        <ToggleButtonGroup
          value={mode}
          exclusive
          onChange={(_, val) => val && setMode(val)}
          size="small"
        >
          <ToggleButton value="change">By Performance</ToggleButton>
          <ToggleButton value="market_cap">By Market Cap</ToggleButton>
        </ToggleButtonGroup>
      </Box>
      <Paper sx={{ p: 0, height: '70vh', overflow: 'hidden' }}>
        <ReactECharts option={option} style={{ height: '100%', width: '100%' }} theme="dark" />
      </Paper>
    </Box>
  );
}
