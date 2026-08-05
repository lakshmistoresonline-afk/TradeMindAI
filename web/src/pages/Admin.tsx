import { Box, Typography, Paper, Grid, Chip, LinearProgress, Stack, Divider, CircularProgress, TableContainer, Table, TableHead, TableRow, TableCell, TableBody } from '@mui/material';
import ReactECharts from 'echarts-for-react';
import { getSystemEvaluation } from '../api/client';
import { useState, useEffect } from 'react';

export default function Admin() {
  const [evaluation, setEvaluation] = useState<any>(null);

  useEffect(() => {
     getSystemEvaluation().then(setEvaluation);
  }, []);

  const usageOption = {
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
    yAxis: { type: 'value' },
    series: [{ type: 'line', data: [1200, 1400, 1100, 1800, 2100], color: '#10b981', areaStyle: { opacity: 0.1 } }]
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>Enterprise Control Center</Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}><AdminStat label="Total Users" value="1,240" trend="+12%" /></Grid>
        <Grid item xs={12} md={3}><AdminStat label="AI Queries" value="48,201" trend="+8%" /></Grid>
        <Grid item xs={12} md={3}><AdminStat label="API Health" value="99.98%" trend="STABLE" color="success.main" /></Grid>
        <Grid item xs={12} md={3}><AdminStat label="Cloud Cost" value="$12.42" trend="-4%" color="warning.main" /></Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400 }}>
             <Typography variant="subtitle2" color="textSecondary" gutterBottom>SYSTEM USAGE (LAST 5 DAYS)</Typography>
             <ReactECharts option={usageOption} style={{ height: '320px' }} theme="dark" />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 400 }}>
             <Typography variant="subtitle2" color="textSecondary" gutterBottom>AGENT ACCURACY MONITOR</Typography>
             <Stack spacing={3} sx={{ mt: 4 }}>
                {evaluation?.agents.map((agent: any) => (
                   <AgentProgress key={agent.name} label={agent.name} value={agent.accuracy} />
                ))}
                {!evaluation && <CircularProgress />}
             </Stack>

             <Divider sx={{ my: 4, opacity: 0.1 }} />

             <Box sx={{ p: 2, bgcolor: 'rgba(16, 185, 129, 0.05)', borderRadius: 2, border: '1px solid #10b981' }}>
                <Typography variant="caption" fontWeight="bold" color="primary">SYSTEM STATUS</Typography>
                <Typography variant="h6" fontWeight="bold">OPERATIONAL</Typography>
                <Typography variant="caption" color="textSecondary">All 12 institutional agents online.</Typography>
             </Box>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ mt: 3, p: 3 }}>
         <Typography variant="h6" gutterBottom>Security & Audit Logs</Typography>
         <TableContainer>
            <Table size="small">
               <TableHead>
                  <TableRow>
                     <TableCell>Timestamp</TableCell>
                     <TableCell>User</TableCell>
                     <TableCell>Action</TableCell>
                     <TableCell>IP Address</TableCell>
                     <TableCell align="right">Status</TableCell>
                  </TableRow>
               </TableHead>
               <TableBody>
                  <TableRow>
                     <TableCell sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>19:42:01</TableCell>
                     <TableCell>admin@trademind.ai</TableCell>
                     <TableCell>BATCH_ANALYSIS_TRIGGER</TableCell>
                     <TableCell>106.213.12.42</TableCell>
                     <TableCell align="right"><Chip label="SUCCESS" size="small" color="success" sx={{ fontSize: '0.6rem' }} /></TableCell>
                  </TableRow>
                  <TableRow>
                     <TableCell sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>18:15:34</TableCell>
                     <TableCell>system_worker</TableCell>
                     <TableCell>ML_MODEL_RETRAIN</TableCell>
                     <TableCell>internal_ip</TableCell>
                     <TableCell align="right"><Chip label="SUCCESS" size="small" color="success" sx={{ fontSize: '0.6rem' }} /></TableCell>
                  </TableRow>
               </TableBody>
            </Table>
         </TableContainer>
      </Paper>
    </Box>
  );
}

function AdminStat({ label, value, trend, color }: any) {
  return (
    <Paper sx={{ p: 3 }}>
       <Typography variant="caption" color="textSecondary">{label}</Typography>
       <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', mt: 1 }}>
          <Typography variant="h4" fontWeight="bold">{value}</Typography>
          <Typography variant="caption" sx={{ color: color || 'primary.main', fontWeight: 'bold' }}>{trend}</Typography>
       </Box>
    </Paper>
  );
}

function AgentProgress({ label, value }: any) {
  return (
    <Box>
       <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="caption" fontWeight="bold">{label}</Typography>
          <Typography variant="caption">{value}%</Typography>
       </Box>
       <LinearProgress variant="determinate" value={value} sx={{ height: 6, borderRadius: 2 }} />
    </Box>
  );
}
