import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Paper, Grid, Stack, Tab, Tabs, Button, Chip, CircularProgress, Divider, List } from '@mui/material';
import { Zap, Clock, TrendingUp, ShieldAlert, ArrowRight, RefreshCw, Star } from 'lucide-react';
import { getStocks, getOpportunities } from '../api/client';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';
import { useNavigate } from 'react-router-dom';

export default function SignalsDashboard() {
  const [activeTab, setActiveTab] = useState(2); // Default to SWING (index 2)
  const [stocks, setStocks] = useState<any[]>([]);
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const timeframes = [
    { label: 'INTRADAY', value: 'INTRADAY' },
    { label: 'SHORT TERM', value: 'SHORT TERM' },
    { label: 'SWING', value: 'SWING' },
    { label: 'LONG TERM', value: 'LONG TERM' }
  ];

  const fetchData = async () => {
    setLoading(true);
    try {
      const [stocksData, oppsData] = await Promise.all([
        getStocks(),
        getOpportunities()
      ]);
      const normalized = stocksData.map((s: any) => ({
        ...s,
        decision: normalizeAITradeDecision(s)
      }));
      setStocks(normalized);
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
    // Prioritize active opportunities that match timeframe
    const setups = opportunities.filter(o => {
        const stock = stocks.find(s => s.symbol === o.symbol);
        return stock?.decision?.timeframe === currentTf || (o.type === 'MOMENTUM' && currentTf === 'INTRADAY');
    }).map(o => {
        const stock = stocks.find(s => s.symbol === o.symbol);
        return { ...stock, ...o, isOpportunity: true };
    });

    // Also include other validated signals for this timeframe
    const others = stocks.filter(s =>
        s.decision.timeframe === currentTf &&
        !setups.find(set => set.symbol === s.symbol) &&
        (s.decision.rating.includes('BUY') || s.decision.rating.includes('SELL'))
    );

    return [...setups, ...others].sort((a,b) => (b.decision?.conviction || 0) - (a.decision?.conviction || 0));
  }, [stocks, opportunities, activeTab]);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 5 }}>
         <Box>
            <Typography variant="h4" sx={{ fontWeight: 900, letterSpacing: -1 }}>Signal Intelligence</Typography>
            <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, letterSpacing: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
               <Zap size={14} className="text-emerald-500" /> MULTI-AGENT ALPHA GENERATION ACTIVE
            </Typography>
         </Box>
         <Stack direction="row" spacing={2}>
            <Button
               variant="outlined"
               startIcon={<RefreshCw size={16} className={loading ? 'animate-spin' : ''} />}
               onClick={fetchData}
               sx={{ fontWeight: 900, borderRadius: 1 }}
            >
               RESYNC TERMINAL
            </Button>
            <Chip label="PROBABILISTIC MODELS LIVE" color="primary" variant="filled" sx={{ fontWeight: 900, height: 32 }} />
         </Stack>
      </Box>

      <Paper sx={{ mb: 4, bgcolor: 'transparent', border: 'none' }}>
         <Tabs
            value={activeTab}
            onChange={(_, v) => setActiveTab(v)}
            indicatorColor="primary"
            sx={{ borderBottom: '1px solid #1e293b' }}
         >
            {timeframes.map((tf) => (
               <Tab
                  key={tf.label}
                  label={tf.label}
                  icon={<Clock size={16} />}
                  iconPosition="start"
                  sx={{ fontWeight: 800, minHeight: 60, minWidth: 160 }}
               />
            ))}
         </Tabs>
      </Paper>

      {loading ? (
         <Box sx={{ py: 20, textAlign: 'center' }}>
            <CircularProgress size={40} />
            <Typography sx={{ mt: 3, color: 'slategray', fontWeight: 700 }}>Synthesizing session setups...</Typography>
         </Box>
      ) : (
         <Grid container spacing={3}>
            {filteredSignals.length > 0 ? filteredSignals.map((s) => (
               <Grid item xs={12} md={6} lg={4} key={s.symbol}>
                  <SignalCard stock={s} />
               </Grid>
            )) : (
               <Grid item xs={12}>
                  <Box sx={{ py: 10, textAlign: 'center', opacity: 0.5 }}>
                     <ShieldAlert size={48} style={{ margin: '0 auto 16px' }} />
                     <Typography variant="h6">No validated {timeframes[activeTab].label} setups detected</Typography>
                     <Typography variant="body2">Monitoring order flow for next institutional displacement.</Typography>
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
  const isBuy = decision.rating.includes('BUY');

  return (
    <Paper
      sx={{
         p: 3,
         height: '100%',
         border: '1px solid #1e293b',
         transition: '0.2s',
         cursor: 'pointer',
         '&:hover': { borderColor: isBuy ? 'primary.main' : 'error.main', bgcolor: 'rgba(255,255,255,0.01)' }
      }}
      onClick={() => navigate('/analysis', { state: { symbol: stock.symbol } })}
    >
       <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
             <Typography variant="h5" sx={{ fontWeight: 900 }}>{stock.symbol}</Typography>
             <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>{stock.name || 'Equity Asset'}</Typography>
          </Box>
          <Stack direction="row" spacing={1}>
             {stock.isOpportunity && <Chip icon={<Star size={12} />} label="HIGH CONVICTION" size="small" color="primary" sx={{ height: 20, fontSize: '0.6rem', fontWeight: 900 }} />}
             <Chip
               label={decision.rating}
               color={isBuy ? 'primary' : decision.rating.includes('SELL') ? 'error' : 'default'}
               size="small"
               sx={{ fontWeight: 900, height: 20, fontSize: '0.6rem' }}
             />
          </Stack>
       </Box>

       <Box sx={{ mb: 3 }}>
          <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
             <Typography variant="caption" color="textSecondary" fontWeight={800}>AI CONVICTION</Typography>
             <Typography variant="caption" color="primary" fontWeight={900}>{decision.conviction}%</Typography>
          </Stack>
          <Box sx={{ height: 4, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 2, overflow: 'hidden' }}>
             <Box sx={{ width: `${decision.conviction}%`, height: '100%', bgcolor: isBuy ? 'primary.main' : 'error.main' }} />
          </Box>
       </Box>

       <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6}>
             <Typography variant="caption" color="textSecondary" display="block">ENTRY ZONE</Typography>
             <Typography variant="body1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono' }}>
                ₹{Math.round(decision.entry).toLocaleString()}
             </Typography>
          </Grid>
          <Grid item xs={6} sx={{ textAlign: 'right' }}>
             <Typography variant="caption" color="textSecondary" display="block">TARGET</Typography>
             <Typography variant="body1" sx={{ fontWeight: 900, color: 'primary.main', fontFamily: 'JetBrains Mono' }}>
                ₹{Math.round(decision.target).toLocaleString()}
             </Typography>
             {decision.targetRange && (
                <Typography variant="caption" sx={{ display: 'block', fontSize: '0.6rem', opacity: 0.7 }}>
                   [{decision.targetRange[0]}-{decision.targetRange[1]}]
                </Typography>
             )}
          </Grid>
          <Grid item xs={6}>
             <Typography variant="caption" color="textSecondary" display="block">STOP LOSS</Typography>
             <Typography variant="body1" sx={{ fontWeight: 900, color: 'error.main', fontFamily: 'JetBrains Mono' }}>
                ₹{Math.round(decision.stopLoss).toLocaleString()}
             </Typography>
             {decision.stopRange && (
                <Typography variant="caption" sx={{ display: 'block', fontSize: '0.6rem', opacity: 0.7 }}>
                   [{decision.stopRange[0]}-{decision.stopRange[1]}]
                </Typography>
             )}
          </Grid>
          <Grid item xs={6} sx={{ textAlign: 'right' }}>
             <Typography variant="caption" color="textSecondary" display="block">R:R RATIO</Typography>
             <Typography variant="body1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono' }}>{decision.riskReward}</Typography>
          </Grid>
       </Grid>

       <Divider sx={{ mb: 2.5, opacity: 0.05 }} />

       <Box sx={{ mb: 2.5 }}>
          <Typography variant="caption" color="primary" sx={{ fontWeight: 900, display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
             <TrendingUp size={12} /> WHY THIS SETUP
          </Typography>
          <List dense sx={{ p: 0 }}>
             {decision.drivers?.slice(0, 3).map((d: string, i: number) => (
                <Typography key={i} variant="caption" display="block" sx={{ color: 'text.secondary', fontWeight: 500, lineHeight: 1.4, mb: 0.5 }}>
                   • {d}
                </Typography>
             ))}
          </List>
       </Box>

       <Box sx={{ mb: 2.5 }}>
          <Typography variant="caption" color="error" sx={{ fontWeight: 900, display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
             <ShieldAlert size={12} /> RISK ASSESSMENT
          </Typography>
          <Typography variant="caption" display="block" sx={{ color: 'text.secondary', fontWeight: 500, fontStyle: 'italic', mb: 1 }}>
             {decision.keyRisks?.[0] || 'Volatility spike on session open.'}
          </Typography>
          {decision.invalidation && (
             <Box sx={{ p: 1, bgcolor: 'rgba(244, 63, 94, 0.05)', borderRadius: 1, border: '1px dashed rgba(244, 63, 94, 0.2)' }}>
                <Typography variant="caption" sx={{ fontWeight: 800, color: 'error.main', fontSize: '0.55rem' }}>
                   INVALIDATION: {decision.invalidation}
                </Typography>
             </Box>
          )}
       </Box>

       <Button
         fullWidth
         variant="contained"
         endIcon={<ArrowRight size={16} />}
         sx={{ bgcolor: 'rgba(255,255,255,0.03)', color: 'white', fontWeight: 900, '&:hover': { bgcolor: 'primary.main', color: 'black' } }}
       >
          FORENSIC LAB
       </Button>
    </Paper>
  );
}
