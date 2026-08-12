import { useState } from 'react';
import { Box, Typography, Paper, Tab, Tabs } from '@mui/material';
import { Wallet, Briefcase, ShieldCheck, History } from 'lucide-react';
import Portfolio from './Portfolio';
import RiskGuard from './RiskGuard';
import Journal from './Journal';

export default function PortfolioDashboard() {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
         <Typography variant="h4" sx={{ fontWeight: 900 }}>Portfolio Hub</Typography>
         <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>INSTITUTIONAL RISK WATCH & PERFORMANCE MEMORY</Typography>
      </Box>

      <Paper sx={{ mb: 4, bgcolor: 'transparent', border: 'none' }}>
         <Tabs
            value={activeTab}
            onChange={(_, v) => setActiveTab(v)}
            indicatorColor="primary"
            sx={{ borderBottom: '1px solid #1e293b' }}
         >
            <Tab label="OVERVIEW" icon={<Wallet size={18} />} iconPosition="start" sx={{ fontWeight: 800, minHeight: 60 }} />
            <Tab label="HOLDINGS" icon={<Briefcase size={18} />} iconPosition="start" sx={{ fontWeight: 800, minHeight: 60 }} />
            <Tab label="RISK" icon={<ShieldCheck size={18} />} iconPosition="start" sx={{ fontWeight: 800, minHeight: 60 }} />
            <Tab label="MY PERFORMANCE" icon={<History size={18} />} iconPosition="start" sx={{ fontWeight: 800, minHeight: 60 }} />
         </Tabs>
      </Paper>

      <Box>
         {activeTab === 0 && <Portfolio isOverviewOnly />}
         {activeTab === 1 && <Portfolio isHoldingsOnly />}
         {activeTab === 2 && <RiskGuard isConsolidated />}
         {activeTab === 3 && <Journal />}
      </Box>
    </Box>
  );
}
