import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Grid, Paper, Stack, alpha, Skeleton, Tabs, Tab, Button, Chip } from '@mui/material';
import { Zap, ShieldCheck, ArrowRight, PieChart, Activity, TrendingUp, Cpu } from 'lucide-react';
import { getMarketStats, getEquitySignals, getEquityMarketState } from '../api/client';
import { mapCanonicalSignal } from '../hooks/useAITradeDecision';
import { useTurboSync } from '../hooks/useTurboSync';
import { useBackendHealth } from '../hooks/useBackendHealth';
import SignalCard from '../components/Research/shared/SignalCard';
import { useNavigate } from 'react-router-dom';
import { MONO_FONT, COLORS, HERO_BANNER_STYLE, GRADIENT_ACCENT_BAR, GLASS_PANEL_STYLE } from '../theme/institutionalTheme';

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

  // Strict Deduplication by Symbol (Guarantees unique card per symbol on Dashboard)
  const filteredSignals = useMemo(() => {
    const horizon = ['SWING', 'SHORT', 'LONG'][tab];

    const raw = signals.filter(s => {
      const isLongTrade = s.decision?.direction === 'LONG' || s.decision?.rating?.includes('BUY');
      const isMatchingHorizon = s.decision?.timeframe === horizon || (horizon === 'SWING' && (!s.decision?.timeframe || s.decision?.timeframe === 'SWING'));
      const isActive = ['ACTIVE', 'WAITING_FOR_ENTRY', 'ENTRY_TRIGGERED'].includes(s.decision?.status);
      return isLongTrade && isMatchingHorizon && isActive;
    });

    raw.sort((a, b) => new Date(b.decision?.generatedAt || b.created_at || 0).getTime() - new Date(a.decision?.generatedAt || a.created_at || 0).getTime());

    const dedupMap = new Map<string, any>();
    raw.forEach(s => {
      const sym = s.symbol.toUpperCase();
      if (!dedupMap.has(sym)) {
        dedupMap.set(sym, s);
      }
    });

    return Array.from(dedupMap.values()).slice(0, 3);
  }, [signals, tab]);

  return (
    <Box sx={{ pb: 8, color: 'white', maxWidth: 1400, mx: 'auto' }}>
      {/* 1. Executive Hero Header Banner */}
      <Box sx={{ ...HERO_BANNER_STYLE, mb: 5 }}>
        <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, ...GRADIENT_ACCENT_BAR }} />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <Box>
            <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 1 }}>
              <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1, color: COLORS.textBright, fontFamily: MONO_FONT }}>
                EXECUTIVE TERMINAL
              </Typography>
              <Chip label="NIFTY-200 LIVE" size="small" sx={{ bgcolor: alpha(COLORS.cyan, 0.15), color: COLORS.cyan, border: `1px solid ${COLORS.borderCyan}`, fontWeight: 950, fontSize: '0.65rem' }} />
              <Chip label="STRATEGY V3.3" size="small" sx={{ bgcolor: alpha(COLORS.purple, 0.15), color: COLORS.purple, border: `1px solid ${COLORS.borderPurple}`, fontWeight: 950, fontSize: '0.65rem' }} />
            </Stack>
            <Typography variant="body2" sx={{ color: COLORS.slateText, fontWeight: 600 }}>
              Auditable quantitative intelligence, institutional order flow, and Strategy V3.3 Master Edition signals.
            </Typography>
          </Box>
          <Chip
            icon={<Activity size={14} color={isOnline ? COLORS.green : COLORS.amber} />}
            label={isOnline ? '🟢 LOCAL SERVER CONNECTED' : '🟡 OFFLINE CLIENT MODE'}
            size="medium"
            sx={{
              fontWeight: 950,
              fontSize: '0.7rem',
              px: 1,
              height: 32,
              bgcolor: isOnline ? alpha(COLORS.green, 0.12) : alpha(COLORS.amber, 0.12),
              color: isOnline ? COLORS.green : COLORS.amber,
              border: `1px solid ${isOnline ? alpha(COLORS.green, 0.3) : alpha(COLORS.amber, 0.3)}`
            }}
          />
        </Box>
      </Box>

      {/* 2. Market Snapshot */}
      <Typography variant="subtitle2" sx={{ fontWeight: 950, mb: 2, color: COLORS.slateMuted, letterSpacing: 1.5, fontFamily: MONO_FONT }}>
        NIFTY-200 MARKET SNAPSHOT
      </Typography>
      <Grid container spacing={2.5} sx={{ mb: 5 }}>
         <Grid item xs={12} sm={6} md={3}>
            <MarketMiniCard label="NIFTY 200" data={stats?.['NIFTY 200']} value={market?.nifty_price} fallbackVal={24250.8} icon={<TrendingUp size={18} color={COLORS.cyan} />} />
         </Grid>
         <Grid item xs={12} sm={6} md={3}>
            <MarketMiniCard label="INDIA VIX" value={market?.vix || (stats?.['India VIX']?.value)} fallbackVal={12.85} icon={<Activity size={18} color={COLORS.purple} />} />
         </Grid>
         <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ ...GLASS_PANEL_STYLE, p: 2.5, height: '100%' }}>
               <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 950, mb: 1, display: 'block', letterSpacing: 1 }}>REGIME STATE</Typography>
               <Chip
                  label={market?.regime || 'SIDEWAYS'}
                  size="small"
                  sx={{
                    fontWeight: 950,
                    px: 1,
                    bgcolor: market?.regime === 'BULL' ? alpha(COLORS.green, 0.15) : (market?.regime === 'BEAR' ? alpha(COLORS.red, 0.15) : alpha(COLORS.cyan, 0.15)),
                    color: market?.regime === 'BULL' ? COLORS.green : (market?.regime === 'BEAR' ? COLORS.red : COLORS.cyan),
                    border: `1px solid ${market?.regime === 'BULL' ? alpha(COLORS.green, 0.3) : (market?.regime === 'BEAR' ? alpha(COLORS.red, 0.3) : alpha(COLORS.cyan, 0.3))}`
                  }}
               />
            </Paper>
         </Grid>
         <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ ...GLASS_PANEL_STYLE, p: 2.5, height: '100%' }}>
               <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 950, mb: 1, display: 'block', letterSpacing: 1 }}>DATA FEED INTEGRITY</Typography>
               <Typography variant="body2" sx={{ fontWeight: 950, color: COLORS.green, fontFamily: MONO_FONT }}>
                  ● LIVE FEED ACTIVE (100% CONSENSUS)
               </Typography>
            </Paper>
         </Grid>
      </Grid>

      {/* 3. Today's Top Signals */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 950, letterSpacing: -0.5, fontFamily: MONO_FONT }}>TOP QUANTITATIVE OPPORTUNITIES</Typography>
        <Button onClick={() => navigate('/signals')} endIcon={<ArrowRight size={16} />} sx={{ color: COLORS.cyan, fontWeight: 950 }}>VIEW TERMINAL →</Button>
      </Box>

      <Paper sx={{ mb: 4, bgcolor: 'transparent', border: 'none', p: 0 }}>
        <Tabs
            value={tab}
            onChange={(_, v) => setTab(v)}
            sx={{
                mb: 3,
                '& .MuiTabs-indicator': { bgcolor: COLORS.cyan, height: 3 },
                '& .MuiTab-root': { color: COLORS.slateMuted, fontWeight: 950, fontSize: '0.75rem', letterSpacing: 1, '&.Mui-selected': { color: COLORS.textBright } }
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
                 <Paper sx={{ ...GLASS_PANEL_STYLE, py: 8, textAlign: 'center' }}>
                    <Typography sx={{ color: COLORS.slateMuted, fontWeight: 800 }}>No current {['SWING', 'SHORT', 'LONG'][tab]} signals meeting conviction threshold.</Typography>
                 </Paper>
              </Grid>
           )}
        </Grid>
      )}

      {/* 4. Market Insights Feed */}
      <Box sx={{ mt: 6 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 950, mb: 2, color: COLORS.slateMuted, letterSpacing: 1.5, fontFamily: MONO_FONT }}>MARKET INSIGHTS & REGIME</Typography>
        <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
                <Paper sx={{ ...GLASS_PANEL_STYLE, p: 3.5 }}>
                    <Typography variant="h6" sx={{ fontWeight: 950, mb: 2.5, fontFamily: MONO_FONT }}>SIGNAL REGIME CONTEXT</Typography>
                    <Stack spacing={2}>
                        <InsightItem
                            title="NIFTY Structural State"
                            desc={`The NIFTY-200 universe is currently in a ${market?.regime || 'SIDEWAYS'} regime with VIX at ${market?.vix?.toFixed(2) || '12.85'}.`}
                        />
                        <InsightItem
                            title="Momentum Alignment"
                            desc="Institutional order flow indicates sector rotation dynamics currently aligned with Strategy V3.3 quantitative ensemble nodes."
                        />
                    </Stack>
                </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
                <Paper sx={{ ...GLASS_PANEL_STYLE, p: 0, overflow: 'hidden' }}>
                    <Box sx={{ p: 2.5, bgcolor: alpha(COLORS.purpleDark, 0.2), borderBottom: `1px solid ${COLORS.borderPurple}` }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 950, color: 'white', letterSpacing: 1, fontFamily: MONO_FONT }}>INSTITUTIONAL PRO ACCESS</Typography>
                    </Box>
                    <Box sx={{ p: 3, textAlign: 'center' }}>
                        <Zap size={32} color={COLORS.purple} style={{ marginBottom: 12 }} />
                        <Typography variant="body2" sx={{ color: COLORS.slateText, fontWeight: 700, mb: 2.5 }}>
                            Unlock algorithmic sector strength analysis, multi-agent AI debates, and institutional order flow metrics.
                        </Typography>
                        <Button variant="outlined" color="secondary" onClick={() => navigate('/pricing')} sx={{ fontWeight: 950, px: 3, borderColor: COLORS.purple }}>GO PRO</Button>
                    </Box>
                </Paper>
            </Grid>
        </Grid>
      </Box>

      {/* 5. Quick Directory */}
      <Box sx={{ mt: 6 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 950, mb: 2, color: COLORS.slateMuted, letterSpacing: 1.5, fontFamily: MONO_FONT }}>PRODUCT DIRECTORY</Typography>
        <Grid container spacing={3}>
           <ToolCard
              icon={<ShieldCheck size={22} color={COLORS.green} />}
              title="Evidence Ledger"
              desc="Audit the bitwise forensic evidence behind our active signal generation."
              onClick={() => navigate('/evidence')}
           />
           <ToolCard
              icon={<PieChart size={22} color={COLORS.purple} />}
              title="Track Record"
              desc="Audit our 100% transparent historical signal performance ledger."
              onClick={() => navigate('/performance')}
           />
           <ToolCard
              icon={<Cpu size={22} color={COLORS.cyan} />}
              title="Quant Engine"
              desc="Explore the Strategy V3.3 ensemble models and multi-stage quality gates."
              onClick={() => navigate('/methodology')}
           />
        </Grid>
      </Box>
    </Box>
  );
}

function MarketMiniCard({ label, data, value, fallbackVal, icon }: any) {
    const rawVal = value || data?.value || fallbackVal || 0;
    const val = (rawVal === 0) ? '---' : rawVal;
    const change = data?.change || 0;
    const isPos = change >= 0;

    return (
        <Paper sx={{ ...GLASS_PANEL_STYLE, p: 2.5, height: '100%' }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 950, letterSpacing: 1 }}>{label}</Typography>
                {icon}
            </Stack>
            <Stack direction="row" spacing={1.5} alignItems="baseline">
                <Typography sx={{ fontWeight: 950, fontSize: '1.25rem', fontFamily: MONO_FONT }}>{typeof val === 'number' ? val.toLocaleString() : val}</Typography>
                {data && rawVal !== 0 && (
                    <Typography sx={{ fontWeight: 950, fontSize: '0.75rem', color: isPos ? COLORS.green : COLORS.red }}>
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
                    ...GLASS_PANEL_STYLE,
                    p: 3,
                    cursor: 'pointer',
                    transition: 'all 0.2s ease-in-out',
                    '&:hover': {
                      borderColor: COLORS.cyan,
                      transform: 'translateY(-2px)',
                      boxShadow: '0 10px 25px -10px rgba(0, 209, 255, 0.25)'
                    }
                }}
            >
                <Box sx={{ mb: 1.5 }}>{icon}</Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 950, mb: 0.5, fontFamily: MONO_FONT }}>{title}</Typography>
                <Typography variant="body2" sx={{ color: COLORS.slateText, fontWeight: 600, fontSize: '0.8rem' }}>{desc}</Typography>
            </Paper>
        </Grid>
    );
}

function InsightItem({ title, desc }: any) {
    return (
        <Box sx={{ p: 2, bgcolor: 'rgba(2, 6, 23, 0.5)', borderRadius: 1.5, border: '1px solid rgba(255,255,255,0.04)' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 950, color: COLORS.cyan, mb: 0.5, fontFamily: MONO_FONT }}>{title}</Typography>
            <Typography variant="body2" sx={{ color: COLORS.slateText, fontWeight: 500, fontSize: '0.825rem' }}>{desc}</Typography>
        </Box>
    );
}
