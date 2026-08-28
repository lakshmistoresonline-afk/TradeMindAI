import { useState } from 'react';
import { Box, Typography, Paper, Tab, Tabs, Grid } from '@mui/material';
import { Globe, PieChart, Activity, Calendar } from 'lucide-react';
import MarketCommandCenter from './MarketCommandCenter';
import SectorRotation from './SectorRotation';
import SectorRotationGraph from '../components/Research/market/SectorRotationGraph';
import OptionsIntelligence from './Options/OptionsIntelligence';
import MacroCalendar from './Calendar/MacroCalendar';

export default function MarketDashboard() {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
         <Typography variant="h4" sx={{ fontWeight: 900 }}>Market Intelligence</Typography>
         <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>INSTITUTIONAL MACRO & CROSS-ASSET FLOW</Typography>
      </Box>

      <Paper sx={{ mb: 4, bgcolor: 'transparent', border: 'none' }}>
         <Tabs
            value={activeTab}
            onChange={(_, v) => setActiveTab(v)}
            indicatorColor="primary"
            sx={{ borderBottom: '1px solid #1e293b' }}
         >
            <Tab label="OVERVIEW" icon={<Globe size={18} />} iconPosition="start" sx={{ fontWeight: 800, minHeight: 60 }} />
            <Tab label="SECTORS" icon={<PieChart size={18} />} iconPosition="start" sx={{ fontWeight: 800, minHeight: 60 }} />
            <Tab label="OPTIONS" icon={<Activity size={18} />} iconPosition="start" sx={{ fontWeight: 800, minHeight: 60 }} />
            <Tab label="MACRO" icon={<Calendar size={18} />} iconPosition="start" sx={{ fontWeight: 800, minHeight: 60 }} />
         </Tabs>
      </Paper>

      <Box>
         {activeTab === 0 && <MarketCommandCenter isConsolidated />}
         {activeTab === 1 && (
            <Grid container spacing={3}>
               <Grid item xs={12} lg={8}>
                  <SectorRotationGraph />
               </Grid>
               <Grid item xs={12} lg={4}>
                  <SectorRotation />
               </Grid>
            </Grid>
         )}
         {activeTab === 2 && <OptionsIntelligence />}
         {activeTab === 3 && <MacroCalendar />}
      </Box>
    </Box>
  );
}
