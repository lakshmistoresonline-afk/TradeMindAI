import { useState } from 'react';
import { Box, Typography, Paper, Tab, Tabs } from '@mui/material';
import { Wallet, Briefcase, ShieldCheck, History } from 'lucide-react';
import Portfolio from './Portfolio';
import RiskGuard from './RiskGuard';
import Journal from './Journal';
import HedgeCommander from '../components/Research/portfolio/HedgeCommander';
import StressLab from '../components/Research/portfolio/StressLab';
import { Grid } from '@mui/material';

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
         {activeTab === 2 && (
            <Grid container spacing={3}>
               <Grid item xs={12} lg={6}>
                  <HedgeCommander />
               </Grid>
               <Grid item xs={12} lg={6}>
                  <StressLab />
               </Grid>
               <Grid item xs={12}>
                  <RiskGuard isConsolidated />
               </Grid>
            </Grid>
         )}
         {activeTab === 3 && <Journal />}
      </Box>
    </Box>
  );
}
