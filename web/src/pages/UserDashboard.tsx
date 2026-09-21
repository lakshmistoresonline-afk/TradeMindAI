import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Grid, Paper, Stack, alpha, Skeleton, Tabs, Tab, Button, Chip } from '@mui/material';
import { Zap, ShieldCheck, ArrowRight, PieChart } from 'lucide-react';
import { getMarketStats, getEquitySignals, getEquityMarketState } from '../api/client';
import { mapCanonicalSignal } from '../hooks/useAITradeDecision';
import { useTurboSync } from '../hooks/useTurboSync';
import LiveSignalCard from '../components/Research/shared/LiveSignalCard';
import { useNavigate } from 'react-router-dom';

export default function UserDashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [market, setMarket] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);
  const [tab, setTab] = useState(0);

  const { firestoreSignals, marketContext } = useTurboSync();

  const fetchData = async () => {
    setLoading(true);

    // 1. Kick off all requests in parallel
    const marketStatsPromise = getMarketStats();
    const marketStatePromise = getEquityMarketState();
    const signalsPromise = getEquitySignals({ limit: 12 }); // Optimized limit for dashboard summary

    // 2. Resolve market data first (usually faster and independent)
    marketStatsPromise.then(data => setStats(data)).catch(e => console.error("Stats Error:", e));
    marketStatePromise.then(data => setMarket(data)).catch(e => console.error("Market Error:", e));

    // 3. Resolve signals and manage loading state
    try {
      const signalsData = await signalsPromise;
      setSignals((signalsData || []).map((s: any) => mapCanonicalSignal(s)));
    } catch (e) {
      console.error("Dashboard Signals Fetch Failed:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Hybrid Sync (V2.3): Authoritatively merges Cloud API and Local PC Mirror
  useEffect(() => {
    if (firestoreSignals.length > 0) {
        const normalizedFS = firestoreSignals.map(s => mapCanonicalSignal(s));
        setSignals(prev => {
            const mergedMap = new Map();
            prev.forEach(s => mergedMap.set(s.id, s));
            normalizedFS.forEach(s => mergedMap.set(s.id, s));
            return Array.from(mergedMap.values()).sort((a,b) =>
                new Date(b.decision?.generatedAt || 0).getTime() - new Date(a.decision?.generatedAt || 0).getTime()
            );
        });
    }
    if (marketContext) {
        setMarket(marketContext);
    }
  }, [firestoreSignals, marketContext]);

  const filteredSignals = useMemo(() => {
    const horizon = ['SWING', 'SHORT', 'LONG'][tab];
    return signals.filter(s =>
      s.decision.timeframe === horizon &&
      ['ACTIVE', 'WAITING_FOR_ENTRY', 'ENTRY_TRIGGERED'].includes(s.decision.status)
    ).slice(0, 3);
  }, [signals, tab]);

  return (
    <Box sx={{ pb: 8, color: 'white' }}>
      {/* 1. Welcom Header */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>Welcome to TradeMind AI</Typography>
        <Typography variant="body1" sx={{ color: '#708090', mt: 1 }}>Auditable intelligence for your institutional investing journey.</Typography>
      </Box>

      {/* 2. Market Snapshot */}
      <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 3, color: '#708090', letterSpacing: 1 }}>MARKET SNAPSHOT</Typography>
      <Grid container spacing={3} sx={{ mb: 6 }}>
         <Grid item xs={12} md={3}>
            <MarketMiniCard label="NIFTY 200" data={stats?.['NIFTY 200']} value={market?.nifty_price} />
         </Grid>
         <Grid item xs={12} md={3}>
            <MarketMiniCard label="INDIA VIX" value={market?.vix || (stats?.['India VIX']?.value)} />
         </Grid>
         <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2.5, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', height: '100%' }}>
               <Typography variant="caption" sx={{ color: '#708090', fontWeight: 900, mb: 1, display: 'block' }}>REGIME</Typography>
               <Chip
                  label={market?.regime || 'SIDEWAYS'}
                  size="small"
                  sx={{
                    fontWeight: 950,
                    bgcolor: market?.regime === 'BULL' ? alpha('#10b981', 0.1) : (market?.regime === 'BEAR' ? alpha('#ef4444', 0.1) : alpha('#00D1FF', 0.1)),
                    color: market?.regime === 'BULL' ? '#10b981' : (market?.regime === 'BEAR' ? '#ef4444' : '#00D1FF')
                  }}
               />
            </Paper>
         </Grid>
         <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2.5, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', height: '100%' }}>
               <Typography variant="caption" sx={{ color: '#708090', fontWeight: 900, mb: 1, display: 'block' }}>DATA FRESHNESS</Typography>
               <Typography variant="body2" sx={{ fontWeight: 800, color: (market?.status === 'HEALTHY' || (stats?.['NIFTY 200']?.value > 0)) ? '#10b981' : 'orange' }}>
                  { (market?.status === 'HEALTHY' || (stats?.['NIFTY 200']?.value > 0)) ? '● LIVE FEED ACTIVE' : '● FEED DEGRADED' }
               </Typography>
            </Paper>
         </Grid>
      </Grid>

      {/* 3. Today's Top Signals */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 950 }}>TOP SIGNALS</Typography>
        <Button onClick={() => navigate('/signals')} endIcon={<ArrowRight size={16} />} sx={{ color: '#00D1FF', fontWeight: 800 }}>VIEW ALL</Button>
      </Box>

      <Paper sx={{ mb: 4, bgcolor: 'transparent', border: 'none', p: 0 }}>
        <Tabs
            value={tab}
            onChange={(_, v) => setTab(v)}
            sx={{
                mb: 4,
                '& .MuiTabs-indicator': { bgcolor: '#00D1FF' },
                '& .MuiTab-root': { color: '#708090', fontWeight: 900, fontSize: '0.75rem', '&.Mui-selected': { color: 'white' } }
            }}
        >
            <Tab label="SWING" />
            <Tab label="SHORT-TERM" />
            <Tab label="LONG-TERM" />
        </Tabs>
      </Paper>

      {loading ? (
        <Grid container spacing={3}>
           {[1, 2, 3].map(i => (
             <Grid item xs={12} md={4} key={i}>
                <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 1, bgcolor: 'rgba(255,255,255,0.02)' }} />
             </Grid>
           ))}
        </Grid>
      ) : (
        <Grid container spacing={3}>
           {filteredSignals.map(s => (
              <Grid item xs={12} md={4} key={s.id}>
                 <LiveSignalCard stock={s} decision={s.decision} variant="SIMPLE" />
              </Grid>
           ))}
           {filteredSignals.length === 0 && (
              <Grid item xs={12}>
                 <Paper sx={{ py: 10, textAlign: 'center', bgcolor: alpha('#0f172a', 0.5), border: '1px dashed rgba(255,255,255,0.1)' }}>
                    <Typography sx={{ color: '#708090', fontWeight: 800 }}>No current {['SWING', 'SHORT', 'LONG'][tab]} signals meeting conviction threshold.</Typography>
                 </Paper>
              </Grid>
           )}
        </Grid>
      )}

      {/* 4. Market Insights Feed */}
      <Box sx={{ mt: 10 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 3, color: '#708090', letterSpacing: 1 }}>MARKET INSIGHTS</Typography>
        <Grid container spacing={4}>
            <Grid item xs={12} md={8}>
                <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <Typography variant="h6" sx={{ fontWeight: 900, mb: 4 }}>SIGNAL REGIME CONTEXT</Typography>
                    <Stack spacing={3}>
                        <InsightItem
                            title="NIFTY Structural State"
                            desc={`The NIFTY-200 universe is currently in a ${market?.regime || 'SIDEWAYS'} regime with VIX at ${market?.vix?.toFixed(2) || '—'}.`}
                        />
                        <InsightItem
                            title="Momentum Alignment"
                            desc="Institutional order flow indicates sector rotation dynamics currently aligned with V2.2 quantitative nodes."
                        />
                    </Stack>
                </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
                <Paper sx={{ p: 0, bgcolor: alpha('#7C3AED', 0.02), border: '1px solid rgba(124, 58, 237, 0.1)', overflow: 'hidden' }}>
                    <Box sx={{ p: 3, bgcolor: alpha('#7C3AED', 0.1) }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 950, color: 'white' }}>PREMIUM INSIGHTS</Typography>
                    </Box>
                    <Box sx={{ p: 3, textAlign: 'center' }}>
                        <Zap size={40} color="#7C3AED" style={{ marginBottom: 16 }} />
                        <Typography variant="body2" sx={{ color: '#708090', fontWeight: 700, mb: 3 }}>
                            Unlock algorithmic sector strength analysis and institutional order flow metrics.
                        </Typography>
                        <Button variant="outlined" color="secondary" onClick={() => navigate('/pricing')} sx={{ fontWeight: 900 }}>GO PRO</Button>
                    </Box>
                </Paper>
            </Grid>
        </Grid>
      </Box>

      {/* 5. Quick Links */}
      <Box sx={{ mt: 10 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 3, color: '#708090', letterSpacing: 1 }}>PRODUCT DIRECTORY</Typography>
        <Grid container spacing={3}>
           <ToolCard
              icon={<ShieldCheck size={24} color="#10b981" />}
              title="Evidence Ledger"
              desc="Audit the bitwise forensic evidence behind our active signal generation."
              onClick={() => navigate('/evidence')}
           />
           <ToolCard
              icon={<PieChart size={24} color="#7C3AED" />}
              title="Track Record"
              desc="Audit our 100% transparent historical signal performance ledger."
              onClick={() => navigate('/performance')}
           />
           <ToolCard
              icon={<Zap size={24} color="#00D1FF" />}
              title="Premium"
              desc="Unlock institutional-grade deep dive forensics and advanced context."
              onClick={() => navigate('/pricing')}
           />
        </Grid>
      </Box>
    </Box>
  );
}

function MarketMiniCard({ label, data, value }: any) {
    const rawVal = value || data?.value || 0;
    const val = (rawVal === 0) ? '---' : rawVal;
    const change = data?.change || 0;
    const isPos = change >= 0;

    return (
        <Paper sx={{ p: 2.5, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', height: '100%' }}>
            <Typography variant="caption" sx={{ color: '#708090', fontWeight: 900, mb: 1, display: 'block' }}>{label}</Typography>
            <Stack direction="row" spacing={1.5} alignItems="baseline">
                <Typography sx={{ fontWeight: 950, fontSize: '1.2rem', fontFamily: 'JetBrains Mono' }}>{typeof val === 'number' ? val.toLocaleString() : val}</Typography>
                {data && rawVal !== 0 && (
                    <Typography sx={{ fontWeight: 900, fontSize: '0.75rem', color: isPos ? '#10b981' : '#ef4444' }}>
                        {isPos ? '+' : ''}{change}%
                    </Typography>
                )}
            </Stack>
        </Paper>
    );
}

function ToolCard({ icon, title, desc, onClick }: any) {
    return (
        <Grid item xs={12} md={4}>
            <Paper
                onClick={onClick}
                sx={{
                    p: 3,
                    cursor: 'pointer',
                    bgcolor: '#0f172a',
                    border: '1px solid rgba(255,255,255,0.05)',
                    transition: '0.2s',
                    '&:hover': { bgcolor: '#111827', borderColor: '#00D1FF', transform: 'translateY(-4px)' }
                }}
            >
                <Box sx={{ mb: 2 }}>{icon}</Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 950, mb: 1 }}>{title}</Typography>
                <Typography variant="body2" sx={{ color: '#708090', fontWeight: 700 }}>{desc}</Typography>
            </Paper>
        </Grid>
    );
}

function InsightItem({ title, desc }: any) {
    return (
        <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.03)' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 900, color: '#00D1FF', mb: 0.5 }}>{title}</Typography>
            <Typography variant="body2" sx={{ color: '#708090', fontWeight: 500 }}>{desc}</Typography>
        </Box>
    );
}
