import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Paper, Tab, Tabs, Grid, Chip, CircularProgress } from '@mui/material';
import { History, Activity, BarChart2, ShieldCheck, TrendingUp, Clock, Zap } from 'lucide-react';
import SignalValidation from './StrategyBuilder/SignalValidation';
import VarianceMap from '../components/Research/history/VarianceMap';
import { getPerformanceSummary, getPerformanceSignals } from '../api/client';
import HistoricalSignalCard from '../components/Research/shared/HistoricalSignalCard';

export default function HistoryDashboard() {
  const [assetTab, setAssetTab] = useState(0); // 0: Equity, 1: Derivatives
  const [activeTab, setActiveTab] = useState(0); // 0: Outcomes, 1: Audit, 2: Viz

  const [summary, setSummary] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [sumData, signalsData] = await Promise.all([
        getPerformanceSummary(),
        getPerformanceSignals()
      ]);
      setSummary(sumData);

      // Sort Historical Signals: created_at DESC
      const resolved = signalsData
        .filter((s: any) => !['ACTIVE', 'WAITING_FOR_ENTRY', 'ENTRY_TRIGGERED'].includes(s.status))
        .sort((a: any, b: any) => {
           const timeA = new Date(a.timestamp || a.date || 0).getTime();
           const timeB = new Date(b.timestamp || b.date || 0).getTime();
           return timeB - timeA;
        });
      setSignals(resolved);
    } catch (error) {
      console.error("Error fetching performance history:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const stats = summary?.live_signals || { total: 0, resolved: 0, win_rate: 0, avg_profit: 0 };

  const filteredSignals = useMemo(() => {
     return signals.filter(s => {
        const isDerivative = s.asset_class === 'FUTURES' || s.asset_class === 'OPTIONS';
        return assetTab === 0 ? !isDerivative : isDerivative;
     });
  }, [signals, assetTab]);

  return (
    <Box sx={{ pb: 10 }}>
      {/* Header Tier */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4 }}>
         <Box>
            <Typography variant="h3" sx={{ fontWeight: 900, letterSpacing: -1, color: 'white' }}>
               Performance Audit
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 800, color: 'text.secondary', letterSpacing: 1.5 }}>
               VERIFIED INSTITUTIONAL SIGNAL RECORD
            </Typography>
         </Box>
         <Chip
           icon={<ShieldCheck size={14} />}
           label="RECONCILIATION ACTIVE"
           variant="outlined"
           color="success"
           sx={{ fontWeight: 900, height: 32 }}
         />
      </Box>

      {/* Main Asset Class Navigation */}
      <Box sx={{ mb: 4, borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
         <Tabs
            value={assetTab}
            onChange={(_, v) => setAssetTab(v)}
            sx={{ '& .MuiTab-root': { fontWeight: 900, minWidth: 200 } }}
         >
            <Tab label="EQUITY HISTORY" icon={<Activity size={18} />} iconPosition="start" />
            <Tab label="DERIVATIVE HISTORY" icon={<Zap size={18} />} iconPosition="start" />
         </Tabs>
      </Box>

      {/* Aggregate Stats Tier */}
      <Grid container spacing={3} sx={{ mb: 5 }}>
         <Grid item xs={12} md={3}>
            <SummaryCard label="TOTAL RESOLVED" value={filteredSignals.length} subValue="Audited Signals" icon={<History size={20} />} color="#3b82f6" />
         </Grid>
         <Grid item xs={12} md={3}>
            <SummaryCard label="WIN RATE" value={`${stats.win_rate}%`} subValue="System Accuracy" icon={<ShieldCheck size={20} />} color="#10b981" />
         </Grid>
         <Grid item xs={12} md={3}>
            <SummaryCard label="AVG PROFIT" value={`+${stats.avg_profit}%`} subValue="Per Successful setup" icon={<TrendingUp size={20} />} color="#00D1FF" />
         </Grid>
         <Grid item xs={12} md={3}>
            <SummaryCard label="AUDIT PERIOD" value="ALL" subValue={`Since ${new Date(summary?.earliest_recorded_date || '').toLocaleDateString()}`} icon={<Clock size={20} />} color="#7C3AED" />
         </Grid>
      </Grid>

      <Paper sx={{ mb: 4, bgcolor: 'transparent', border: 'none' }}>
         <Tabs
            value={activeTab}
            onChange={(_, v) => setActiveTab(v)}
            sx={{
               borderBottom: '1px solid rgba(255,255,255,0.05)',
               '& .MuiTab-root': { minWidth: 200, fontWeight: 900, fontSize: '0.75rem' }
            }}
         >
            <Tab label="OUTCOME LOG" icon={<History size={18} />} iconPosition="start" />
            <Tab label="ACCURACY AUDIT" icon={<Activity size={18} />} iconPosition="start" />
            <Tab label="DATA VISUALIZATION" icon={<BarChart2 size={18} />} iconPosition="start" />
         </Tabs>
      </Paper>

      {loading ? (
         <Box sx={{ py: 10, textAlign: 'center' }}>
            <CircularProgress size={30} sx={{ mb: 2 }} />
            <Typography variant="caption" display="block" sx={{ fontWeight: 800 }}>RECONCILING HISTORICAL DATA...</Typography>
         </Box>
      ) : (
         <Box>
            {activeTab === 0 && (
               <Grid container spacing={2}>
                  {filteredSignals.length > 0 ? filteredSignals.map((sig, idx) => (
                     <Grid item xs={12} md={6} lg={4} key={sig.id || idx}>
                        <HistoricalSignalCard signal={sig} />
                     </Grid>
                  )) : (
                     <Grid item xs={12}>
                        <Paper sx={{ py: 10, textAlign: 'center', border: '1px dashed rgba(255,255,255,0.05)' }}>
                            <Typography color="textSecondary" sx={{ fontWeight: 700 }}>NO RESOLVED {assetTab === 0 ? 'EQUITY' : 'DERIVATIVE'} SIGNALS</Typography>
                        </Paper>
                     </Grid>
                  )}
               </Grid>
            )}
            {activeTab === 1 && <SignalValidation isConsolidated initialTab={0} />}
            {activeTab === 2 && (
               <Grid container spacing={3}>
                  <Grid item xs={12} lg={8}>
                     <SignalValidation isConsolidated initialTab={0} />
                  </Grid>
                  <Grid item xs={12} lg={4}>
                     <VarianceMap />
                  </Grid>
               </Grid>
            )}
         </Box>
      )}
    </Box>
  );
}

function SummaryCard({ label, value, subValue, icon, color }: any) {
  return (
    <Paper sx={{ p: 3, border: '1px solid rgba(255,255,255,0.05)', bgcolor: '#0C1118' }}>
       <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="caption" sx={{ fontWeight: 900, color: 'text.secondary', letterSpacing: 1 }}>{label}</Typography>
          <Box sx={{ color }}>{icon}</Box>
       </Box>
       <Typography variant="h4" fontWeight={900} sx={{ mb: 0.5 }}>{value}</Typography>
       <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>{subValue}</Typography>
    </Paper>
  );
}
