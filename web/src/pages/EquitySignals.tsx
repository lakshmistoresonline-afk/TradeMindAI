import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Grid, Stack, Tab, Tabs, Button, Divider, InputBase, alpha, IconButton, Paper, Skeleton } from '@mui/material';
import { ShieldAlert, RefreshCw, Search, Activity, Info } from 'lucide-react';
import { getEquitySignals } from '../api/client';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';
import { useTurboSync } from '../hooks/useTurboSync';
import LiveSignalCard from '../components/Research/shared/LiveSignalCard';

export default function EquitySignals() {
  const [activeTab, setActiveTab] = useState(1); // Default to SWING PRIMARY (index 1)
  const [signals, setSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const { connectionStatus } = useTurboSync();

  // Canonical Signal Universes (V2.3)
  const universes = useMemo(() => [
    { label: 'ALL ACTIVE', value: 'ALL', color: 'primary.main' },
    { label: 'SWING', value: 'SWING', color: '#10b981' },
    { label: 'SHORT', value: 'SHORT', color: 'slategray' },
    { label: 'LONG', value: 'LONG', color: '#00D1FF' }
  ], []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const signalsData = await getEquitySignals({ limit: 100 });
      const normalized = (Array.isArray(signalsData) ? signalsData : [])
        .map((s: any) => ({
          ...s,
          decision: normalizeAITradeDecision(s)
        })).sort((a: any, b: any) => {
          const timeA = new Date(a.decision?.generatedAt || 0).getTime();
          const timeB = new Date(b.decision?.generatedAt || 0).getTime();
          return timeB - timeA;
        });

      setSignals(normalized);
    } catch (e) {
      console.error("Failed to sync equity signals:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const counts = useMemo(() => {
    return {
      all: signals.length,
      swing: signals.filter(s => s.decision.timeframe === 'SWING').length,
      short: signals.filter(s => s.decision.timeframe === 'SHORT').length,
      long: signals.filter(s => s.decision.timeframe === 'LONG').length
    };
  }, [signals]);

  const filteredSignals = useMemo(() => {
    const universe = universes[activeTab].value;

    return signals.filter(s => {
        const matchesSearch = s.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
                             (s.company_name?.toLowerCase().includes(searchQuery.toLowerCase()));

        if (!matchesSearch) return false;

        if (universe === 'ALL') return true;
        if (universe === 'SWING') return s.decision.timeframe === 'SWING';
        if (universe === 'SHORT') return s.decision.timeframe === 'SHORT';
        if (universe === 'LONG') return s.decision.timeframe === 'LONG';

        return false;
    });
  }, [signals, activeTab, searchQuery, universes]);

  const latestUpdate = signals.length > 0 ? new Date(signals[0].decision?.generatedAt).toLocaleTimeString() : '—';

  return (
    <Box sx={{ pb: 10, bgcolor: '#020617', minHeight: '100vh', mx: -4, px: 4, pt: 2 }}>
      {/* 1. Terminal Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', mb: 5, flexWrap: 'wrap', gap: 3 }}>
         <Box>
            <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1, color: '#fff' }}>EQUITY TERMINAL</Typography>
            <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
               <Typography variant="caption" sx={{ fontWeight: 900, color: '#10b981', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Activity size={14} /> LIVE SHADOW SCAN
               </Typography>
               <Divider orientation="vertical" flexItem sx={{ height: 12, my: 'auto', bgcolor: 'rgba(255,255,255,0.1)' }} />
               <Typography variant="caption" sx={{ fontWeight: 800, color: connectionStatus === 'ONLINE' ? '#10b981' : '#ef4444' }}>
                  NODE: {connectionStatus} (SHADOW MODE)
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
               '&:focus-within': { borderColor: '#10b981', bgcolor: '#111827', boxShadow: '0 0 0 2px rgba(16, 185, 129, 0.1)' }
            }}>
               <Search size={18} color="slategray" />
               <InputBase
                  placeholder="FILTER BY TICKER..."
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

      {/* 2. Signal Summary Ribbon */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
         <Grid item xs={6} md={3}>
            <SummaryStat label="TOTAL ACTIVE" value={counts.all} color="primary.main" />
         </Grid>
         <Grid item xs={6} md={3}>
            <SummaryStat label="PRIMARY SWING" value={counts.swing} color="#10b981" />
         </Grid>
         <Grid item xs={6} md={3}>
            <SummaryStat label="SELECTIVE LONG" value={counts.long} color="#00D1FF" />
         </Grid>
         <Grid item xs={6} md={3}>
            <SummaryStat label="EXPERIMENTAL SHORT" value={counts.short} color="slategray" />
         </Grid>
      </Grid>

      {/* 3. Universe Selectors */}
      <Paper sx={{ mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 1, p: 0.5, width: 'fit-content' }}>
        <Tabs
            value={activeTab}
            onChange={(_, v) => setActiveTab(v)}
            sx={{
                minHeight: 44,
                '& .MuiTabs-indicator': { height: 3, bgcolor: universes[activeTab].color },
                '& .MuiTab-root': {
                    color: 'slategray',
                    fontWeight: 950,
                    fontSize: '0.7rem',
                    minWidth: 160,
                    textTransform: 'none',
                    '&.Mui-selected': { color: 'white' }
                }
            }}
        >
            {universes.map((u) => (
                <Tab key={u.value} label={u.label} />
            ))}
        </Tabs>
      </Paper>

      {/* 4. Data Grid */}
      {loading ? (
         <Grid container spacing={3}>
            {[1,2,3,4,5,6].map(i => (
               <Grid item xs={12} md={6} lg={4} key={i}>
                  <Skeleton variant="rectangular" height={450} sx={{ borderRadius: 1, bgcolor: 'rgba(255,255,255,0.02)' }} />
               </Grid>
            ))}
         </Grid>
      ) : (
         <Box>
            {filteredSignals.length > 0 ? (
               <Grid container spacing={3}>
                  {filteredSignals.map((s) => (
                     <Grid item xs={12} md={6} lg={4} key={s.id}>
                        <LiveSignalCard stock={s} decision={s.decision} />
                     </Grid>
                  ))}
               </Grid>
            ) : (
               <Paper sx={{ py: 20, textAlign: 'center', bgcolor: alpha('#0f172a', 0.5), border: '1px dashed rgba(255,255,255,0.05)', borderRadius: 1 }}>
                  <ShieldAlert size={56} color="slategray" style={{ margin: '0 auto 24px', opacity: 0.2 }} />
                  <Typography variant="h6" sx={{ fontWeight: 900, color: 'slategray', letterSpacing: 1 }}>
                     {universes[activeTab].label} — NO QUALIFIED SIGNALS
                  </Typography>
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 1, opacity: 0.5, fontWeight: 700 }}>
                     The quantitative engine has not identified any signals meeting the {universes[activeTab].label} evidence gates.
                  </Typography>
                  <Button
                    variant="text"
                    size="small"
                    sx={{ mt: 4, fontWeight: 900, color: '#10b981', textTransform: 'none' }}
                    onClick={() => {setSearchQuery(''); setActiveTab(0);}}
                  >
                    VIEW ALL ACTIVE SIGNALS
                  </Button>
               </Paper>
            )}
         </Box>
      )}

      {/* 5. Footer Metadata */}
      <Box sx={{ mt: 10, p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1 }}>
         <Stack direction="row" spacing={3} alignItems="flex-start">
            <Box sx={{ bgcolor: alpha('#10b981', 0.1), p: 1, borderRadius: 1 }}>
               <Info size={20} color="#10b981" />
            </Box>
            <Box>
               <Typography variant="subtitle2" sx={{ fontWeight: 950, color: '#fff', mb: 0.5, letterSpacing: 1 }}>FORENSIC SIGNAL PROTOCOL</Typography>
               <Typography variant="caption" sx={{ color: 'slategray', lineHeight: 1.6, display: 'block', fontWeight: 600 }}>
                  Authoritative signals are derived from institutional order flow and Strategy V2.2 breakout logic.
                  Latest sync confirmed at {latestUpdate} IST.
               </Typography>
            </Box>
         </Stack>
      </Box>
    </Box>
  );
}

function SummaryStat({ label, value, color }: any) {
    return (
        <Paper sx={{ p: 2, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.03)' }}>
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, fontSize: '0.6rem', display: 'block', mb: 0.5 }}>{label}</Typography>
            <Typography variant="h4" sx={{ fontWeight: 950, color, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
        </Paper>
    );
}
