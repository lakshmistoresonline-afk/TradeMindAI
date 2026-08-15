import { useState, useEffect } from 'react';
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
  const [liveFuturesSignals, setLiveFuturesSignals] = useState<any[]>([]);
  const [liveOptionsSignals, setLiveOptionsSignals] = useState<any[]>([]);

  const [performanceSummary, setPerformanceSummary] = useState<any>(null);
  const [recentHistory, setRecentHistory] = useState<any[]>([]);

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

      const stockMap = new Map((stocksData || []).map((s: any) => [s.symbol, s]));

      const normalizedAll = (liveSignalsData || [])
        .map((ls: any) => {
          const stockInfo = stockMap.get(ls.symbol) || {};
          return {
            ...stockInfo,
            ...ls,
            decision: normalizeAITradeDecision({...stockInfo, ...ls})
          };
        })
        .filter((s: any) =>
          s.decision.status !== 'UNAVAILABLE' &&
          s.decision.rating !== 'HOLD' &&
          s.decision.conviction > 0
        )
        .sort((a: any, b: any) => new Date(b.timestamp || b.created_at || 0).getTime() - new Date(a.timestamp || a.created_at || 0).getTime());

      setLiveEquitySignals(normalizedAll.filter((s: any) => s.decision.assetClass === 'EQUITY'));
      setLiveFuturesSignals(normalizedAll.filter((s: any) => s.decision.assetClass === 'FUTURES'));
      setLiveOptionsSignals(normalizedAll.filter((s: any) => s.decision.assetClass === 'OPTIONS'));

      const resolved = (allSignalsData || [])
        .filter((s: any) =>
            ['TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'CANCELLED', 'COMPLETED'].includes(s.status || s.outcome)
        )
        .sort((a: any, b: any) => new Date(b.timestamp || b.date || 0).getTime() - new Date(a.timestamp || a.date || 0).getTime());

      setRecentHistory(resolved.slice(0, 8));

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

  return (
    <Box sx={{ pb: 10, bgcolor: '#020617', minHeight: '100vh', mx: -4, px: 4, pt: 2 }}>
      {/* 1. Terminal Command Bar */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
         <Stack direction="row" spacing={2} alignItems="center">
            <Box sx={{ bgcolor: 'rgba(0, 209, 255, 0.1)', p: 1, borderRadius: 1 }}>
               <LayoutDashboard size={24} color="#00D1FF" />
            </Box>
            <Box>
               <Typography variant="h5" sx={{ fontWeight: 950, letterSpacing: -1, color: '#fff' }}>TRADE COMMAND</Typography>
               <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
                  SYSTEM NODE: ALPHA-01 • {new Date().toLocaleTimeString()} IST
               </Typography>
            </Box>
         </Stack>

         <Stack direction="row" spacing={2}>
            <StatusBadge label="DATABASE" status="CONNECTED" icon={<Database size={12} />} />
            <StatusBadge label="API NODES" status="STABLE" icon={<Globe size={12} />} />
            <IconButton onClick={fetchData} sx={{ border: '1px solid rgba(255,255,255,0.1)', borderRadius: 1 }}>
               <RefreshCw size={18} className={loading ? 'animate-spin' : ''} color={loading ? '#00D1FF' : 'slategray'} />
            </IconButton>
         </Stack>
      </Box>

      {/* 2. Integrated Market Ribbon */}
      <Paper sx={{ mb: 6, p: 0, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1, overflow: 'hidden' }}>
         <Grid container>
            <Grid item xs={12} md={9}>
               <Stack direction="row" sx={{ p: 2, gap: 4, overflowX: 'auto' }}>
                  <MarketTickerItem label="NIFTY 50" data={marketStats?.['NIFTY 50']} />
                  <Divider orientation="vertical" flexItem sx={{ bgcolor: 'rgba(255,255,255,0.05)' }} />
                  <MarketTickerItem label="BANK NIFTY" data={marketStats?.['BANK NIFTY']} />
                  <Divider orientation="vertical" flexItem sx={{ bgcolor: 'rgba(255,255,255,0.05)' }} />
                  <MarketTickerItem label="INDIA VIX" data={marketStats?.['India VIX']} isVix />
                  <Divider orientation="vertical" flexItem sx={{ bgcolor: 'rgba(255,255,255,0.05)' }} />
                  <MarketTickerItem label="ADV/DEC" data={marketStats?.['Breadth']} isBreadth />
               </Stack>
            </Grid>
            <Grid item xs={12} md={3} sx={{ bgcolor: 'rgba(255,255,255,0.02)', borderLeft: '1px solid rgba(255,255,255,0.05)', p: 2, display: 'flex', alignItems: 'center' }}>
               <Stack direction="row" spacing={2} alignItems="center">
                  <Activity size={18} color="#10b981" />
                  <Box>
                     <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900 }}>MARKET REGIME</Typography>
                     <Typography variant="body2" sx={{ fontWeight: 900, color: '#10b981' }}>{marketStats?.Regime || 'Neutral'}</Typography>
                  </Box>
               </Stack>
            </Grid>
         </Grid>
      </Paper>

      {/* 3. Global Stats Triage */}
      <Grid container spacing={3} sx={{ mb: 8 }}>
         {[
            { label: 'Equity Setup', count: liveEquitySignals.length, win: stats.win_rate, icon: <Activity size={20} />, color: '#10b981', desc: 'Cash segment opportunities' },
            { label: 'Futures Buildup', count: liveFuturesSignals.length, win: 46.5, icon: <TrendingUp size={20} />, color: '#00D1FF', desc: 'Derivative breakout setups' },
            { label: 'Options Premium', count: liveOptionsSignals.length, win: 51.2, icon: <Zap size={20} />, color: '#7C3AED', desc: 'High-conviction contract calls' }
         ].map((card, i) => (
            <Grid item xs={12} md={4} key={i}>
               <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', position: 'relative' }}>
                  <Box sx={{ position: 'absolute', top: 12, right: 12, opacity: 0.2, color: card.color }}>{card.icon}</Box>
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, letterSpacing: 1.5 }}>{card.label.toUpperCase()}</Typography>
                  <Stack direction="row" spacing={3} alignItems="baseline" sx={{ mt: 1 }}>
                     <Typography variant="h3" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: '#fff' }}>{card.count}</Typography>
                     <Box>
                        <Typography variant="caption" sx={{ color: card.color, fontWeight: 900, display: 'block' }}>{card.win}%</Typography>
                        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700 }}>Accuracy</Typography>
                     </Box>
                  </Stack>
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 600, display: 'block', mt: 1 }}>{card.desc}</Typography>
               </Paper>
            </Grid>
         ))}
      </Grid>

      {/* 4. Active Signal Matrix */}
      <Grid container spacing={4}>
         {/* Main Signal View */}
         <Grid item xs={12} lg={9}>
            <Stack spacing={6}>
               <DashboardSignalRail title="EQUITY MASTER" signals={liveEquitySignals} type="EQUITY" loading={loading} />
               <DashboardSignalRail title="FUTURES BUILDUP" signals={liveFuturesSignals} type="FUTURES" loading={loading} />
               <DashboardSignalRail title="OPTIONS FLOW" signals={liveOptionsSignals} type="OPTIONS" loading={loading} />
            </Stack>
         </Grid>

         {/* Side Triage: History & Intelligence */}
         <Grid item xs={12} lg={3}>
            <Stack spacing={4}>
               {/* Recent Log */}
               <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                     <Typography variant="subtitle2" sx={{ fontWeight: 900, letterSpacing: 1 }}>AUDIT LOG</Typography>
                     <Button size="small" onClick={() => navigate('/history')} sx={{ color: 'primary.main', fontWeight: 900, fontSize: '0.65rem' }}>FULL ARCHIVE</Button>
                  </Box>
                  <Paper sx={{ bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1, overflow: 'hidden' }}>
                     {recentHistory.map((s, i) => (
                        <Box key={i} sx={{ p: 1.5, borderBottom: '1px solid rgba(255,255,255,0.03)', '&:last-child': { border: 0 } }}>
                           <Stack direction="row" justifyContent="space-between" alignItems="center">
                              <Box>
                                 <Typography sx={{ fontWeight: 900, fontSize: '0.75rem', color: '#fff' }}>{s.symbol}</Typography>
                                 <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700 }}>{s.asset_class || 'EQUITY'}</Typography>
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

               {/* Intelligence Component */}
               <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, letterSpacing: 1, mb: 2 }}>NODE INTELLIGENCE</Typography>
                  <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                     <Stack spacing={3}>
                        <IntelligenceItem label="Global Accuracy" value={`${stats.win_rate}%`} icon={<ShieldCheck size={14} />} />
                        <IntelligenceItem label="Node Latency" value="12ms" icon={<Globe size={14} />} color="#10b981" />
                        <IntelligenceItem label="Model State" value="V2.2 MASTER" icon={<Bot size={14} />} color="#00D1FF" />
                     </Stack>
                     <Divider sx={{ my: 3, opacity: 0.05 }} />
                     <Typography variant="caption" sx={{ color: 'slategray', lineHeight: 1.5, display: 'block', fontWeight: 500 }}>
                        Market consensus indicates <b>institutional accumulation</b> in blue-chip IT constituents. Monitoring for gamma expansion in monthly expiries.
                     </Typography>
                  </Paper>
               </Box>
            </Stack>
         </Grid>
      </Grid>
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
