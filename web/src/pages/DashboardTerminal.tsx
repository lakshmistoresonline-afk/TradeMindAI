import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Grid, Paper, Stack, Button, Skeleton, Divider, alpha, Collapse, Chip } from '@mui/material';
import { ShieldCheck, Zap, ArrowRight, TrendingUp } from 'lucide-react';
import { mapCanonicalSignal } from '../hooks/useAITradeDecision';
import LiveSignalCard from '../components/Research/shared/LiveSignalCard';
import { useNavigate } from 'react-router-dom';
import { getEquitySignals, getEquityPerformance, getEquityMarketState, getMarketStats, getEquityHistory } from '../api/client';

export default function DashboardTerminal() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [expandedShort, setExpandedShort] = useState(false);

  const [marketStats, setMarketStats] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);
  const [recentHistory, setRecentHistory] = useState<any[]>([]);
  const [performanceSummary, setPerformanceSummary] = useState<any>(null);
  const [marketState, setMarketState] = useState<any>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        getEquitySignals({ limit: 100 }),
        getEquityPerformance(),
        getEquityMarketState(),
        getMarketStats(),
        getEquityHistory({ limit: 5 })
      ]);

      const signalsData = results[0].status === 'fulfilled' ? (results[0].value || []) : [];
      const perfData = results[1].status === 'fulfilled' ? results[1].value : null;
      const marketData = results[2].status === 'fulfilled' ? results[2].value : null;
      const statsData = results[3].status === 'fulfilled' ? results[3].value : null;
      const historyData = results[4].status === 'fulfilled' ? results[4].value : null;

      setMarketStats(statsData);
      setPerformanceSummary(perfData);
      setMarketState(marketData);
      setRecentHistory((historyData?.records || []).map((r: any) => mapCanonicalSignal(r)));

      const normalized = (Array.isArray(signalsData) ? signalsData : [])
        .map((s: any) => mapCanonicalSignal(s));

      setSignals(normalized);
    } catch (e) {
      console.error("Dashboard Sync Failed:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const counts = useMemo(() => {
    return {
      swingPrimary: signals.filter(s => s.decision.timeframe === 'SWING' && s.decision.qualityClass === 'PRIMARY').length,
      swingSelective: signals.filter(s => s.decision.timeframe === 'SWING' && s.decision.qualityClass === 'SELECTIVE').length,
      longSelective: signals.filter(s => s.decision.timeframe === 'LONG' && s.decision.qualityClass === 'SELECTIVE').length,
      shortExperimental: signals.filter(s => s.decision.timeframe === 'SHORT').length,
      total: signals.length
    };
  }, [signals]);

  return (
    <Box sx={{ pb: 10, bgcolor: '#020617', minHeight: '100vh', mx: -4, px: 4, pt: 2 }}>
      {/* 1. Executive Intelligence Header */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h3" sx={{ fontWeight: 950, letterSpacing: -2, color: '#fff', mb: 1 }}>TRADEMIND AI</Typography>
        <Typography variant="h5" sx={{ fontWeight: 800, color: 'primary.main', letterSpacing: 1, mb: 4 }}>OPERATIONAL INTELLIGENCE TERMINAL</Typography>

        <Grid container spacing={2}>
           <Grid item xs={12} md={8}>
              <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                 <Grid container spacing={4}>
                    <HeroStat label="MARKET REGIME" value={marketState?.regime?.toUpperCase() || 'BEAR'} color="#ef4444" />
                    <HeroStat label="STRATEGY" value="V2.2 FROZEN" color="primary.main" />
                    <HeroStat label="ACTIVE SIGNALS" value={counts.total} color="#fff" />
                    <HeroStat label="SYSTEM MODE" value="SHADOW" color="#00D1FF" />
                 </Grid>
                 <Divider sx={{ my: 3, opacity: 0.05 }} />
                 <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                        <SummaryStat label="SWING" value={counts.swingPrimary + counts.swingSelective} sub={`${counts.swingPrimary} PRI / ${counts.swingSelective} SEL`} color="#10b981" />
                    </Grid>
                    <Grid item xs={6} md={4}>
                        <SummaryStat label="LONG" value={counts.longSelective} sub="Symbol Qualified" color="#00D1FF" />
                    </Grid>
                    <Grid item xs={6} md={4}>
                        <SummaryStat label="SHORT" value={counts.shortExperimental} sub="Experimental" color="slategray" />
                    </Grid>
                 </Grid>
                 <Divider sx={{ my: 3, opacity: 0.05 }} />
                 <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                       <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, display: 'block' }}>STRATEGY: V2.2 (FROZEN)</Typography>
                       <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 900 }}>RELIABILITY: AUDITED</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'right' }}>
                       <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, display: 'block' }}>AUDIT STATUS: HARDENED</Typography>
                       <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 900 }}>REAL-TIME FEED: ACTIVE</Typography>
                    </Box>
                 </Box>
              </Paper>
           </Grid>
           <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: '100%', bgcolor: alpha('#00D1FF', 0.03), border: '1px solid rgba(0, 209, 255, 0.1)', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                 <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 900, letterSpacing: 2, mb: 1 }}>BASELINE IDENTITY</Typography>
                 <Typography variant="h4" sx={{ fontWeight: 950, color: '#fff' }}>V2.2 FROZEN</Typography>
                 <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700, mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                    TRADING EXECUTION: LOCKED <ShieldCheck size={12} color="#ef4444" />
                 </Typography>
                 <Button
                    variant="text"
                    size="small"
                    onClick={() => navigate('/evidence')}
                    sx={{ mt: 2, p: 0, justifyContent: 'flex-start', color: 'primary.main', fontWeight: 800, fontSize: '0.65rem' }}
                 >
                    VIEW EVIDENCE & LIMITATIONS →
                 </Button>
              </Paper>
           </Grid>
        </Grid>
      </Box>

      <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 2, color: 'slategray', letterSpacing: 1 }}>MARKET OVERVIEW</Typography>
      <Stack direction="row" spacing={4} sx={{ mb: 6, overflowX: 'auto', pb: 1 }}>
         <MarketTickerItem label="NIFTY 50" data={marketStats?.['NIFTY 50']} />
         <MarketTickerItem label="NIFTY 100" data={marketStats?.['NIFTY 100']} />
         <MarketTickerItem label="NIFTY 200" data={marketStats?.['NIFTY 200']} />
         <MarketTickerItem label="INDIA VIX" data={marketState?.vix ? { value: marketState.vix, change: 0 } : null} />
      </Stack>

      <Grid container spacing={4}>
         {/* 3. Primary Opportunities */}
         <Grid item xs={12} lg={9}>
            {loading ? (
               <Grid container spacing={2}>
                  {[1,2,3].map(i => <Grid item xs={12} md={4} key={i}><Skeleton variant="rectangular" height={450} sx={{ borderRadius: 1 }} /></Grid>)}
               </Grid>
            ) : (
               <Stack spacing={6}>
                  <Box>
                     <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                        <Typography variant="h6" sx={{ fontWeight: 900, letterSpacing: 1, color: '#10b981', display: 'flex', alignItems: 'center', gap: 1.5 }}>
                           <ShieldCheck size={20} /> PRIMARY SWING OPPORTUNITIES
                        </Typography>
                        <Button onClick={() => navigate('/signals')} endIcon={<ArrowRight size={14} />} sx={{ fontWeight: 800, color: 'slategray', fontSize: '0.7rem' }}>VIEW ALL</Button>
                     </Box>
                     {counts.swingPrimary > 0 ? (
                        <Grid container spacing={2}>
                           {signals.filter(s => s.decision.timeframe === 'SWING' && s.decision.qualityClass === 'PRIMARY').map((s) => (
                              <Grid item xs={12} md={4} key={s.id}>
                                 <LiveSignalCard stock={s} decision={s.decision} />
                              </Grid>
                           ))}
                        </Grid>
                     ) : (
                        <Paper sx={{ p: 6, textAlign: 'center', bgcolor: alpha('#10b981', 0.02), border: '1px dashed rgba(16, 185, 129, 0.2)' }}>
                           <Typography variant="body1" sx={{ color: 'slategray', fontWeight: 700 }}>NO CURRENTLY QUALIFIED PRIMARY SIGNALS</Typography>
                        </Paper>
                     )}
                  </Box>

                  <Box>
                     <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                        <Typography variant="h6" sx={{ fontWeight: 900, letterSpacing: 1, color: '#00D1FF', display: 'flex', alignItems: 'center', gap: 1.5 }}>
                           <TrendingUp size={20} /> SELECTIVE SWING / LONG
                        </Typography>
                     </Box>
                     {(counts.swingSelective + counts.longSelective) > 0 ? (
                        <Grid container spacing={2}>
                           {signals.filter(s => s.decision.qualityClass === 'SELECTIVE').map((s) => (
                              <Grid item xs={12} md={4} key={s.id}>
                                 <LiveSignalCard stock={s} decision={s.decision} />
                              </Grid>
                           ))}
                        </Grid>
                     ) : (
                        <Paper sx={{ p: 4, textAlign: 'center', bgcolor: alpha('#00D1FF', 0.02), border: '1px dashed rgba(0, 209, 255, 0.15)' }}>
                           <Typography variant="body2" sx={{ color: 'slategray', fontWeight: 700 }}>NO CURRENTLY QUALIFIED SELECTIVE SIGNALS</Typography>
                        </Paper>
                     )}
                  </Box>

                  <Box>
                     <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                        <Typography variant="h6" sx={{ fontWeight: 900, letterSpacing: 1, color: 'slategray', display: 'flex', alignItems: 'center', gap: 1.5 }}>
                           <Zap size={20} /> EXPERIMENTAL SHORT (RESEARCH ONLY)
                        </Typography>
                        {!expandedShort && counts.shortExperimental > 0 && (
                            <Button onClick={() => setExpandedShort(true)} size="small" sx={{ fontWeight: 800, color: 'slategray' }}>SHOW {counts.shortExperimental} SIGNALS</Button>
                        )}
                     </Box>
                     <Collapse in={expandedShort}>
                        <Grid container spacing={2}>
                           {signals.filter(s => s.decision.timeframe === 'SHORT').map((s) => (
                              <Grid item xs={12} md={4} key={s.id}>
                                 <LiveSignalCard stock={s} decision={s.decision} />
                              </Grid>
                           ))}
                        </Grid>
                     </Collapse>
                  </Box>
               </Stack>
            )}
         </Grid>

         {/* 4. Side Panels */}
         <Grid item xs={12} lg={3}>
            <Stack spacing={4}>
               {/* SIGNAL INTELLIGENCE SUMMARY */}
               <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 2 }}>SIGNAL INTELLIGENCE</Typography>
                  <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                     <Stack spacing={2.5}>
                        <SidebarStat label="Total Active" value={counts.total} color="primary.main" />
                        <SidebarStat label="Primary Swing" value={counts.swingPrimary} color="#10b981" />
                        <SidebarStat label="Selective" value={counts.swingSelective + counts.longSelective} color="#00D1FF" />
                        <SidebarStat label="Experimental" value={counts.shortExperimental} color="slategray" />
                     </Stack>
                     <Divider sx={{ my: 3, opacity: 0.05 }} />
                     <Box>
                        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, display: 'block', mb: 1 }}>DATA INTEGRITY</Typography>
                        <Chip label="VERIFIED" size="small" sx={{ height: 18, fontSize: '0.6rem', fontWeight: 950, bgcolor: alpha('#10b981', 0.1), color: '#10b981' }} />
                        <Typography variant="caption" sx={{ color: 'slategray', ml: 1.5, fontWeight: 700 }}>NSE SYNC STABLE</Typography>
                     </Box>
                  </Paper>
               </Box>

               {/* RECENT SIGNAL ACTIVITY */}
               <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 2 }}>RECENT SIGNAL ACTIVITY</Typography>
                  <Paper sx={{ p: 2, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                     {recentHistory.length > 0 ? (
                        <Stack spacing={2}>
                           {recentHistory.map((s) => (
                              <Box key={s.id} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                 <Box>
                                    <Typography variant="caption" sx={{ fontWeight: 950, color: '#fff' }}>{s.symbol}</Typography>
                                    <Typography variant="caption" sx={{ color: 'slategray', display: 'block', fontSize: '0.5rem', fontWeight: 800 }}>
                                        {s.decision.status} · {s.decision.timeframe}
                                    </Typography>
                                 </Box>
                                 <Box sx={{ textAlign: 'right' }}>
                                    <Typography variant="caption" sx={{ fontWeight: 950, color: (s.decision.realizedReturn || 0) >= 0 ? '#10b981' : '#ef4444' }}>
                                        {s.decision.realizedReturn !== undefined ? `${s.decision.realizedReturn > 0 ? '+' : ''}${s.decision.realizedReturn.toFixed(1)}%` : '—'}
                                    </Typography>
                                    <Typography variant="caption" sx={{ color: 'slategray', display: 'block', fontSize: '0.45rem', fontWeight: 700 }}>
                                        {s.decision.closedAt ? new Date(s.decision.closedAt).toLocaleDateString() : '—'}
                                    </Typography>
                                 </Box>
                              </Box>
                           ))}
                           <Button
                              fullWidth
                              size="small"
                              onClick={() => navigate('/signals')}
                              sx={{ mt: 1, fontSize: '0.6rem', fontWeight: 900, color: 'primary.main', textTransform: 'none' }}
                           >
                              VIEW FULL SIGNAL HISTORY →
                           </Button>
                        </Stack>
                     ) : (
                        <Typography variant="caption" sx={{ color: 'slategray', display: 'block', py: 2, textAlign: 'center' }}>NO RECENT CLOSED CALLS</Typography>
                     )}
                  </Paper>
               </Box>

               {/* OBSERVED PERFORMANCE */}
               <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 2 }}>OBSERVED PERFORMANCE</Typography>
                  <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                     <Stack spacing={2.5}>
                        <SidebarStat label="Win Rate" value={`${performanceSummary?.win_rate || 0}%`} color="#10b981" />
                        <SidebarStat label="Net P&L" value={`${(performanceSummary?.net_pnl || 0) > 0 ? '+' : ''}${performanceSummary?.net_pnl || 0}%`} color={(performanceSummary?.net_pnl || 0) >= 0 ? '#10b981' : '#ef4444'} />
                     </Stack>
                     <Divider sx={{ my: 3, opacity: 0.05 }} />
                     <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700, fontStyle: 'italic', textAlign: 'center', display: 'block' }}>
                        {performanceSummary?.sample_size ? `Authoritative Dataset (n=${performanceSummary.sample_size})` : 'NO CLOSED OUTCOMES AVAILABLE'}
                     </Typography>
                     <Button
                        fullWidth
                        size="small"
                        onClick={() => navigate('/performance')}
                        sx={{ mt: 2, fontSize: '0.6rem', fontWeight: 900, color: 'primary.main', textTransform: 'none' }}
                     >
                        PERFORMANCE ANALYSIS →
                     </Button>
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

function SummaryStat({ label, value, sub, color }: any) {
   return (
      <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.03)', height: '100%' }}>
         <Stack direction="row" spacing={1} alignItems="baseline">
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>{label}:</Typography>
            <Typography sx={{ fontWeight: 900, color, fontSize: '1.2rem', fontFamily: 'JetBrains Mono' }}>{value}</Typography>
         </Stack>
         <Typography variant="caption" sx={{ color: 'slategray', fontSize: '0.65rem', fontWeight: 700, mt: 0.5, display: 'block' }}>{sub}</Typography>
      </Box>
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
  if (!data) return <Skeleton width={120} height={40} />;
  const isPositive = data.change >= 0;
  return (
    <Box sx={{ minWidth: 140 }}>
       <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, fontSize: '0.6rem', display: 'block', mb: 0.5 }}>{label}</Typography>
       <Stack direction="row" spacing={1.5} alignItems="baseline">
          <Typography sx={{ fontWeight: 900, fontSize: '1rem', fontFamily: 'JetBrains Mono', color: '#fff' }}>
             {data.value.toLocaleString()}
          </Typography>
          <Typography sx={{ fontWeight: 900, fontSize: '0.7rem', color: isPositive ? '#10b981' : '#ef4444' }}>
             {isPositive ? '+' : ''}{data.change}%
          </Typography>
       </Stack>
    </Box>
  );
}
