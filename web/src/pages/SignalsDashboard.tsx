import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Grid, Stack, Tab, Tabs, Button, CircularProgress, Divider, InputBase, alpha, IconButton, Tooltip } from '@mui/material';
import { Zap, Clock, ShieldAlert, RefreshCw, Search, Activity, LayoutGrid, List } from 'lucide-react';
import { getStocks, getOpportunities, getLiveSignalsAudit } from '../api/client';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';
import { useTurboSync } from '../hooks/useTurboSync';
import LiveSignalCard from '../components/Research/shared/LiveSignalCard';
import LiveSignalsBoard from '../components/Research/shared/LiveSignalsBoard';

export default function SignalsDashboard() {
  const [activeTab, setActiveTab] = useState(2); // Default to SWING (index 2)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [stocks, setStocks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const { connectionStatus } = useTurboSync();

  const timeframes = [
    { label: 'INTRADAY', value: 'INTRADAY' },
    { label: 'SHORT TERM', value: 'SHORT TERM' },
    { label: 'SWING', value: 'SWING' },
    { label: 'LONG TERM', value: 'LONG TERM' }
  ];

  const fetchData = async () => {
    setLoading(true);
    try {
      const [stocksData, oppsData, liveSignalsData] = await Promise.all([
        getStocks(),
        getOpportunities(),
        getLiveSignalsAudit()
      ]);

      const stockMap = new Map(stocksData.map((s: any) => [s.symbol, s]));

      // 1. Normalize Live Signals (can have multiple per symbol)
      const normalizedLive = liveSignalsData.map((ls: any) => {
        const stockInfo = stockMap.get(ls.symbol) || {};
        return {
          ...stockInfo,
          ...ls,
          id: ls.id,
          decision: normalizeAITradeDecision({...stockInfo, ...ls})
        };
      });

      // 2. Filter out symbols that already have a live signal to avoid duplicates
      // when merging with the general stocks list (which has analysis field)
      const liveSymbols = new Set(normalizedLive.map((s: any) => s.symbol));

      const normalizedStocks = stocksData
        .filter((s: any) => !liveSymbols.has(s.symbol))
        .map((s: any) => ({
          ...s,
          decision: normalizeAITradeDecision(s)
        }));

      // 3. Combined list includes ALL live signals + analyzed stocks without active live signals
      setStocks([...normalizedLive, ...normalizedStocks]);
      console.log("Opps fetched:", oppsData.length);
    } catch (e) {
      console.error("Failed to sync signals:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredSignals = useMemo(() => {
    const currentTf = timeframes[activeTab].value;

    return stocks.filter(s => {
        const matchesTf = s.decision?.timeframe === currentTf;
        const isTradeable = (s.decision?.rating?.includes('BUY') || s.decision?.rating?.includes('SELL'));
        const matchesSearch = s.symbol.toLowerCase().includes(searchQuery.toLowerCase());
        const isNotResolved = !['TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'COMPLETED'].includes(s.decision?.status);
        return matchesTf && isTradeable && matchesSearch && isNotResolved;
    }).sort((a,b) => (b.decision?.conviction || 0) - (a.decision?.conviction || 0));
  }, [stocks, activeTab, searchQuery]);

  return (
    <Box sx={{ pb: 10 }}>
      {/* Header Tier - Modern Institutional Design */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 5, flexWrap: 'wrap', gap: 3 }}>
         <Box>
            <Typography variant="h3" sx={{ fontWeight: 900, letterSpacing: -1, color: 'white' }}>
               Signal Command Center
            </Typography>
            <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
               <Typography variant="caption" color="primary" sx={{ fontWeight: 900, letterSpacing: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Zap size={14} /> AI-POWERED TERMINAL
               </Typography>
               <Divider orientation="vertical" flexItem sx={{ height: 12, my: 'auto', bgcolor: 'rgba(255,255,255,0.1)' }} />
               <Typography variant="caption" sx={{ fontWeight: 800, color: 'secondary.main', display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Activity size={14} /> {filteredSignals.length} LIVE OPPORTUNITIES
               </Typography>
               <Divider orientation="vertical" flexItem sx={{ height: 12, my: 'auto', bgcolor: 'rgba(255,255,255,0.1)' }} />
               <Typography variant="caption" sx={{ fontWeight: 800, color: connectionStatus === 'ONLINE' ? 'success.main' : 'error.main' }}>
                  {connectionStatus}
               </Typography>
            </Stack>
         </Box>

         <Stack direction="row" spacing={2} alignItems="center">
            {/* Search Component */}
            <Box sx={{
               display: 'flex',
               alignItems: 'center',
               bgcolor: '#0C1118',
               border: '1px solid rgba(255,255,255,0.05)',
               borderRadius: 2,
               px: 2,
               width: { xs: '100%', sm: 280 },
               height: 44,
               transition: '0.2s',
               '&:focus-within': { borderColor: 'primary.main', bgcolor: '#111821' }
            }}>
               <Search size={16} color="#64748b" />
               <InputBase
                  placeholder="SEARCH INSTRUMENTS..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  sx={{ ml: 1.5, flex: 1, fontSize: '0.75rem', fontWeight: 800, color: 'white' }}
               />
            </Box>

            <Stack direction="row" spacing={1} sx={{ bgcolor: '#0C1118', p: 0.5, borderRadius: 2, border: '1px solid rgba(255,255,255,0.05)' }}>
               <Tooltip title="Grid View">
                  <IconButton
                     onClick={() => setViewMode('grid')}
                     sx={{
                        borderRadius: 1.5,
                        p: 1,
                        color: viewMode === 'grid' ? 'primary.main' : 'text.secondary',
                        bgcolor: viewMode === 'grid' ? 'rgba(0, 209, 255, 0.1)' : 'transparent'
                     }}
                  >
                     <LayoutGrid size={18} />
                  </IconButton>
               </Tooltip>
               <Tooltip title="List View">
                  <IconButton
                     onClick={() => setViewMode('list')}
                     sx={{
                        borderRadius: 1.5,
                        p: 1,
                        color: viewMode === 'list' ? 'primary.main' : 'text.secondary',
                        bgcolor: viewMode === 'list' ? 'rgba(0, 209, 255, 0.1)' : 'transparent'
                     }}
                  >
                     <List size={18} />
                  </IconButton>
               </Tooltip>
            </Stack>

            <IconButton
               onClick={fetchData}
               sx={{ border: '1px solid rgba(255,255,255,0.05)', borderRadius: 2, p: 1.5, '&:hover': { bgcolor: '#111821', borderColor: 'primary.main' } }}
            >
               <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
            </IconButton>
         </Stack>
      </Box>

      {/* Timeframe Navigation - Institutional Tabs */}
      <Box sx={{ position: 'sticky', top: 64, zIndex: 10, bgcolor: alpha('#070A0F', 0.9), backdropFilter: 'blur(12px)', mx: -3, px: 3, mb: 4, borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
         <Tabs
            value={activeTab}
            onChange={(_, v) => setActiveTab(v)}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
               minHeight: 60,
               '& .MuiTabs-indicator': { height: 3, borderRadius: '3px 3px 0 0', bgcolor: 'primary.main' },
               '& .MuiTab-root': {
                  color: '#64748b',
                  fontWeight: 800,
                  fontSize: '0.7rem',
                  minWidth: 160,
                  transition: '0.2s',
                  '&.Mui-selected': { color: 'white' }
               }
            }}
         >
            {timeframes.map((tf) => (
               <Tab
                  key={tf.label}
                  label={tf.label}
                  icon={<Clock size={14} />}
                  iconPosition="start"
                  sx={{ letterSpacing: 1.5 }}
               />
            ))}
         </Tabs>
      </Box>

      {loading ? (
         <Box sx={{ py: 20, textAlign: 'center' }}>
            <CircularProgress size={40} thickness={4} sx={{ color: 'primary.main', mb: 3 }} />
            <Typography sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 2, fontSize: '0.7rem' }}>
               SYNTHESIZING MARKET DATA...
            </Typography>
         </Box>
      ) : (
         <Box>
            {viewMode === 'grid' ? (
               <Grid container spacing={3}>
                  {filteredSignals.length > 0 ? filteredSignals.map((s) => (
                     <Grid item xs={12} md={6} lg={4} key={s.id || s.symbol}>
                        <LiveSignalCard stock={s} decision={s.decision} />
                     </Grid>
                  )) : (
                     <Grid item xs={12}>
                        <Box sx={{ py: 15, textAlign: 'center', bgcolor: 'rgba(255,255,255,0.01)', border: '1px dashed rgba(255,255,255,0.05)', borderRadius: 4 }}>
                           <ShieldAlert size={48} color="#334155" style={{ margin: '0 auto 20px' }} />
                           <Typography variant="h6" fontWeight={800} color="textSecondary">No Validated {timeframes[activeTab].label} Setups</Typography>
                           <Typography variant="body2" color="textSecondary" sx={{ mt: 1, opacity: 0.5 }}>The multi-agent consensus has not identified high-probability entries for this timeframe.</Typography>
                           <Button variant="outlined" sx={{ mt: 4, borderRadius: 2 }} onClick={() => setSearchQuery('')}>RESET FILTERS</Button>
                        </Box>
                     </Grid>
                  )}
               </Grid>
            ) : (
               <LiveSignalsBoard stocks={filteredSignals} />
            )}
         </Box>
      )}
    </Box>
  );
}
