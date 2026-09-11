import { useState, useEffect } from 'react';
import { Box, Typography, Grid, Paper, Stack, Button, Skeleton, Divider, alpha } from '@mui/material';
import { ChevronRight } from 'lucide-react';
import {
  getEquitySignals,
  getEquityPerformance,
  getEquityMarketState,
  getMarketStats
} from '../api/client';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';
import LiveSignalCard from '../components/Research/shared/LiveSignalCard';
import { useNavigate } from 'react-router-dom';

export default function DashboardTerminal() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  const [marketStats, setMarketStats] = useState<any>(null);
  const [liveEquitySignals, setLiveEquitySignals] = useState<any[]>([]);
  const [performanceSummary, setPerformanceSummary] = useState<any>(null);
  const [marketState, setMarketState] = useState<any>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [signalsData, perfData, marketData, statsData] = await Promise.all([
        getEquitySignals({ limit: 10 }),
        getEquityPerformance(),
        getEquityMarketState(),
        getMarketStats()
      ]);

      setMarketStats(statsData);
      setPerformanceSummary(perfData);
      setMarketState(marketData);

      const normalized = (signalsData || [])
        .map((ls: any) => ({
          ...ls,
          decision: normalizeAITradeDecision(ls)
        }));

      setLiveEquitySignals(normalized);

    } catch (e) {
      console.error("Dashboard Sync Failed:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const stats = {
    total: performanceSummary?.sample_size || 0,
    win_rate: performanceSummary?.win_rate || 0,
    net_pnl: performanceSummary?.net_pnl || 0,
    profit_factor: performanceSummary?.profit_factor || 0
  };

  const buyCount = liveEquitySignals.filter(s => s.direction === 'LONG').length;
  const sellCount = liveEquitySignals.filter(s => s.direction === 'SHORT').length;
  const highConfidence = liveEquitySignals.filter(s => (s.calibrated_probability || 0) > 0.75).length;

  return (
    <Box sx={{ pb: 10, bgcolor: '#020617', minHeight: '100vh', mx: -4, px: 4, pt: 2 }}>
      {/* 1. Hero Header */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h3" sx={{ fontWeight: 950, letterSpacing: -2, color: '#fff', mb: 1 }}>TRADEMIND AI</Typography>
        <Typography variant="h5" sx={{ fontWeight: 800, color: 'primary.main', letterSpacing: 1, mb: 4 }}>NIFTY-200 EQUITY INTELLIGENCE</Typography>

        <Grid container spacing={2}>
           <Grid item xs={12} md={8}>
              <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                 <Grid container spacing={4}>
                    <HeroStat label="MARKET REGIME" value={marketState?.regime?.toUpperCase() || 'NEUTRAL'} color="#10b981" />
                    <HeroStat label="MONITORED EQUITIES" value="200" />
                    <HeroStat label="ACTIVE SIGNALS" value={liveEquitySignals.length} color="primary.main" />
                    <HeroStat label="HIGH CONFIDENCE" value={highConfidence} color="#7C3AED" />
                 </Grid>
                 <Divider sx={{ my: 3, opacity: 0.05 }} />
                 <Stack direction="row" spacing={4}>
                    <SmallStat label="BUY" value={buyCount} color="#10b981" />
                    <SmallStat label="SELL" value={sellCount} color="#ef4444" />
                    <SmallStat label="HOLD" value={200 - buyCount - sellCount} />
                    <Box sx={{ ml: 'auto', textAlign: 'right' }}>
                       <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, display: 'block' }}>LAST DATA REFRESH</Typography>
                       <Typography variant="caption" sx={{ color: '#fff', fontWeight: 900 }}>{new Date().toLocaleTimeString()} IST • LIVE</Typography>
                    </Box>
                 </Stack>
              </Paper>
           </Grid>
           <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: '100%', bgcolor: alpha('#00D1FF', 0.03), border: '1px solid rgba(0, 209, 255, 0.1)', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                 <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 900, letterSpacing: 2, mb: 1 }}>MARKET SESSION</Typography>
                 <Typography variant="h4" sx={{ fontWeight: 950, color: '#fff' }}>OPEN</Typography>
                 <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700, mt: 1 }}>NSE LIVE FEED ACTIVE</Typography>
              </Paper>
           </Grid>
        </Grid>
      </Box>

      {/* 2. Market Ribbon */}
      <Stack direction="row" spacing={4} sx={{ mb: 6, overflowX: 'auto', pb: 1 }}>
         <MarketTickerItem label="NIFTY 50" data={marketStats?.['NIFTY 50']} />
         <MarketTickerItem label="NIFTY 100" data={marketStats?.['NIFTY 100']} />
         <MarketTickerItem label="NIFTY 200" data={marketStats?.['NIFTY 200']} />
      </Stack>

      <Grid container spacing={4}>
         <Grid item xs={12} lg={9}>
            <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
               <Typography variant="h6" sx={{ fontWeight: 900, letterSpacing: 1 }}>ACTIVE EQUITY SIGNALS</Typography>
               <Button onClick={() => navigate('/signals')} size="small" endIcon={<ChevronRight size={16} />} sx={{ color: 'primary.main', fontWeight: 800 }}>VIEW ALL</Button>
            </Box>

            {loading ? (
               <Grid container spacing={2}>
                  {[1,2,3].map(i => <Grid item xs={12} md={4} key={i}><Skeleton variant="rectangular" height={320} sx={{ borderRadius: 1 }} /></Grid>)}
               </Grid>
            ) : (
               <Grid container spacing={2}>
                  {liveEquitySignals.slice(0, 6).map((s) => (
                     <Grid item xs={12} md={4} key={s.id}>
                        <LiveSignalCard stock={s} decision={s.decision} />
                     </Grid>
                  ))}
               </Grid>
            )}
         </Grid>

         <Grid item xs={12} lg={3}>
            <Stack spacing={4}>
               <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 2 }}>OBSERVED PERFORMANCE</Typography>
                  <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                     <Stack spacing={2.5}>
                        <SidebarStat label="Win Rate" value={`${stats.win_rate}%`} color="#10b981" />
                        <SidebarStat label="Profit Factor" value={stats.profit_factor} color="primary.main" />
                        <SidebarStat label="Net P&L" value={`${stats.net_pnl > 0 ? '+' : ''}${stats.net_pnl}%`} color={stats.net_pnl >= 0 ? '#10b981' : '#ef4444'} />
                     </Stack>
                     <Divider sx={{ my: 3, opacity: 0.05 }} />
                     <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700, fontStyle: 'italic', textAlign: 'center', display: 'block' }}>
                        Authoritative Dataset (n={stats.total})
                     </Typography>
                  </Paper>
               </Box>
            </Stack>
         </Grid>
      </Grid>
    </Box>
  );
}

function HeroStat({ label, value, color = '#fff' }: any) {
   return (
      <Grid item xs={6} md={3}>
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, letterSpacing: 1, display: 'block', mb: 0.5 }}>{label}</Typography>
         <Typography variant="h4" sx={{ fontWeight: 950, color, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
      </Grid>
   );
}

function SmallStat({ label, value, color = 'slategray' }: any) {
   return (
      <Stack direction="row" spacing={1} alignItems="baseline">
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>{label}:</Typography>
         <Typography sx={{ fontWeight: 900, color, fontSize: '0.9rem' }}>{value}</Typography>
      </Stack>
   );
}

function SidebarStat({ label, value, color }: any) {
   return (
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>{label}</Typography>
         <Typography variant="body2" sx={{ color, fontWeight: 950, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
      </Box>
   );
}

function MarketTickerItem({ label, data }: any) {
  if (!data) return <Skeleton width={100} height={40} />;
  const isPositive = data.change >= 0;
  return (
    <Box sx={{ minWidth: 140 }}>
       <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, fontSize: '0.6rem', display: 'block', mb: 0.5 }}>{label}</Typography>
       <Stack direction="row" spacing={1.5} alignItems="baseline">
          <Typography sx={{ fontWeight: 900, fontSize: '1rem', fontFamily: 'JetBrains Mono', color: '#fff' }}>
             {data.value.toLocaleString()}
          </Typography>
          <Stack direction="row" spacing={0.2} alignItems="center">
             <Typography sx={{ fontWeight: 900, fontSize: '0.7rem', color: isPositive ? '#10b981' : '#ef4444' }}>
                {isPositive ? '+' : ''}{data.change}%
             </Typography>
          </Stack>
       </Stack>
    </Box>
  );
}
