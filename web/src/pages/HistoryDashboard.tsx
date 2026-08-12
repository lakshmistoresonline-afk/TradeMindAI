import { useState } from 'react';
import { Box, Typography, Paper, Tab, Tabs } from '@mui/material';
import { History, Activity, BarChart2 } from 'lucide-react';
import SignalValidation from './StrategyBuilder/SignalValidation';

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
         {/* SignalValidation handles Signal History (tab 1) and Performance (tab 0) internal logic */}
         {/* We wrap it to match the new consolidated structure */}
         {activeTab === 0 && <SignalValidation isConsolidated initialTab={1} />}
         {activeTab === 1 && <SignalValidation isConsolidated initialTab={0} />}
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
