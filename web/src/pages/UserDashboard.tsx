import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Grid, Paper, Stack, alpha, Skeleton, Tabs, Tab, Button, Chip } from '@mui/material';
import { Zap, ShieldCheck, ArrowRight, PieChart, Activity, TrendingUp, Cpu } from 'lucide-react';
import { getMarketStats, getEquitySignals, getEquityMarketState } from '../api/client';
import { mapCanonicalSignal } from '../hooks/useAITradeDecision';
import { useTurboSync } from '../hooks/useTurboSync';
import { useBackendHealth } from '../hooks/useBackendHealth';
import SignalCard from '../components/Research/shared/SignalCard';
import { useNavigate } from 'react-router-dom';

export default function UserDashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [market, setMarket] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);
  const [tab, setTab] = useState(0);

  const { isOnline } = useBackendHealth();
  const { firestoreSignals, marketContext } = useTurboSync();

  const fetchData = async () => {
    setLoading(true);

    const marketStatsPromise = getMarketStats();
    const marketStatePromise = getEquityMarketState();
    const signalsPromise = getEquitySignals({ limit: 12 });

    marketStatsPromise.then(data => setStats(data)).catch(e => console.error("Stats Error:", e));
    marketStatePromise.then(data => setMarket(data)).catch(e => console.error("Market Error:", e));

    try {
      const signalsData = await signalsPromise;
      const normalized = (signalsData || []).map((s: any) => mapCanonicalSignal(s));

      setSignals(prev => {
          const mergedMap = new Map();
          prev.forEach((s: any) => mergedMap.set(s.id, s));
          normalized.forEach((s: any) => mergedMap.set(s.id, s));
          return Array.from(mergedMap.values()).sort((a: any, b: any) =>
              new Date(b.decision?.generatedAt || 0).getTime() - new Date(a.decision?.generatedAt || 0).getTime()
          );
      });
    } catch (e) {
      console.error("Dashboard Signals Fetch Failed:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (firestoreSignals.length === 0) return;

    const normalizedFS = firestoreSignals.map(s => ({ ...mapCanonicalSignal(s), _isFirestore: true }));

    setSignals(prev => {
        const mergedMap = new Map();
        prev.forEach(s => mergedMap.set(s.id, s));
        normalizedFS.forEach(s => mergedMap.set(s.id, s));

        return Array.from(mergedMap.values()).sort((a,b) =>
            new Date(b.decision?.generatedAt || 0).getTime() - new Date(a.decision?.generatedAt || 0).getTime()
        );
    });

    if (marketContext) {
        setMarket(marketContext);
    }
  }, [firestoreSignals, marketContext]);

  const filteredSignals = useMemo(() => {
    const horizon = ['SWING', 'SHORT', 'LONG'][tab];
    return signals.filter(s => {
      const isLongTrade = s.decision?.direction === 'LONG' || s.decision?.rating?.includes('BUY');
      return isLongTrade &&
        s.decision?.timeframe === horizon &&
        ['ACTIVE', 'WAITING_FOR_ENTRY', 'ENTRY_TRIGGERED'].includes(s.decision?.status);
    }).slice(0, 3);
  }, [signals, tab]);

  return (
    <Box sx={{ pb: 8, color: 'white' }}>
      {/* 1. Welcome Header Banner */}
      <Box sx={{
        mb: 6,
        p: 4,
        borderRadius: 3,
        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(11, 19, 41, 0.8))',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        backdropFilter: 'blur(16px)',
        boxShadow: '0 20px 40px -15px rgba(0, 0, 0, 0.5)',
        display: 'flex',
        justify: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 2,
        position: 'relative',
        overflow: 'hidden'
      }}>
        <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: 'linear-gradient(90deg, #00D1FF, #7C3AED, #10b981)' }} />
        <Box>
          <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 1 }}>
            <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1, color: '#f8fafc' }}>
              EXECUTIVE TERMINAL
            </Typography>
            <Chip label="NIFTY-200 LIVE" size="small" sx={{ bgcolor: alpha('#00D1FF', 0.15), color: '#00D1FF', border: '1px solid rgba(0, 209, 255, 0.3)', fontWeight: 950, fontSize: '0.65rem' }} />
          </Stack>
          <Typography variant="body1" sx={{ color: '#94a3b8', fontWeight: 600 }}>
            Auditable quantitative intelligence, institutional order flow, and Strategy V2.3 signals.
          </Typography>
        </Box>
        <Chip
          icon={<Activity size={14} color={isOnline ? '#10b981' : '#f59e0b'} />}
          label={isOnline ? '🟢 LOCAL SERVER CONNECTED' : '🟡 OFFLINE CLIENT MODE'}
          size="medium"
          sx={{
            fontWeight: 950,
            fontSize: '0.7rem',
            px: 1,
            height: 32,
            bgcolor: isOnline ? alpha('#10b981', 0.12) : alpha('#f59e0b', 0.12),
            color: isOnline ? '#10b981' : '#f59e0b',
            border: `1px solid ${isOnline ? alpha('#10b981', 0.3) : alpha('#f59e0b', 0.3)}`
          }}
        />
      </Box>

      {/* 2. Market Snapshot */}
      <Typography variant="subtitle2" sx={{ fontWeight: 950, mb: 2.5, color: '#64748b', letterSpacing: 1.5, fontFamily: 'JetBrains Mono, monospace' }}>
        NIFTY-200 MARKET SNAPSHOT
      </Typography>
      <Grid container spacing={3} sx={{ mb: 6 }}>
         <Grid item xs={12} md={3}>
            <MarketMiniCard label="NIFTY 200" data={stats?.['NIFTY 200']} value={market?.nifty_price} icon={<TrendingUp size={18} color="#00D1FF" />} />
         </Grid>
         <Grid item xs={12} md={3}>
            <MarketMiniCard label="INDIA VIX" value={market?.vix || (stats?.['India VIX']?.value)} icon={<Activity size={18} color="#a855f7" />} />
         </Grid>
         <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2.5, bgcolor: 'rgba(15, 23, 42, 0.85)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2, height: '100%' }}>
               <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 950, mb: 1, display: 'block', letterSpacing: 1 }}>REGIME STATE</Typography>
               <Chip
                  label={market?.regime || 'SIDEWAYS'}
                  size="small"
                  sx={{
                    fontWeight: 950,
                    px: 1,
                    bgcolor: market?.regime === 'BULL' ? alpha('#10b981', 0.15) : (market?.regime === 'BEAR' ? alpha('#f43f5e', 0.15) : alpha('#00D1FF', 0.15)),
                    color: market?.regime === 'BULL' ? '#10b981' : (market?.regime === 'BEAR' ? '#f43f5e' : '#00D1FF'),
                    border: `1px solid ${market?.regime === 'BULL' ? alpha('#10b981', 0.3) : (market?.regime === 'BEAR' ? alpha('#f43f5e', 0.3) : alpha('#00D1FF', 0.3))}`
                  }}
               />
            </Paper>
         </Grid>
         <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2.5, bgcolor: 'rgba(15, 23, 42, 0.85)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2, height: '100%' }}>
               <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 950, mb: 1, display: 'block', letterSpacing: 1 }}>DATA FEED INTEGRITY</Typography>
               <Typography variant="body2" sx={{ fontWeight: 950, color: (market?.status === 'HEALTHY' || (stats?.['NIFTY 200']?.value > 0)) ? '#10b981' : '#f59e0b', fontFamily: 'JetBrains Mono, monospace' }}>
                  { (market?.status === 'HEALTHY' || (stats?.['NIFTY 200']?.value > 0)) ? '● LIVE FEED ACTIVE' : '● FEED DEGRADED' }
               </Typography>
            </Paper>
         </Grid>
      </Grid>

      {/* 3. Today's Top Signals */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 950, letterSpacing: -0.5 }}>TOP QUANTITATIVE OPPORTUNITIES</Typography>
        <Button onClick={() => navigate('/signals')} endIcon={<ArrowRight size={16} />} sx={{ color: '#00D1FF', fontWeight: 950 }}>VIEW TERMINAL →</Button>
      </Box>

      <Paper sx={{ mb: 4, bgcolor: 'transparent', border: 'none', p: 0 }}>
        <Tabs
            value={tab}
            onChange={(_, v) => setTab(v)}
            sx={{
                mb: 3,
                '& .MuiTabs-indicator': { bgcolor: '#00D1FF', height: 3 },
                '& .MuiTab-root': { color: '#64748b', fontWeight: 950, fontSize: '0.75rem', letterSpacing: 1, '&.Mui-selected': { color: '#f8fafc' } }
            }}
        >
            <Tab label="SWING (1-30D)" />
            <Tab label="SHORT HORIZON" />
            <Tab label="LONG HORIZON" />
        </Tabs>
      </Paper>

      {loading ? (
        <Grid container spacing={3}>
           {[1, 2, 3].map(i => (
             <Grid item xs={12} md={4} key={i}>
                <Skeleton variant="rectangular" height={360} sx={{ borderRadius: 2, bgcolor: 'rgba(255,255,255,0.02)' }} />
             </Grid>
           ))}
        </Grid>
      ) : (
        <Grid container spacing={3}>
           {filteredSignals.map(s => (
              <Grid item xs={12} md={4} key={s.id}>
                 <SignalCard stock={s} decision={s.decision} />
              </Grid>
           ))}
           {filteredSignals.length === 0 && (
              <Grid item xs={12}>
                 <Paper sx={{ py: 8, textAlign: 'center', bgcolor: 'rgba(15, 23, 42, 0.4)', border: '1px dashed rgba(255,255,255,0.1)', borderRadius: 2 }}>
                    <Typography sx={{ color: '#64748b', fontWeight: 800 }}>No current {['SWING', 'SHORT', 'LONG'][tab]} signals meeting conviction threshold.</Typography>
                 </Paper>
              </Grid>
           )}
        </Grid>
      )}

      {/* 4. Market Insights Feed */}
      <Box sx={{ mt: 8 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 950, mb: 2.5, color: '#64748b', letterSpacing: 1.5, fontFamily: 'JetBrains Mono, monospace' }}>MARKET INSIGHTS & REGIME</Typography>
        <Grid container spacing={4}>
            <Grid item xs={12} md={8}>
                <Paper sx={{ p: 4, bgcolor: 'rgba(15, 23, 42, 0.85)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 950, mb: 3 }}>SIGNAL REGIME CONTEXT</Typography>
                    <Stack spacing={2.5}>
                        <InsightItem
                            title="NIFTY Structural State"
                            desc={`The NIFTY-200 universe is currently in a ${market?.regime || 'SIDEWAYS'} regime with VIX at ${market?.vix?.toFixed(2) || '—'}.`}
                        />
                        <InsightItem
                            title="Momentum Alignment"
                            desc="Institutional order flow indicates sector rotation dynamics currently aligned with V2.3 quantitative ensemble nodes."
                        />
                    </Stack>
                </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
                <Paper sx={{ p: 0, bgcolor: alpha('#7C3AED', 0.03), border: '1px solid rgba(124, 58, 237, 0.2)', borderRadius: 2, overflow: 'hidden' }}>
                    <Box sx={{ p: 3, bgcolor: alpha('#7C3AED', 0.12) }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 950, color: 'white', letterSpacing: 1 }}>INSTITUTIONAL PRO ACCESS</Typography>
                    </Box>
                    <Box sx={{ p: 3, textAlign: 'center' }}>
                        <Zap size={36} color="#a855f7" style={{ marginBottom: 12 }} />
                        <Typography variant="body2" sx={{ color: '#94a3b8', fontWeight: 700, mb: 3 }}>
                            Unlock algorithmic sector strength analysis, multi-agent AI debates, and institutional order flow metrics.
                        </Typography>
                        <Button variant="outlined" color="secondary" onClick={() => navigate('/pricing')} sx={{ fontWeight: 950, px: 3 }}>GO PRO</Button>
                    </Box>
                </Paper>
            </Grid>
        </Grid>
      </Box>

      {/* 5. Quick Links */}
      <Box sx={{ mt: 8 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 950, mb: 2.5, color: '#64748b', letterSpacing: 1.5, fontFamily: 'JetBrains Mono, monospace' }}>PRODUCT DIRECTORY</Typography>
        <Grid container spacing={3}>
           <ToolCard
              icon={<ShieldCheck size={24} color="#10b981" />}
              title="Evidence Ledger"
              desc="Audit the bitwise forensic evidence behind our active signal generation."
              onClick={() => navigate('/evidence')}
           />
           <ToolCard
              icon={<PieChart size={24} color="#a855f7" />}
              title="Track Record"
              desc="Audit our 100% transparent historical signal performance ledger."
              onClick={() => navigate('/performance')}
           />
           <ToolCard
              icon={<Cpu size={24} color="#00D1FF" />}
              title="Quant Engine"
              desc="Explore the strategy V2.3 ensemble models and multi-stage quality gates."
              onClick={() => navigate('/methodology')}
           />
        </Grid>
      </Box>
    </Box>
  );
}

function MarketMiniCard({ label, data, value, icon }: any) {
    const rawVal = value || data?.value || 0;
    const val = (rawVal === 0) ? '---' : rawVal;
    const change = data?.change || 0;
    const isPos = change >= 0;

    return (
        <Paper sx={{ p: 2.5, bgcolor: 'rgba(15, 23, 42, 0.85)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2, height: '100%' }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 950, letterSpacing: 1 }}>{label}</Typography>
                {icon}
            </Stack>
            <Stack direction="row" spacing={1.5} alignItems="baseline">
                <Typography sx={{ fontWeight: 950, fontSize: '1.25rem', fontFamily: 'JetBrains Mono, monospace' }}>{typeof val === 'number' ? val.toLocaleString() : val}</Typography>
                {data && rawVal !== 0 && (
                    <Typography sx={{ fontWeight: 950, fontSize: '0.75rem', color: isPos ? '#10b981' : '#f43f5e' }}>
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
                    bgcolor: 'rgba(15, 23, 42, 0.85)',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: 2,
                    transition: 'all 0.2s ease-in-out',
                    '&:hover': { bgcolor: 'rgba(15, 23, 42, 0.95)', borderColor: '#00D1FF', transform: 'translateY(-3px)', boxShadow: '0 10px 25px -10px rgba(0,209,255,0.2)' }
                }}
            >
                <Box sx={{ mb: 2 }}>{icon}</Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 950, mb: 0.5 }}>{title}</Typography>
                <Typography variant="body2" sx={{ color: '#94a3b8', fontWeight: 600 }}>{desc}</Typography>
            </Paper>
        </Grid>
    );
}

function InsightItem({ title, desc }: any) {
    return (
        <Box sx={{ p: 2, bgcolor: 'rgba(2, 6, 23, 0.4)', borderRadius: 1.5, border: '1px solid rgba(255,255,255,0.04)' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 950, color: '#00D1FF', mb: 0.5 }}>{title}</Typography>
            <Typography variant="body2" sx={{ color: '#94a3b8', fontWeight: 500 }}>{desc}</Typography>
        </Box>
    );
}
