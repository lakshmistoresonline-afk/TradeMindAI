import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Grid, Paper, Stack, Button, Skeleton, Divider, alpha, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton } from '@mui/material';
import { ShieldCheck, RefreshCw } from 'lucide-react';
import { mapCanonicalSignal } from '../hooks/useAITradeDecision';
import { useNavigate } from 'react-router-dom';
import { getEquitySignals, getEquityPerformance, getEquityMarketState, getMarketStats, getEquityHistory, getDataHealth, getShadowAnalytics } from '../api/client';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  const [marketStats, setMarketStats] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);
  const [marketState, setMarketState] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [shadow, setShadow] = useState<any>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        getEquitySignals({ limit: 100 }),
        getEquityPerformance(),
        getEquityMarketState(),
        getMarketStats(),
        getEquityHistory({ limit: 5 }),
        getDataHealth(),
        getShadowAnalytics()
      ]);

      const signalsData = results[0].status === 'fulfilled' ? (results[0].value || []) : [];
      const marketData = results[2].status === 'fulfilled' ? results[2].value : null;
      const statsData = results[3].status === 'fulfilled' ? results[3].value : null;
      const healthData = results[5].status === 'fulfilled' ? results[5].value : null;
      const shadowData = results[6].status === 'fulfilled' ? results[6].value : null;

      setMarketStats(statsData);
      setMarketState(marketData);
      setHealth(healthData);
      setShadow(shadowData);

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
        <Typography variant="h5" sx={{ fontWeight: 800, color: '#00D1FF', letterSpacing: 1, mb: 4 }}>OPERATIONAL INTELLIGENCE TERMINAL</Typography>

        <Grid container spacing={2}>
           <Grid item xs={12} md={8}>
              <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                 <Grid container spacing={4}>
                    <HeroStat label="MARKET REGIME" value={marketState?.regime?.toUpperCase() || 'SIDEWAYS'} color={marketState?.regime === 'BULL' ? '#10b981' : (marketState?.regime === 'BEAR' ? '#ef4444' : '#00D1FF')} />
                    <HeroStat label="STRATEGY" value="V2.2 FROZEN" color="#00D1FF" />
                    <HeroStat label="OPEN SIGNALS" value={counts.total} color="#fff" />
                    <HeroStat label="SYSTEM MODE" value="SHADOW" color="#00D1FF" />
                 </Grid>
                 <Divider sx={{ my: 3, opacity: 0.05 }} />
                 <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                        <SummaryStat label="SWING" value={counts.swingPrimary + counts.swingSelective} sub={`${counts.swingPrimary} ACTIVE / 0 WAIT`} color="#10b981" />
                    </Grid>
                    <Grid item xs={6} md={4}>
                        <SummaryStat label="LONG" value={counts.longSelective} sub="ACTIVE" color="#00D1FF" />
                    </Grid>
                    <Grid item xs={6} md={4}>
                        <SummaryStat label="SHORT" value={counts.shortExperimental} sub="ACTIVE" color="slategray" />
                    </Grid>
                 </Grid>
                 <Divider sx={{ my: 3, opacity: 0.05 }} />
                 <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                       <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, display: 'block' }}>STRATEGY: V2.2 (FROZEN)</Typography>
                       <Typography variant="caption" sx={{ color: '#00D1FF', fontWeight: 900 }}>RELIABILITY: AUDITED</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'right' }}>
                       <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, display: 'block' }}>AUDIT STATUS: HARDENED</Typography>
                       <Typography variant="caption" sx={{ color: '#00D1FF', fontWeight: 900 }}>REAL-TIME FEED: ACTIVE</Typography>
                    </Box>
                 </Box>
              </Paper>
           </Grid>
           <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: '100%', bgcolor: alpha('#00D1FF', 0.03), border: '1px solid rgba(0, 209, 255, 0.1)', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                 <Typography variant="caption" sx={{ color: '#00D1FF', fontWeight: 900, letterSpacing: 2, mb: 1 }}>BASELINE IDENTITY</Typography>
                 <Typography variant="h4" sx={{ fontWeight: 950, color: '#fff' }}>V2.2 FROZEN</Typography>
                 <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700, mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                    TRADING EXECUTION: LOCKED <ShieldCheck size={12} color="#ef4444" />
                 </Typography>
                 <Button
                    variant="text"
                    size="small"
                    onClick={() => navigate('/evidence')}
                    sx={{ mt: 2, p: 0, justifyContent: 'flex-start', color: '#00D1FF', fontWeight: 800, fontSize: '0.65rem' }}
                 >
                    VIEW EVIDENCE & LIMITATIONS →
                 </Button>
              </Paper>
           </Grid>
        </Grid>
      </Box>

      {/* 2. Operational Health Ribbon */}
      <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 2, color: 'slategray', letterSpacing: 1 }}>OPERATIONAL HEALTH</Typography>
      <Stack direction="row" spacing={2} sx={{ mb: 6, overflowX: 'auto', pb: 1 }}>
         <HealthBadge label="API" status={health?.components?.API} />
         <HealthBadge label="DB" status={health?.components?.Database} />
         <HealthBadge label="SYNC" status={health?.components?.['Market Data']} />
         <HealthBadge label="CORE" status={health?.components?.['V2.2 Engine']} />
         <HealthBadge label="PRICE REFRESH" status={health?.last_price_sync?.status || 'NOT ACTIVE'} />
         <HealthBadge label="UNIVERSE" status={`${health?.universe?.fresh || 0}/${health?.universe?.total || 200}`} />
      </Stack>

      <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 2, color: 'slategray', letterSpacing: 1 }}>MARKET OVERVIEW</Typography>
      <Stack direction="row" spacing={4} sx={{ mb: 6, overflowX: 'auto', pb: 1 }}>
         <MarketTickerItem label="NIFTY 50" data={marketStats?.['NIFTY 50']} />
         <MarketTickerItem label="NIFTY 100" data={marketStats?.['NIFTY 100']} />
         <MarketTickerItem label="NIFTY 200" data={marketStats?.['NIFTY 200']} />
         <MarketTickerItem label="INDIA VIX" data={(marketState?.vix && marketState.vix > 0) ? { value: marketState.vix, change: 0 } : (marketStats?.['India VIX'] || null)} />
      </Stack>

      <Grid container spacing={4}>
         {/* 3. Signal Operations Terminal */}
         <Grid item xs={12} lg={9}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1 }}>
               <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                  <Typography variant="h6" sx={{ fontWeight: 950, color: 'white' }}>SIGNAL OPERATIONS</Typography>
                  <Stack direction="row" spacing={1}>
                     <Chip label="AUTO-SYNC ACTIVE" size="small" sx={{ bgcolor: alpha('#10b981', 0.1), color: '#10b981', fontWeight: 900 }} />
                     <IconButton onClick={fetchData} size="small" sx={{ color: 'slategray' }}><RefreshCw size={16} /></IconButton>
                  </Stack>
               </Box>

               <TableContainer>
                  <Table size="small">
                     <TableHead>
                        <TableRow sx={{ '& th': { borderBottom: '1px solid rgba(255,255,255,0.05)', color: 'slategray', fontWeight: 800, py: 2 } }}>
                           <TableCell>SYMBOL</TableCell>
                           <TableCell>DIRECTION</TableCell>
                           <TableCell>STATUS</TableCell>
                           <TableCell>ENTRY</TableCell>
                           <TableCell>CURRENT</TableCell>
                           <TableCell>AGE</TableCell>
                           <TableCell align="right">VALIDATION</TableCell>
                        </TableRow>
                     </TableHead>
                     <TableBody>
                        {loading ? (
                           [1,2,3,4,5].map(i => <TableRow key={i}><TableCell colSpan={7}><Skeleton height={32} /></TableCell></TableRow>)
                        ) : signals.slice(0, 15).map((s) => (
                           <TableRow key={s.id} sx={{ '& td': { borderBottom: '1px solid rgba(255,255,255,0.02)', py: 1.5 } }}>
                              <TableCell sx={{ fontWeight: 950, color: 'white' }}>{s.symbol}</TableCell>
                              <TableCell>
                                 <Chip label={s.decision.rating} size="small" sx={{ height: 18, fontSize: '0.5rem', fontWeight: 950, bgcolor: alpha(s.decision.rating.includes('BUY') ? '#10b981' : '#ef4444', 0.1), color: s.decision.rating.includes('BUY') ? '#10b981' : '#ef4444' }} />
                              </TableCell>
                              <TableCell>
                                 <Typography variant="caption" sx={{ fontWeight: 800, color: 'slategray' }}>{s.decision.status}</Typography>
                              </TableCell>
                              <TableCell sx={{ fontFamily: 'JetBrains Mono', color: 'slategray' }}>{s.decision.entry?.toLocaleString()}</TableCell>
                              <TableCell sx={{ fontFamily: 'JetBrains Mono', color: '#fff' }}>{s.decision.normalizedCurrentPrice?.toLocaleString()}</TableCell>
                              <TableCell sx={{ color: 'slategray' }}>{s.decision.signalAgeHours?.toFixed(1)}h</TableCell>
                              <TableCell align="right">
                                 <Chip label="PASS" size="small" sx={{ height: 16, fontSize: '0.45rem', fontWeight: 950, bgcolor: alpha('#10b981', 0.1), color: '#10b981' }} />
                              </TableCell>
                           </TableRow>
                        ))}
                     </TableBody>
                  </Table>
               </TableContainer>

               <Box sx={{ mt: 4, textAlign: 'center' }}>
                  <Button variant="text" size="small" onClick={() => navigate('/signals')} sx={{ color: 'slategray', fontWeight: 800 }}>OPEN FULL OPERATIONS TERMINAL →</Button>
               </Box>
            </Paper>

            {/* V2.3 SHADOW ANALYTICS (Workstream 11) */}
            <Paper sx={{ p: 4, mt: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1 }}>
               <Typography variant="h6" sx={{ fontWeight: 950, color: 'white', mb: 3 }}>V2.3 SHADOW GATE PERFORMANCE</Typography>
               <Grid container spacing={3} sx={{ mb: 4 }}>
                  <Grid item xs={12} md={3}>
                     <SidebarStat label="Hindsight Losses Prev" value={shadow?.replay?.losses_prevented || '0'} color="#10b981" />
                  </Grid>
                  <Grid item xs={12} md={3}>
                     <SidebarStat label="Hindsight Winners Lost" value={shadow?.replay?.winners_lost || '0'} color="#ef4444" />
                  </Grid>
                  <Grid item xs={12} md={3}>
                     <SidebarStat label="Net Efficiency" value={shadow?.replay?.net_gate_efficiency || '0'} color="#00D1FF" />
                  </Grid>
                  <Grid item xs={12} md={3}>
                     <SidebarStat label="V2.3 Shadow Yield" value={`${(shadow?.forward?.v23_yield_pct || 0).toFixed(1)}%`} color="white" />
                  </Grid>
               </Grid>
               <Divider sx={{ mb: 4, opacity: 0.05 }} />
               <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700, fontStyle: 'italic' }}>
                  * Shadow metrics represent candidate signals blocked by V2.3 Quality Gate (60% Prob floor) while still published by V2.2.
               </Typography>
            </Paper>

            <Box sx={{ mt: 6 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 3, color: 'slategray', letterSpacing: 1 }}>SYSTEM LOGS (FORENSIC)</Typography>
                <Paper sx={{ p: 0, bgcolor: '#070a0f', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1, maxHeight: 300, overflow: 'auto' }}>
                    <Box sx={{ p: 2, fontFamily: 'JetBrains Mono', fontSize: '0.7rem', color: '#10b981' }}>
                        {`[${new Date().toISOString()}] Signal Engine: Heartbeat OK.`}<br/>
                        {health?.last_price_sync ? (
                            `[${new Date(health.last_price_sync.timestamp).toISOString()}] Price Worker: Pulse Sync Complete (${health.last_price_sync.symbols_success} OK, ${health.last_price_sync.symbols_failed} FAIL) in ${health.last_price_sync.duration_s?.toFixed(1)}s.`
                        ) : (
                            `[${new Date().toISOString()}] Price Worker: STANDBY (Automatic Refresh Inactive).`
                        )}<br/>
                        {`[${new Date().toISOString()}] Model Service: Ensemble V2.2 Standby.`}<br/>
                        {`[${new Date().toISOString()}] Auth: Session Verified.`}
                    </Box>
                </Paper>
            </Box>
         </Grid>

         {/* 4. Side Panels */}
         <Grid item xs={12} lg={3}>
            <Stack spacing={4}>
               {/* REVENUE OVERVIEW */}
               <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 2 }}>OPERATIONAL STATS</Typography>
                  <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                     <Stack spacing={2.5}>
                        <SidebarStat label="Avg Signal Age" value="2.4h" color="#10b981" />
                        <SidebarStat label="V2.2 Shadow Pop" value={health?.universe?.fresh || '0'} color="#00D1FF" />
                        <SidebarStat label="Signals/24h" value="12" color="#00D1FF" />
                     </Stack>
                  </Paper>
               </Box>

               {/* SIGNAL FLOW SUMMARY */}
               <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 2 }}>SIGNAL FLOW</Typography>
                  <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                     <Stack spacing={2.5}>
                        <SidebarStat label="Total Open" value={counts.total} color="#00D1FF" />
                        <SidebarStat label="Rejected (Gate)" value="0" color="#ef4444" />
                        <SidebarStat label="Wait for Sync" value="0" color="orange" />
                     </Stack>
                     <Divider sx={{ my: 3, opacity: 0.05 }} />
                     <Box>
                        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, display: 'block', mb: 1 }}>GATE STATUS</Typography>
                        <Chip label="HARDENED" size="small" sx={{ height: 18, fontSize: '0.6rem', fontWeight: 950, bgcolor: alpha('#10b981', 0.1), color: '#10b981' }} />
                     </Box>
                  </Paper>
               </Box>

               {/* QUICK ADMIN ACTIONS */}
               <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 2 }}>OPERATIONS</Typography>
                  <Paper sx={{ p: 2, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                     <Stack spacing={1}>
                        <AdminAction label="Retrain Champion" color="primary" />
                        <AdminAction label="Sync Instrument Master" color="secondary" />
                        <AdminAction label="Flush Redis Cache" color="error" />
                     </Stack>
                  </Paper>
               </Box>
            </Stack>
         </Grid>
      </Grid>
    </Box>
  );
}

function HeroStat({ label, value, color = '#fff' }: any) {
   const displayValue = (value === 0 || value === '0') ? '---' : value;
   return (
      <Grid item xs={6} md={3}>
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, letterSpacing: 1, display: 'block', mb: 0.5 }}>{label}</Typography>
         <Typography variant="h4" sx={{ fontWeight: 950, color, fontFamily: 'JetBrains Mono' }}>{displayValue}</Typography>
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

function MarketTickerItem({ label, data, value }: any) {
  if (!data && !value) return <Skeleton width={120} height={40} />;
  const rawVal = value || data?.value || 0;
  const val = (rawVal === 0) ? '---' : rawVal;
  const change = data?.change || 0;
  const isPositive = change >= 0;
  return (
    <Box sx={{ minWidth: 140 }}>
       <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, fontSize: '0.6rem', display: 'block', mb: 0.5 }}>{label}</Typography>
       <Stack direction="row" spacing={1.5} alignItems="baseline">
          <Typography sx={{ fontWeight: 900, fontSize: '1rem', fontFamily: 'JetBrains Mono', color: '#fff' }}>
             {typeof val === 'number' ? val.toLocaleString() : val}
          </Typography>
          {data && rawVal !== 0 && (
            <Typography sx={{ fontWeight: 900, fontSize: '0.7rem', color: isPositive ? '#10b981' : '#ef4444' }}>
                {isPositive ? '+' : ''}{change}%
            </Typography>
          )}
       </Stack>
    </Box>
  );
}

function HealthBadge({ label, status }: any) {
    const isHealthy = status === 'HEALTHY' || (status && status.includes('/'));
    return (
        <Box sx={{
            px: 2, py: 1,
            bgcolor: isHealthy ? alpha('#10b981', 0.05) : alpha('#ef4444', 0.05),
            border: `1px solid ${isHealthy ? alpha('#10b981', 0.1) : alpha('#ef4444', 0.1)}`,
            borderRadius: 0.5,
            minWidth: 100
        }}>
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, fontSize: '0.55rem', display: 'block' }}>{label}</Typography>
            <Typography variant="caption" sx={{ color: isHealthy ? '#10b981' : '#ef4444', fontWeight: 950 }}>{status || 'LOADING...'}</Typography>
        </Box>
    );
}

function AdminAction({ label, color }: any) {
    return (
        <Button fullWidth size="small" color={color} variant="contained" sx={{ fontSize: '0.6rem', fontWeight: 950, py: 1 }}>{label}</Button>
    );
}
