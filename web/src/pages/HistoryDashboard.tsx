import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Paper, Tab, Tabs, Grid, Stack, IconButton, alpha, Skeleton, Divider, Button } from '@mui/material';
import { History, Activity, BarChart2, ShieldCheck, TrendingUp, Zap, RefreshCw, FileText } from 'lucide-react';
import { getPerformanceSummary, getPerformanceSignals } from '../api/client';
import HistoricalSignalCard from '../components/Research/shared/HistoricalSignalCard';

export default function HistoryDashboard() {
  const [assetTab, setAssetTab] = useState(0); // 0: Equity, 1: Futures, 2: Options
  const [activeTab, setActiveTab] = useState(0); // 0: Archive, 1: Performance

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

      const resolved = (signalsData || [])
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

  const assetTypes = ['EQUITY', 'FUTURES', 'OPTIONS'];

  const filteredSignals = useMemo(() => {
     const currentType = assetTypes[assetTab];
     return signals.filter(s => {
        const assetClass = s.asset_class || 'EQUITY';
        return assetClass === currentType;
     });
  }, [signals, assetTab]);

  return (
    <Box sx={{ pb: 10, bgcolor: '#020617', minHeight: '100vh', mx: -4, px: 4, pt: 2 }}>
      {/* 1. Archive Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 5 }}>
         <Box>
            <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1, color: '#fff' }}>AUDIT ARCHIVE</Typography>
            <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
               <Typography variant="caption" sx={{ fontWeight: 900, color: 'primary.main', display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ShieldCheck size={14} /> FORENSIC SIGNAL LOG
               </Typography>
               <Divider orientation="vertical" flexItem sx={{ height: 12, my: 'auto', bgcolor: 'rgba(255,255,255,0.1)' }} />
               <Typography variant="caption" sx={{ fontWeight: 800, color: 'slategray' }}>
                  {filteredSignals.length} RESOLVED {assetTypes[assetTab]} ENTRIES
               </Typography>
            </Stack>
         </Box>
         <IconButton onClick={fetchData} sx={{ border: '1px solid rgba(255,255,255,0.08)', borderRadius: 1, p: 1.5, bgcolor: '#0f172a' }}>
            <RefreshCw size={20} className={loading ? 'animate-spin' : ''} color="slategray" />
         </IconButton>
      </Box>

      {/* 2. Control Hub */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
         <Grid item xs={12} lg={8}>
            <Paper sx={{ bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 1, p: 0.5 }}>
               <Tabs
                  value={assetTab}
                  onChange={(_, v) => setAssetTab(v)}
                  sx={{
                      px: 1,
                      minHeight: 48,
                      '& .MuiTabs-indicator': { height: 3, borderRadius: '3px 3px 0 0' },
                      '& .MuiTab-root': {
                          fontWeight: 950,
                          fontSize: '0.8rem',
                          minWidth: 150,
                          color: 'slategray',
                          textTransform: 'none',
                          '&.Mui-selected': { color: '#fff' }
                      }
                  }}
               >
                  <Tab label="Equity History" icon={<Activity size={16} />} iconPosition="start" />
                  <Tab label="Futures History" icon={<TrendingUp size={16} />} iconPosition="start" />
                  <Tab label="Options History" icon={<Zap size={16} />} iconPosition="start" />
               </Tabs>
            </Paper>
         </Grid>
         <Grid item xs={12} lg={4}>
            <Paper sx={{ bgcolor: alpha('#10b981', 0.05), border: '1px solid rgba(16,185,129,0.15)', borderRadius: 1, p: 2, height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
               <Stack direction="row" spacing={4} alignItems="center">
                  <Box>
                     <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray', display: 'block', mb: 0.5 }}>AVG WIN RATE</Typography>
                     <Typography variant="h4" sx={{ fontWeight: 950, color: '#10b981', fontFamily: 'JetBrains Mono' }}>
                        {summary?.live_signals?.win_rate || '—'}%
                     </Typography>
                  </Box>
                  <Divider orientation="vertical" flexItem sx={{ bgcolor: 'rgba(16,185,129,0.1)' }} />
                  <Box>
                     <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray', display: 'block', mb: 0.5 }}>AVG ALPHA</Typography>
                     <Typography variant="h4" sx={{ fontWeight: 950, color: '#fff', fontFamily: 'JetBrains Mono' }}>
                        +{summary?.live_signals?.avg_profit || '—'}%
                     </Typography>
                  </Box>
               </Stack>
            </Paper>
         </Grid>
      </Grid>

      {/* 3. Main Content Area */}
      <Box sx={{ mb: 4, display: 'flex', gap: 1 }}>
         <ArchiveTabButton active={activeTab === 0} onClick={() => setActiveTab(0)} icon={<FileText size={16} />} label="Signal Audit Log" />
         <ArchiveTabButton active={activeTab === 1} onClick={() => setActiveTab(1)} icon={<BarChart2 size={16} />} label="Performance Metrics" />
      </Box>

      {/* 4. Content Matrix */}
      {loading ? (
         <Grid container spacing={3}>
            {[1,2,3,4,5,6].map(i => (
               <Grid item xs={12} md={6} lg={4} key={i}>
                  <Skeleton variant="rectangular" height={320} sx={{ borderRadius: 1, bgcolor: 'rgba(255,255,255,0.02)' }} />
               </Grid>
            ))}
         </Grid>
      ) : (
         <Box>
            {activeTab === 0 && (
               <Grid container spacing={3}>
                  {filteredSignals.length > 0 ? filteredSignals.map((sig, idx) => (
                     <Grid item xs={12} md={6} lg={4} key={sig.id || idx}>
                        <HistoricalSignalCard signal={sig} />
                     </Grid>
                  )) : (
                     <Grid item xs={12}>
                        <Paper sx={{ py: 20, textAlign: 'center', bgcolor: alpha('#0f172a', 0.5), border: '1px dashed rgba(255,255,255,0.05)', borderRadius: 1 }}>
                           <History size={56} color="slategray" style={{ margin: '0 auto 24px', opacity: 0.2 }} />
                           <Typography variant="h6" sx={{ fontWeight: 900, color: 'slategray' }}>EMPTY AUDIT LOG</Typography>
                           <Typography variant="body2" color="textSecondary" sx={{ mt: 1, opacity: 0.5, fontWeight: 700 }}>No resolved setups found for the selected instrument class.</Typography>
                        </Paper>
                     </Grid>
                  )}
               </Grid>
            )}

            {activeTab === 1 && (
               <Grid container spacing={3}>
                  <Grid item xs={12} lg={8}>
                     <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 1 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 950, mb: 4, letterSpacing: 1 }}>PERFORMANCE EVOLUTION</Typography>
                        <Box sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px dashed rgba(255,255,255,0.03)', borderRadius: 1 }}>
                           <Typography color="textSecondary" sx={{ fontWeight: 700, letterSpacing: 1.5, opacity: 0.5 }}>QUANT VISUALIZATION UNAVAILABLE</Typography>
                        </Box>
                     </Paper>
                  </Grid>
                  <Grid item xs={12} lg={4}>
                     <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 1 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 950, mb: 3, letterSpacing: 1 }}>OUTCOME RATIOS</Typography>
                        <Stack spacing={3}>
                           <OutcomeRow label="Target Hit" count={summary?.live_signals?.outcomes?.TARGET_HIT || 0} color="#10b981" total={filteredSignals.length} />
                           <OutcomeRow label="Stop Loss" count={summary?.live_signals?.outcomes?.STOP_LOSS || 0} color="#ef4444" total={filteredSignals.length} />
                           <OutcomeRow label="Expired" count={summary?.live_signals?.outcomes?.EXPIRED || 0} color="slategray" total={filteredSignals.length} />
                        </Stack>
                     </Paper>
                  </Grid>
               </Grid>
            )}
         </Box>
      )}
    </Box>
  );
}

function ArchiveTabButton({ active, onClick, icon, label }: any) {
   return (
      <Button
         onClick={onClick}
         startIcon={icon}
         sx={{
            bgcolor: active ? alpha('#00D1FF', 0.1) : 'transparent',
            color: active ? '#00D1FF' : 'slategray',
            border: `1px solid ${active ? alpha('#00D1FF', 0.2) : 'rgba(255,255,255,0.05)'}`,
            fontWeight: 950,
            fontSize: '0.7rem',
            px: 2,
            py: 1,
            borderRadius: 0.5,
            textTransform: 'none',
            letterSpacing: 0.5,
            '&:hover': { bgcolor: alpha('#fff', 0.03), borderColor: 'rgba(255,255,255,0.1)' }
         }}
      >
         {label.toUpperCase()}
      </Button>
   );
}

function OutcomeRow({ label, count, color, total }: any) {
  const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <Box>
       <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.2 }}>
          <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray', letterSpacing: 0.5 }}>{label.toUpperCase()}</Typography>
          <Typography variant="caption" sx={{ fontWeight: 950, color: '#fff' }}>{count} <span style={{ color: 'slategray', fontWeight: 700 }}>({percentage}%)</span></Typography>
       </Box>
       <Box sx={{ height: 4, width: '100%', bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 4, overflow: 'hidden' }}>
          <Box sx={{ height: '100%', width: `${percentage}%`, bgcolor: color }} />
       </Box>
    </Box>
  );
}
