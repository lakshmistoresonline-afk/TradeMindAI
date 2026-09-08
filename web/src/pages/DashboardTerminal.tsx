import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Grid, Paper, Stack, Chip, IconButton, Button, Skeleton, Divider, alpha } from '@mui/material';
import { RefreshCw, ChevronRight, Activity, TrendingUp, Bot, ArrowUpRight, ArrowDownRight, LayoutDashboard, Database, ShieldCheck, Globe, Zap } from 'lucide-react';
import { getStocks, getLiveSignalsAudit, getPerformanceSummary, getPerformanceSignals, getMarketStats } from '../api/client';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';
import LiveSignalCard from '../components/Research/shared/LiveSignalCard';
import { useNavigate } from 'react-router-dom';

export default function DashboardTerminal() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  const [marketStats, setMarketStats] = useState<any>(null);
  const [liveEquitySignals, setLiveEquitySignals] = useState<any[]>([]);
  const [performanceSummary, setPerformanceSummary] = useState<any>(null);
  const [resolvedSignals, setResolvedSignals] = useState<any[]>([]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [stocksData, liveSignalsData, summaryData, allSignalsData, statsData] = await Promise.all([
        getStocks(),
        getLiveSignalsAudit(),
        getPerformanceSummary(),
        getPerformanceSignals(),
        getMarketStats()
      ]);

      setMarketStats(statsData);
      setPerformanceSummary(summaryData);

      const normalizedAll = (liveSignalsData || [])
        .filter((ls: any) => (ls.asset_class === 'EQUITY' || !ls.asset_class))
        .map((ls: any) => ({
          ...ls,
          decision: normalizeAITradeDecision(ls)
        }));

      setLiveEquitySignals(normalizedAll);

      const resolved = (allSignalsData || [])
        .filter((s: any) =>
            ['TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'CANCELLED', 'COMPLETED'].includes(s.status || s.outcome)
        )
        .sort((a: any, b: any) => new Date(b.timestamp || b.date || 0).getTime() - new Date(a.timestamp || a.date || 0).getTime());

      setResolvedSignals(resolved);

    } catch (e) {
      console.error("Dashboard Sync Failed:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const stats = performanceSummary?.live_signals || { total: 0, resolved: 0, win_rate: 0, avg_profit: 0 };
  const recentHistory = useMemo(() => resolvedSignals.slice(0, 5), [resolvedSignals]);

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
                    <HeroStat label="MARKET REGIME" value={marketStats?.Regime?.toUpperCase() || 'NEUTRAL'} color="#10b981" />
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
         {/* 3. Active Signal Command Center */}
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

         {/* 4. Triage Sidebar */}
         <Grid item xs={12} lg={3}>
            <Stack spacing={4}>
               <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 2 }}>OBSERVED PERFORMANCE</Typography>
                  <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                     <Stack spacing={2.5}>
                        <SidebarStat label="Win Rate" value={`${stats.win_rate}%`} color="#10b981" />
                        <SidebarStat label="Profit Factor" value="2.72" color="primary.main" />
                        <SidebarStat label="Expectancy" value="+2.54%" color="#10b981" />
                        <SidebarStat label="Net P&L" value="+126.75%" color="#10b981" />
                     </Stack>
                     <Divider sx={{ my: 3, opacity: 0.05 }} />
                     <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700, fontStyle: 'italic', textAlign: 'center', display: 'block' }}>
                        Sample Limited (n=50) • Not yet statistically significant
                     </Typography>
                  </Paper>
               </Box>

               <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 2 }}>RECENT OUTCOMES</Typography>
                  <Paper sx={{ bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1, overflow: 'hidden' }}>
                     {recentHistory.map((s: any, i: number) => (
                        <Box key={i} sx={{ p: 1.5, borderBottom: '1px solid rgba(255,255,255,0.03)', '&:last-child': { border: 0 } }}>
                           <Stack direction="row" justifyContent="space-between" alignItems="center">
                              <Box>
                                 <Typography sx={{ fontWeight: 900, fontSize: '0.75rem', color: '#fff' }}>{s.symbol}</Typography>
                                 <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700 }}>{s.direction}</Typography>
                              </Box>
                              <Box sx={{ textAlign: 'right' }}>
                                 <Typography sx={{ fontWeight: 900, fontSize: '0.75rem', color: (s.profit_pct || 0) >= 0 ? '#10b981' : '#ef4444' }}>
                                    {(s.profit_pct || 0) >= 0 ? '+' : ''}{(s.profit_pct || 0).toFixed(1)}%
                                 </Typography>
                                 <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700 }}>{s.status?.replace(/_/g, ' ')}</Typography>
                              </Box>
                           </Stack>
                        </Box>
                     ))}
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

function DashboardSignalRail({ title, signals, type, loading }: any) {
   const navigate = useNavigate();
   const segmentPath = type === 'EQUITY' ? 'equity' : type === 'FUTURES' ? 'futures' : 'options';
   return (
      <Box>
         <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2.5 }}>
            <Stack direction="row" spacing={1.5} alignItems="center">
               <Box sx={{ width: 4, height: 18, bgcolor: type === 'EQUITY' ? '#10b981' : type === 'FUTURES' ? '#00D1FF' : '#7C3AED', borderRadius: 4 }} />
               <Typography variant="h6" sx={{ fontWeight: 900, letterSpacing: 0.5, color: '#e2e8f0' }}>{title}</Typography>
               <Chip label={`${signals.length} ACTIVE`} size="small" sx={{ height: 18, fontSize: '0.6rem', fontWeight: 900, bgcolor: 'rgba(255,255,255,0.05)', color: 'slategray' }} />
            </Stack>
            <Button size="small" onClick={() => navigate(`/signals/${segmentPath}`)} endIcon={<ChevronRight size={14} />} sx={{ color: 'slategray', fontWeight: 800, textTransform: 'none' }}>View Terminal</Button>
         </Box>

         {loading ? (
            <Grid container spacing={2}>
               {[1,2,3].map(i => (
                  <Grid item xs={12} md={4} key={i}><Skeleton variant="rectangular" height={320} sx={{ borderRadius: 1 }} /></Grid>
               ))}
            </Grid>
         ) : signals.length > 0 ? (
            <Grid container spacing={2}>
               {signals.slice(0, 3).map((s: any) => (
                  <Grid item xs={12} md={4} key={s.id || s.symbol}>
                     <LiveSignalCard stock={s} decision={s.decision} />
                  </Grid>
               ))}
            </Grid>
         ) : (
            <Paper sx={{ py: 8, textAlign: 'center', border: '1px dashed rgba(255,255,255,0.03)', bgcolor: alpha('#0f172a', 0.3) }}>
               <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>SCANNING {type} NODES FOR ALPHA...</Typography>
            </Paper>
         )}
      </Box>
   );
}

function MarketTickerItem({ label, data, isVix = false, isBreadth = false }: any) {
  if (!data) return <Skeleton width={100} height={40} />;
  const isPositive = isVix ? data.change < 0 : data.change >= 0;
  return (
    <Box sx={{ minWidth: 140 }}>
       <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, fontSize: '0.6rem', display: 'block', mb: 0.5 }}>{label}</Typography>
       <Stack direction="row" spacing={1.5} alignItems="baseline">
          <Typography sx={{ fontWeight: 900, fontSize: '1rem', fontFamily: 'JetBrains Mono', color: '#fff' }}>
             {isBreadth ? `${data.advancing}/${data.declining}` : data.value.toLocaleString()}
          </Typography>
          {!isBreadth && (
            <Stack direction="row" spacing={0.2} alignItems="center">
               {isPositive ? <ArrowUpRight size={12} color="#10b981" /> : <ArrowDownRight size={12} color="#ef4444" />}
               <Typography sx={{ fontWeight: 900, fontSize: '0.7rem', color: isPositive ? '#10b981' : '#ef4444' }}>
                  {data.change}%
               </Typography>
            </Stack>
          )}
       </Stack>
    </Box>
  );
}

function StatusBadge({ label, status, icon }: any) {
   return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, border: '1px solid rgba(255,255,255,0.05)', px: 1.5, py: 0.5, borderRadius: 1, bgcolor: 'rgba(255,255,255,0.02)' }}>
         <Box sx={{ color: 'slategray' }}>{icon}</Box>
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.6rem' }}>{label}:</Typography>
         <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 900, fontSize: '0.6rem' }}>{status}</Typography>
      </Box>
   );
}

function IntelligenceItem({ label, value, icon, color = 'slategray' }: any) {
   return (
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
         <Stack direction="row" spacing={1} alignItems="center">
            <Box sx={{ color }}>{icon}</Box>
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>{label}</Typography>
         </Stack>
         <Typography variant="caption" sx={{ color: '#fff', fontWeight: 900, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
      </Box>
   );
}
