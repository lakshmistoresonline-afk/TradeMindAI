import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Grid, Paper, Stack, alpha, Skeleton, Tabs, Tab, Button, Chip } from '@mui/material';
import { ShieldCheck, ArrowRight, PieChart, Activity, Cpu, Database } from 'lucide-react';
import { getEquitySignals } from '../api/client';
import { mapCanonicalSignal } from '../hooks/useAITradeDecision';
import { useTurboSync } from '../hooks/useTurboSync';
import { useBackendHealth } from '../hooks/useBackendHealth';
import SignalCard from '../components/Research/shared/SignalCard';
import { useNavigate } from 'react-router-dom';
import { MONO_FONT, COLORS, HERO_BANNER_STYLE, GRADIENT_ACCENT_BAR, GLASS_PANEL_STYLE } from '../theme/institutionalTheme';

export default function UserDashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [signals, setSignals] = useState<any[]>([]);
  const [tab, setTab] = useState(0);

  const { isOnline } = useBackendHealth();
  const { firestoreSignals, marketContext } = useTurboSync();

  const fetchData = async () => {
    setLoading(true);

    const signalsPromise = getEquitySignals({ limit: 12 });

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
        // market context updated if needed
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
    <Box sx={{ pb: { xs: 14, md: 8 }, px: { xs: 1, sm: 2, md: 0 }, color: 'white', maxWidth: 1400, mx: 'auto', boxSizing: 'border-box' }}>
      {/* 1. Executive Hero Header Banner */}
      <Box sx={{ ...HERO_BANNER_STYLE, mb: 5 }}>
        <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, ...GRADIENT_ACCENT_BAR }} />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <Box sx={{ width: { xs: '100%', sm: 'auto' } }}>
            <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" gap={1} sx={{ mb: 1 }}>
              <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1, color: COLORS.textBright, fontFamily: MONO_FONT, fontSize: { xs: '1.5rem', sm: '2rem' } }}>
                EXECUTIVE TERMINAL
              </Typography>
              <Chip label="BUY-ONLY SIGNALS" size="small" sx={{ bgcolor: alpha(COLORS.cyan, 0.15), color: COLORS.cyan, border: `1px solid ${COLORS.borderCyan}`, fontWeight: 950, fontSize: '0.625rem' }} />
              <Chip label="STRATEGY V3.3" size="small" sx={{ bgcolor: alpha(COLORS.purple, 0.15), color: COLORS.purple, border: `1px solid ${COLORS.borderPurple}`, fontWeight: 950, fontSize: '0.625rem' }} />
            </Stack>
            <Typography variant="body2" sx={{ color: COLORS.slateText, fontWeight: 600, fontSize: { xs: '0.8rem', sm: '0.875rem' } }}>
              Authoritative institutional signal provider terminal. BUY-only multi-horizon setups with zero live execution.
            </Typography>
          </Box>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Button
              variant="outlined"
              size="small"
              startIcon={<Database size={16} />}
              onClick={() => navigate('/universes')}
              sx={{ fontWeight: 950, borderColor: COLORS.borderCyan, color: COLORS.cyan, bgcolor: alpha(COLORS.cyan, 0.05) }}
            >
              Stock Universes
            </Button>
            <Chip
              icon={<Activity size={14} color={isOnline ? COLORS.green : COLORS.amber} />}
              label={isOnline ? '🟢 LOCAL SERVER CONNECTED' : '🟡 OFFLINE CLIENT MODE'}
              size="medium"
              sx={{
                fontWeight: 950,
                fontSize: '0.675rem',
                px: 1,
                height: 32,
                bgcolor: isOnline ? alpha(COLORS.green, 0.12) : alpha(COLORS.amber, 0.12),
                color: isOnline ? COLORS.green : COLORS.amber,
                border: `1px solid ${isOnline ? alpha(COLORS.green, 0.3) : alpha(COLORS.amber, 0.3)}`
              }}
            />
          </Stack>
        </Box>
      </Box>

      {/* 2. Today's Top Signals */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 950, letterSpacing: -0.5, fontFamily: MONO_FONT, fontSize: { xs: '1rem', sm: '1.25rem' } }}>TOP QUANTITATIVE OPPORTUNITIES</Typography>
        <Button onClick={() => navigate('/signals')} endIcon={<ArrowRight size={16} />} sx={{ color: COLORS.cyan, fontWeight: 950, fontSize: '0.75rem' }}>VIEW TERMINAL →</Button>
      </Box>

      <Paper sx={{ mb: 4, bgcolor: 'transparent', border: 'none', p: 0 }}>
        <Tabs
            value={tab}
            onChange={(_, v) => setTab(v)}
            sx={{
                mb: 3,
                '& .MuiTabs-indicator': { bgcolor: COLORS.cyan, height: 3 },
                '& .MuiTab-root': { color: COLORS.slateMuted, fontWeight: 950, fontSize: '0.725rem', letterSpacing: 1, '&.Mui-selected': { color: COLORS.textBright } }
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
      ) : filteredSignals.length === 0 ? (
        <Paper sx={{ p: 6, textAlign: 'center', bgcolor: 'rgba(15,23,42,0.6)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 950, color: COLORS.textBright, mb: 1 }}>No Active BUY Signals for this Horizon</Typography>
          <Typography variant="body2" sx={{ color: COLORS.slateMuted, mb: 3 }}>All signals adhere to strict Strategy V3.3 buy-only and trend quality gates.</Typography>
          <Button variant="outlined" onClick={() => navigate('/signals')} sx={{ color: COLORS.cyan, borderColor: COLORS.borderCyan, fontWeight: 950 }}>Browse All Signals</Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {filteredSignals.map(sig => (
            <Grid item xs={12} md={4} key={sig.id}>
              <SignalCard stock={sig} decision={sig.decision} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* 3. Terminal Navigation Tools */}
      <Box sx={{ mt: 8 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 950, mb: 2, color: COLORS.slateMuted, letterSpacing: 1.5, fontFamily: MONO_FONT }}>
          INSTITUTIONAL QUANT TOOLS
        </Typography>
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

function ToolCard({ icon, title, desc, onClick }: any) {
  return (
    <Grid item xs={12} md={4}>
       <Paper
         onClick={onClick}
         sx={{
            ...GLASS_PANEL_STYLE,
            p: 3,
            height: '100%',
            cursor: 'pointer',
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
               borderColor: alpha(COLORS.cyan, 0.4),
               transform: 'translateY(-2px)',
               bgcolor: alpha(COLORS.cyan, 0.02)
            }
         }}
       >
          <Stack direction="row" spacing={2} alignItems="flex-start">
             <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: alpha(COLORS.cyan, 0.08), border: `1px solid ${alpha(COLORS.cyan, 0.15)}` }}>
                {icon}
             </Box>
             <Box sx={{ flexGrow: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 950, color: COLORS.textBright, mb: 0.5 }}>{title}</Typography>
                <Typography variant="body2" sx={{ color: COLORS.slateMuted, fontWeight: 600, lineHeight: 1.5 }}>{desc}</Typography>
             </Box>
          </Stack>
       </Paper>
    </Grid>
  );
}
