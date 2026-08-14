import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Paper, Grid, Stack, Tab, Tabs, Button, Chip, CircularProgress, Divider, InputBase, alpha, IconButton } from '@mui/material';
import { Zap, Clock, ShieldAlert, ArrowRight, RefreshCw, Star, Radio, Search, Activity } from 'lucide-react';
import { getStocks, getOpportunities, getLiveSignalsAudit } from '../api/client';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';
import { useNavigate } from 'react-router-dom';
import { useTurboSync } from '../hooks/useTurboSync';

export default function SignalsDashboard() {
  const [activeTab, setActiveTab] = useState(2); // Default to SWING (index 2)
  const [stocks, setStocks] = useState<any[]>([]);
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const { connectionStatus } = useTurboSync();

  const timeframes = [
    { label: 'INTRADAY', value: 'INTRADAY' },
    { label: 'SHORT TERM', value: 'SHORT TERM' },
    { label: 'SWING', value: 'SWING' },
    { label: 'LONG TERM', value: 'LONG TERM' }
  ];

  const fetchData = async () => {
    setLoading(true);
    try {
      const [stocksData, oppsData, liveSignalsData] = await Promise.all([
        getStocks(),
        getOpportunities(),
        getLiveSignalsAudit()
      ]);

      // 1. Map stock metadata for easy lookup
      const stockMap = new Map(stocksData.map((s: any) => [s.symbol, s]));

      // 2. Normalize Live Signals from SQL Tier (Audit Table)
      const normalizedLive = liveSignalsData.map((ls: any) => {
        const stockInfo = stockMap.get(ls.symbol) || {};
        return {
          ...stockInfo,
          ...ls,
          id: ls.id, // Ensure signal ID is used
          decision: normalizeAITradeDecision({...stockInfo, ...ls})
        };
      });

      // 3. Normalize Stocks from Alpha Tier (Main Table)
      const normalizedStocks = stocksData.map((s: any) => ({
        ...s,
        decision: normalizeAITradeDecision(s)
      }));

      // 4. MERGE STRATEGY: Prioritize live signals, but include all alpha signals
      const allSymbols = new Set([...normalizedLive.map((s: any) => s.symbol), ...normalizedStocks.map((s: any) => s.symbol)]);
      const combined = Array.from(allSymbols).map(symbol => {
          // If a live signal exists, it's likely more recent/specific
          const live = normalizedLive.find((l: any) => l.symbol === symbol);
          if (live) return live;
          return normalizedStocks.find((s: any) => s.symbol === symbol);
      });

      setStocks(combined);
      setOpportunities(oppsData);
    } catch (e) {
      console.error("Failed to sync signals:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredSignals = useMemo(() => {
    const currentTf = timeframes[activeTab].value;

    // 1. Combine and Filter by Timeframe & Search
    const setups = opportunities.filter(o => {
        const stock = stocks.find(s => s.symbol === o.symbol);
        if (!stock?.decision) return false;
        const matchesTf = stock.decision.timeframe === currentTf || (o.type === 'MOMENTUM' && currentTf === 'INTRADAY');
        const matchesSearch = o.symbol.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesTf && matchesSearch;
    }).map(o => {
        const stock = stocks.find(s => s.symbol === o.symbol);
        return { ...stock, ...o, isOpportunity: true };
    });

    const others = stocks.filter(s => {
        const matchesTf = s.decision?.timeframe === currentTf;
        const isTradeable = (s.decision?.rating?.includes('BUY') || s.decision?.rating?.includes('SELL'));
        const notInSetups = !setups.find(set => set.symbol === s.symbol);
        const matchesSearch = s.symbol.toLowerCase().includes(searchQuery.toLowerCase());
        const isNotResolved = !['TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'COMPLETED'].includes(s.decision?.status);
        return matchesTf && isTradeable && notInSetups && matchesSearch && isNotResolved;
    });

    return [...setups, ...others].sort((a,b) => (b.decision?.conviction || 0) - (a.decision?.conviction || 0));
  }, [stocks, opportunities, activeTab, searchQuery]);

  return (
    <Box sx={{ pb: 10 }}>
      {/* 🟢 Advanced Header Tier */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4, flexWrap: 'wrap', gap: 3 }}>
         <Box>
            <Typography variant="h3" sx={{ fontWeight: 900, letterSpacing: -1.5, background: 'linear-gradient(45deg, #fff 30%, #94a3b8 90%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
               Signal Intelligence
            </Typography>
            <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
               <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, letterSpacing: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Zap size={14} className="text-emerald-400" /> MULTI-AGENT ALPHA ENGINE
               </Typography>
               <Divider orientation="vertical" flexItem sx={{ height: 12, my: 'auto', bgcolor: 'rgba(255,255,255,0.1)' }} />
               <Typography variant="caption" color="primary" sx={{ fontWeight: 900, letterSpacing: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Activity size={14} /> {filteredSignals.length} ACTIVE SETUPS
               </Typography>
            </Stack>
         </Box>

         <Stack direction="row" spacing={1.5} alignItems="center">
            {/* 🔍 Forensic Search Bar */}
            <Box sx={{
               display: 'flex',
               alignItems: 'center',
               bgcolor: 'rgba(255,255,255,0.03)',
               border: '1px solid #1e293b',
               borderRadius: 1.5,
               px: 1.5,
               width: { xs: '100%', sm: 260 },
               transition: '0.2s',
               '&:focus-within': { borderColor: 'primary.main', bgcolor: 'rgba(255,255,255,0.05)' }
            }}>
               <Search size={16} color="#64748b" />
               <InputBase
                  placeholder="FORENSIC SEARCH..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  sx={{ ml: 1, flex: 1, fontSize: '0.75rem', fontWeight: 800, color: 'white' }}
               />
            </Box>

            <Chip
               icon={<Radio size={14} className={connectionStatus === 'ONLINE' ? 'text-emerald-500' : 'text-rose-500'} />}
               label={connectionStatus}
               variant="outlined"
               sx={{ fontWeight: 900, height: 36, fontSize: '0.65rem', border: '1px solid #1e293b' }}
            />

            <IconButton
               onClick={fetchData}
               sx={{ border: '1px solid #1e293b', borderRadius: 1.5, p: 1, '&:hover': { bgcolor: 'rgba(255,255,255,0.05)' } }}
            >
               <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
            </IconButton>
         </Stack>
      </Box>

      {/* 📊 Institutional Tabs Layer */}
      <Box sx={{ position: 'sticky', top: 64, zIndex: 10, bgcolor: alpha('#020617', 0.8), backdropFilter: 'blur(12px)', mx: -3, px: 3, mb: 4, borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
         <Tabs
            value={activeTab}
            onChange={(_, v) => setActiveTab(v)}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
               minHeight: 54,
               '& .MuiTabs-indicator': { height: 3, borderRadius: '3px 3px 0 0' },
               '& .MuiTab-root': { color: 'slategray', fontWeight: 800, fontSize: '0.75rem', minWidth: 140, transition: '0.2s', '&.Mui-selected': { color: 'white' } }
            }}
         >
            {timeframes.map((tf) => (
               <Tab
                  key={tf.label}
                  label={tf.label}
                  icon={<Clock size={14} />}
                  iconPosition="start"
                  sx={{ letterSpacing: 1.2 }}
               />
            ))}
         </Tabs>
      </Box>

      {loading ? (
         <Box sx={{ py: 20, textAlign: 'center' }}>
            <Box sx={{ position: 'relative', display: 'inline-flex', mb: 3 }}>
               <CircularProgress size={60} thickness={2} sx={{ color: 'primary.main' }} />
               <Box sx={{ position: 'absolute', top: 0, left: 0, bottom: 0, right: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Zap size={20} className="text-emerald-500 animate-pulse" />
               </Box>
            </Box>
            <Typography sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1 }}>SYNTHESIZING QUANTITATIVE OVERVIEW...</Typography>
         </Box>
      ) : (
         <Grid container spacing={3}>
            {filteredSignals.length > 0 ? filteredSignals.map((s) => (
               <Grid item xs={12} md={6} lg={4} key={s.symbol}>
                  <SignalCard stock={s} />
               </Grid>
            )) : (
               <Grid item xs={12}>
                  <Box sx={{ py: 15, textAlign: 'center', bgcolor: 'rgba(255,255,255,0.01)', border: '1px dashed #1e293b', borderRadius: 4 }}>
                     <ShieldAlert size={48} color="#64748b" style={{ margin: '0 auto 20px' }} />
                     <Typography variant="h6" fontWeight={800} color="textSecondary">No Validated {timeframes[activeTab].label} Setups</Typography>
                     <Typography variant="body2" color="textSecondary" sx={{ mt: 1, opacity: 0.6 }}>The multi-agent consensus has not reached an 80% threshold for this timeframe.</Typography>
                     <Button variant="outlined" sx={{ mt: 4, borderRadius: 2 }} onClick={() => setSearchQuery('')}>CLEAR FILTERS</Button>
                  </Box>
               </Grid>
            )}
         </Grid>
      )}
    </Box>
  );
}

function SignalCard({ stock }: { stock: any }) {
  const navigate = useNavigate();
  const decision = stock.decision;

  if (!decision) return null;

  const isBuy = decision.rating?.includes('BUY');
  const isHighConviction = decision.conviction > 80;

  return (
    <Paper
      elevation={0}
      sx={{
         p: 0,
         height: '100%',
         border: '1px solid #1e293b',
         borderRadius: 3,
         overflow: 'hidden',
         transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
         cursor: 'pointer',
         bgcolor: 'rgba(15, 23, 42, 0.4)',
         position: 'relative',
         '&:hover': {
            borderColor: isBuy ? alpha('#10b981', 0.5) : alpha('#f43f5e', 0.5),
            bgcolor: 'rgba(15, 23, 42, 0.6)',
            transform: 'translateY(-4px)',
            boxShadow: `0 12px 24px -10px ${isBuy ? 'rgba(16, 185, 129, 0.2)' : 'rgba(244, 63, 94, 0.2)'}`
         },
         ...(isHighConviction && {
            '&::before': {
               content: '""',
               position: 'absolute',
               top: 0, left: 0, right: 0, height: 2,
               background: 'linear-gradient(90deg, #10b981, #3b82f6)'
            }
         })
      }}
      onClick={() => navigate('/analysis', { state: { symbol: stock.symbol } })}
    >
       {/* 💎 Card Header */}
       <Box sx={{ p: 3, pb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
             <Box>
                <Typography variant="h5" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', display: 'flex', alignItems: 'center', gap: 1 }}>
                   {stock.symbol}
                   {isHighConviction && <Star size={16} className="text-yellow-400" fill="currentColor" />}
                </Typography>
                <Typography variant="caption" sx={{ fontWeight: 700, color: 'text.secondary', textTransform: 'uppercase' }}>
                   {stock.industry || 'Asset Class'}
                </Typography>
             </Box>
             <Stack direction="column" spacing={0.5} alignItems="flex-end">
                <Chip
                  label={decision.rating}
                  size="small"
                  sx={{
                     fontWeight: 900,
                     fontSize: '0.65rem',
                     bgcolor: isBuy ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
                     color: isBuy ? '#10b981' : '#f43f5e',
                     border: `1px solid ${isBuy ? alpha('#10b981', 0.2) : alpha('#f43f5e', 0.2)}`
                  }}
                />
                <Typography variant="caption" sx={{ fontWeight: 900, fontSize: '0.6rem', opacity: 0.5 }}>
                   {decision.timeframe}
                </Typography>
             </Stack>
          </Box>
       </Box>

       {/* 📊 Conviction Meter */}
       <Box sx={{ px: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
             <Typography variant="caption" sx={{ fontWeight: 800, color: 'text.secondary' }}>AI CONVICTION</Typography>
             <Typography variant="caption" sx={{ fontWeight: 900, color: isBuy ? '#10b981' : '#f43f5e' }}>{decision.conviction}%</Typography>
          </Box>
          <Box sx={{ height: 6, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 3, overflow: 'hidden' }}>
             <Box
               sx={{
                  width: `${decision.conviction}%`,
                  height: '100%',
                  background: isBuy ? 'linear-gradient(90deg, #059669, #10b981)' : 'linear-gradient(90deg, #e11d48, #f43f5e)',
                  borderRadius: 3
               }}
             />
          </Box>
       </Box>

       {/* 🔢 Core Quant Tiers */}
       <Box sx={{ px: 3, py: 2, bgcolor: 'rgba(0,0,0,0.2)' }}>
          <Grid container spacing={2}>
             <Grid item xs={6}>
                <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.6rem' }}>ENTRY ZONE</Typography>
                <Typography variant="body1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: 'white' }}>
                   ₹{Math.round(decision.entry).toLocaleString()}
                </Typography>
             </Grid>
             <Grid item xs={6} sx={{ textAlign: 'right' }}>
                <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.6rem' }}>TARGET</Typography>
                <Typography variant="body1" sx={{ fontWeight: 900, color: '#10b981', fontFamily: 'JetBrains Mono' }}>
                   ₹{Math.round(decision.target).toLocaleString()}
                </Typography>
             </Grid>
             <Grid item xs={6}>
                <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.6rem' }}>STOP LOSS</Typography>
                <Typography variant="body1" sx={{ fontWeight: 900, color: '#f43f5e', fontFamily: 'JetBrains Mono' }}>
                   ₹{Math.round(decision.stopLoss).toLocaleString()}
                </Typography>
             </Grid>
             <Grid item xs={6} sx={{ textAlign: 'right' }}>
                <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.6rem' }}>R:R RATIO</Typography>
                <Typography variant="body1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: '#3b82f6' }}>{decision.riskReward}</Typography>
             </Grid>
          </Grid>
       </Box>

       {/* 🧠 Intelligence Digest */}
       <Box sx={{ p: 3 }}>
          <Typography variant="caption" sx={{ fontWeight: 900, color: 'primary.main', display: 'flex', alignItems: 'center', gap: 0.5, mb: 1, letterSpacing: 1 }}>
             <Zap size={12} /> INSIGHT DIGEST
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 500, fontSize: '0.75rem', lineHeight: 1.5, minHeight: 44 }}>
             {decision.thesis?.length > 120 ? decision.thesis.substring(0, 117) + '...' : decision.thesis}
          </Typography>

          <Stack direction="row" spacing={1} sx={{ mt: 2, flexWrap: 'wrap', gap: 1 }}>
             {decision.drivers?.slice(0, 2).map((d: string, i: number) => (
                <Chip
                  key={i}
                  label={d.toUpperCase()}
                  size="small"
                  sx={{ height: 18, fontSize: '0.55rem', fontWeight: 800, bgcolor: 'rgba(255,255,255,0.03)', color: 'slategray', border: '1px solid rgba(255,255,255,0.05)' }}
                />
             ))}
          </Stack>

          <Button
            fullWidth
            variant="text"
            endIcon={<ArrowRight size={14} />}
            sx={{
               mt: 3,
               py: 1,
               justifyContent: 'space-between',
               color: 'text.secondary',
               fontWeight: 800,
               fontSize: '0.7rem',
               border: '1px solid rgba(255,255,255,0.05)',
               borderRadius: 2,
               '&:hover': { color: 'primary.main', borderColor: 'primary.main', bgcolor: alpha('#10b981', 0.05) }
            }}
          >
             OPEN FORENSIC LAB
          </Button>
       </Box>
    </Paper>
  );
}
