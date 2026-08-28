import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Grid, Stack, Tab, Tabs, Button, Divider, InputBase, alpha, IconButton, Paper, Skeleton } from '@mui/material';
import { Zap, Clock, ShieldAlert, RefreshCw, Search, Info } from 'lucide-react';
import { getStocks, getLiveSignalsAudit } from '../api/client';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';
import { useTurboSync } from '../hooks/useTurboSync';
import LiveSignalCard from '../components/Research/shared/LiveSignalCard';

export default function OptionsSignals() {
  const [tfTab, setTfTab] = useState(0); // Default to SWING (index 0) for Options
  const [stocks, setStocks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const { connectionStatus } = useTurboSync();

  const timeframes = [
    { label: 'SWING', value: 'SWING' },
    { label: 'INTRADAY', value: 'INTRADAY' }
  ];

  const fetchData = async () => {
    setLoading(true);
    try {
      const [stocksData, liveSignalsData] = await Promise.all([
        getStocks(),
        getLiveSignalsAudit()
      ]);

      const stockMap = new Map((stocksData || []).map((s: any) => [s.symbol, s]));

      const normalizedLive = (liveSignalsData || [])
        .filter((ls: any) => ls.asset_class === 'OPTIONS')
        .map((ls: any) => {
          const stockInfo = stockMap.get(ls.symbol) || {};
          return {
            ...stockInfo,
            ...ls,
            decision: normalizeAITradeDecision({...stockInfo, ...ls})
          };
        });

      const combined = normalizedLive.sort((a: any, b: any) => {
          const timeA = new Date(a.decision?.generatedAt || a.timestamp || 0).getTime();
          const timeB = new Date(b.decision?.generatedAt || b.timestamp || 0).getTime();
          return timeB - timeA;
      });

      setStocks(combined);
    } catch (e) {
      console.error("Failed to sync options signals:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredSignals = useMemo(() => {
    const currentTf = timeframes[tfTab].value;

    return stocks.filter(s => {
        const matchesTf = s.decision?.timeframe === currentTf;
        const isTradeable = (s.decision?.rating?.includes('BUY') || s.decision?.rating?.includes('SELL'));
        const matchesSearch = s.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
                             (s.underlying_symbol?.toLowerCase().includes(searchQuery.toLowerCase()));

        const isNotResolved = !['TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'COMPLETED', 'CANCELLED'].includes(s.decision?.status);

        return matchesTf && isTradeable && matchesSearch && isNotResolved;
    });
  }, [stocks, tfTab, searchQuery]);

  return (
    <Box sx={{ pb: 10, bgcolor: '#020617', minHeight: '100vh', mx: -4, px: 4, pt: 2 }}>
      {/* 1. Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', mb: 5, flexWrap: 'wrap', gap: 3 }}>
         <Box>
            <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1, color: '#fff' }}>OPTIONS TERMINAL</Typography>
            <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
               <Typography variant="caption" sx={{ fontWeight: 900, color: '#7C3AED', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Zap size={14} /> PREMIUM FLOW STREAM
               </Typography>
               <Divider orientation="vertical" flexItem sx={{ height: 12, my: 'auto', bgcolor: 'rgba(255,255,255,0.1)' }} />
               <Typography variant="caption" sx={{ fontWeight: 800, color: connectionStatus === 'ONLINE' ? '#10b981' : '#ef4444' }}>
                  NODE: {connectionStatus}
               </Typography>
            </Stack>
         </Box>

         <Stack direction="row" spacing={2} alignItems="center">
            <Box sx={{
               display: 'flex',
               alignItems: 'center',
               bgcolor: '#0f172a',
               border: '1px solid rgba(255,255,255,0.08)',
               borderRadius: 1,
               px: 2,
               width: { xs: '100%', sm: 320 },
               height: 48,
               transition: '0.2s',
               '&:focus-within': { borderColor: '#7C3AED', bgcolor: '#111827', boxShadow: '0 0 0 2px rgba(124, 58, 237, 0.1)' }
            }}>
               <Search size={18} color="slategray" />
               <InputBase
                  placeholder="FILTER BY STRIKE..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  sx={{ ml: 1.5, flex: 1, fontSize: '0.8rem', fontWeight: 800, color: 'white' }}
               />
            </Box>
            <IconButton onClick={fetchData} sx={{ border: '1px solid rgba(255,255,255,0.08)', borderRadius: 1, p: 1.5, bgcolor: '#0f172a' }}>
               <RefreshCw size={20} className={loading ? 'animate-spin' : ''} color="slategray" />
            </IconButton>
         </Stack>
      </Box>

      {/* 2. Timeframe Navigation */}
      <Paper sx={{ mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 1, p: 0.5 }}>
         <Tabs
            value={tfTab}
            onChange={(_, v) => setTfTab(v)}
            sx={{
               minHeight: 48,
               '& .MuiTabs-indicator': { height: 2, bgcolor: '#7C3AED' },
               '& .MuiTab-root': {
                  color: 'slategray',
                  fontWeight: 950,
                  fontSize: '0.75rem',
                  minWidth: 160,
                  textTransform: 'none',
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
               />
            ))}
         </Tabs>
      </Paper>

      {/* 3. Main Data Grid */}
      {loading ? (
         <Grid container spacing={3}>
            {[1,2,3,4,5,6].map(i => (
               <Grid item xs={12} md={6} lg={4} key={i}>
                  <Skeleton variant="rectangular" height={420} sx={{ borderRadius: 1, bgcolor: 'rgba(255,255,255,0.02)' }} />
               </Grid>
            ))}
         </Grid>
      ) : (
         <Box>
            {filteredSignals.length > 0 ? (
               <Grid container spacing={3}>
                  {filteredSignals.map((s) => (
                     <Grid item xs={12} md={6} lg={4} key={s.id || s.symbol}>
                        <LiveSignalCard stock={s} decision={s.decision} />
                     </Grid>
                  ))}
               </Grid>
            ) : (
               <Paper sx={{ py: 20, textAlign: 'center', bgcolor: alpha('#0f172a', 0.5), border: '1px dashed rgba(255,255,255,0.05)', borderRadius: 1 }}>
                  <ShieldAlert size={56} color="slategray" style={{ margin: '0 auto 24px', opacity: 0.2 }} />
                  <Typography variant="h6" sx={{ fontWeight: 900, color: 'slategray', letterSpacing: 1 }}>NO ACTIVE OPTIONS SIGNALS</Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 1, opacity: 0.5, fontWeight: 700 }}>Premium decay scanners identifying {timeframes[tfTab].label} opportunities...</Typography>
                  <Button
                    variant="text"
                    size="small"
                    sx={{ mt: 4, fontWeight: 900, color: '#7C3AED', textTransform: 'none' }}
                    onClick={() => {setSearchQuery(''); setTfTab(0);}}
                  >
                    RESET ALL FILTERS
                  </Button>
               </Paper>
            )}
         </Box>
      )}

      {/* 4. Terminal Metadata */}
      <Box sx={{ mt: 10, p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1 }}>
         <Stack direction="row" spacing={3} alignItems="flex-start">
            <Box sx={{ bgcolor: alpha('#7C3AED', 0.1), p: 1, borderRadius: 1 }}>
               <Info size={20} color="#7C3AED" />
            </Box>
            <Box>
               <Typography variant="subtitle2" sx={{ fontWeight: 950, color: '#fff', mb: 0.5, letterSpacing: 1 }}>OPTIONS PREMIUM FIDELITY</Typography>
               <Typography variant="caption" sx={{ color: 'slategray', lineHeight: 1.6, display: 'block', fontWeight: 600 }}>
                  Options signals focus on gamma breakouts and institutional hedging floors.
                  All entry/stop levels refer to the contract premium, not the underlying spot price.
                  Win rates are calculated based on the actual percentage return of the traded premium.
               </Typography>
            </Box>
         </Stack>
      </Box>
    </Box>
  );
}
