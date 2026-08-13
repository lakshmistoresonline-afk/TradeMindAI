import { useState } from 'react';
import { Box, Typography, Paper, Tab, Tabs, Grid } from '@mui/material';
import { History, Activity, BarChart2 } from 'lucide-react';
import SignalValidation from './StrategyBuilder/SignalValidation';
import VarianceMap from '../components/Research/history/VarianceMap';

export default function HistoryDashboard() {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
         <Typography variant="h4" sx={{ fontWeight: 900 }}>History & Performance</Typography>
         <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>COMPLETE INSTITUTIONAL SIGNAL RECORD & ACCURACY AUDIT</Typography>
      </Box>

      <Paper sx={{ mb: 4, bgcolor: 'transparent', border: 'none' }}>
         <Tabs
            value={activeTab}
            onChange={(_, v) => setActiveTab(v)}
            indicatorColor="primary"
            sx={{ borderBottom: '1px solid #1e293b' }}
         >
            <Tab label="SIGNAL HISTORY" icon={<History size={18} />} iconPosition="start" sx={{ fontWeight: 800, minHeight: 60 }} />
            <Tab label="OVERALL PERFORMANCE" icon={<Activity size={18} />} iconPosition="start" sx={{ fontWeight: 800, minHeight: 60 }} />
            <Tab label="PERFORMANCE ANALYSIS" icon={<BarChart2 size={18} />} iconPosition="start" sx={{ fontWeight: 800, minHeight: 60 }} />
         </Tabs>
      </Paper>

      <Box>
         {activeTab === 0 && <SignalValidation isConsolidated initialTab={1} />}
         {activeTab === 1 && (
            <Grid container spacing={3}>
               <Grid item xs={12} lg={8}>
                  <SignalValidation isConsolidated initialTab={0} />
               </Grid>
               <Grid item xs={12} lg={4}>
                  <VarianceMap />
               </Grid>
            </Grid>
         )}
         {activeTab === 2 && (
            <Box sx={{ py: 10, textAlign: 'center', opacity: 0.5 }}>
               <BarChart2 size={48} style={{ margin: '0 auto 16px' }} />
               <Typography variant="h6">Deep Performance Analysis Engine</Typography>
               <Typography variant="body2">Cross-referencing market regimes with signal conviction levels...</Typography>
            </Box>
         )}
      </Box>
    </Box>
  );
}
