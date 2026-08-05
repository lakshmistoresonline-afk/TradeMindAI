import { Box, Typography, Paper, Grid, Table, TableBody, TableCell, TableHead, TableRow, Tab, Tabs } from '@mui/material';
import { useState } from 'react';
import { BarChart3, TrendingUp, DollarSign } from 'lucide-react';
import ReactECharts from 'echarts-for-react';

export default function FinancialWorkspace() {
  const [tab, setTab] = useState(0);

  const revenueOption = {
    xAxis: { type: 'category', data: ['2022', '2023', '2024', '2025', '2026'] },
    yAxis: { type: 'value' },
    series: [
      { name: 'Revenue', type: 'bar', data: [12000, 14500, 18200, 21000, 24500], color: '#10b981' },
      { name: 'Net Profit', type: 'line', data: [1200, 1800, 2400, 3100, 3800], color: '#3b82f6' }
    ],
    legend: { show: true, textStyle: { color: '#fff' } },
    grid: { top: 40, bottom: 40, left: 60, right: 20 }
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <DollarSign size={20} className="text-emerald-400" /> Financial Analysis Workspace
      </Typography>

      <Paper sx={{ p: 3 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3, borderBottom: '1px solid #334155' }}>
           <Tab label="Profit & Loss" />
           <Tab label="Balance Sheet" />
           <Tab label="Cash Flow" />
           <Tab label="Capital Allocation" />
        </Tabs>

        <Grid container spacing={4}>
           <Grid item xs={12} md={7}>
              <Box sx={{ height: 350 }}>
                 <Typography variant="subtitle2" color="textSecondary" gutterBottom>HISTORICAL FINANCIAL PERFORMANCE (INR CR)</Typography>
                 <ReactECharts option={revenueOption} style={{ height: '300px' }} theme="dark" />
              </Box>
           </Grid>

           <Grid item xs={12} md={5}>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom>KEY RATIO TRENDS</Typography>
              <Table size="small">
                 <TableHead>
                    <TableRow>
                       <TableCell>Metric</TableCell>
                       <TableCell align="right">FY25</TableCell>
                       <TableCell align="right">FY26</TableCell>
                    </TableRow>
                 </TableHead>
                 <TableBody>
                    <TableRow>
                       <TableCell>Operating Margin</TableCell>
                       <TableCell align="right">18.4%</TableCell>
                       <TableCell align="right" sx={{ color: 'primary.main', fontWeight: 'bold' }}>21.2%</TableCell>
                    </TableRow>
                    <TableRow>
                       <TableCell>Net Profit Margin</TableCell>
                       <TableCell align="right">12.5%</TableCell>
                       <TableCell align="right" sx={{ color: 'primary.main', fontWeight: 'bold' }}>14.8%</TableCell>
                    </TableRow>
                    <TableRow>
                       <TableCell>Asset Turnover</TableCell>
                       <TableCell align="right">1.2x</TableCell>
                       <TableCell align="right">1.4x</TableCell>
                    </TableRow>
                    <TableRow>
                       <TableCell>Inventory Days</TableCell>
                       <TableCell align="right">42</TableCell>
                       <TableCell align="right">38</TableCell>
                    </TableRow>
                 </TableBody>
              </Table>
           </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}
