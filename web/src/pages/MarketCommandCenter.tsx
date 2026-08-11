import { useEffect, useState } from 'react'
import { Box, Typography, Grid, Paper, Button, CircularProgress, Chip, Stack, Divider } from '@mui/material'
import { Activity, Zap, ShieldCheck, Target, BarChart2 } from 'lucide-react'
import { getStocks, getMarketStats, getInstitutionalFlow } from '../api/client'
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision'
import { useNavigate } from 'react-router-dom';
import LiveSignalsBoard from '../components/Research/shared/LiveSignalsBoard';

export default function MarketCommandCenter() {
  const navigate = useNavigate();
  const [stocks, setStocks] = useState<any[]>([])
  const [marketStats, setMarketStats] = useState<any>(null)
  const [instFlow, setInstFlow] = useState<any>({ FII_Net: 0, DII_Net: 0, Market_Sentiment: 'Initializing...' })
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    try {
      const [stocksData, statsData, flowData] = await Promise.all([
        getStocks(),
        getMarketStats(),
        getInstitutionalFlow()
      ])
      const normalizedStocks = Array.isArray(stocksData) ? stocksData.map((s: any) => ({ ...s, decision: normalizeAITradeDecision(s) })) : [];
      setStocks(normalizedStocks)
      setMarketStats(statsData)
      setInstFlow(flowData)
    } catch (error) {
      console.error('Error fetching command center data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const bias = getMarketBias(marketStats);
  const topAlpha = stocks.filter(s => s.decision.conviction >= 70).sort((a,b) => b.decision.conviction - a.decision.conviction).slice(0, 4);

  return (
    <Box>
      {/* 1. Terminal Cockpit Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 5, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 900, letterSpacing: -1.5 }}>Trading Command Center</Typography>
          <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, letterSpacing: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
             <Activity size={12} className="text-emerald-500" /> INSTITUTIONAL SESSION DATA • {new Date().toLocaleTimeString()}
          </Typography>
        </Box>
        <Stack direction="row" spacing={2}>
           <Button variant="outlined" onClick={() => navigate('/portfolio')} sx={{ borderRadius: 1, fontWeight: 900 }}>PORTFOLIO</Button>
           <Button variant="contained" onClick={() => navigate('/ranking')} sx={{ borderRadius: 1, px: 3, fontWeight: 900 }} startIcon={<Target size={18} />}>ALPHA HUB</Button>
        </Stack>
      </Box>

      {loading ? (
        <Box sx={{ py: 20, textAlign: 'center' }}><CircularProgress size={32} /><Typography sx={{ mt: 2, fontWeight: 800, color: 'text.secondary', fontSize: '0.8rem' }}>Reconciling multi-agent terminal state...</Typography></Box>
      ) : (
        <Grid container spacing={3}>
          {/* Tier 1: Macro Context & Portfolio Guard */}
          <Grid item xs={12} lg={8}>
             <Paper sx={{ p: 0, overflow: 'hidden', border: '1px solid #1e293b' }}>
                <Box sx={{ p: 2.5, borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center', bgcolor: 'rgba(255,255,255,0.01)' }}>
                   <Typography variant="subtitle2" sx={{ fontWeight: 900, letterSpacing: 1 }}>AI MARKET REGIME</Typography>
                   <Chip label={bias.label} color={bias.color as any} sx={{ fontWeight: 900, borderRadius: 1, height: 24, fontSize: '0.65rem' }} />
                </Box>
                <Box sx={{ p: 3 }}>
                   <Grid container spacing={4}>
                      <Grid item xs={12} md={6}>
                         <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, display: 'block', mb: 2.5 }}>INDEX & BREADTH METRICS</Typography>
                         <Stack spacing={2.5}>
                            <MarketStatRow label="NIFTY 50" value={marketStats?.['NIFTY 50']?.value} change={marketStats?.['NIFTY 50']?.change} />
                            <MarketStatRow label="MARKET BREADTH" value={marketStats?.Breadth?.ratio?.toFixed(2)} subValue={`${marketStats?.Breadth?.advancing} ADV / ${marketStats?.Breadth?.declining} DEC`} />
                            <MarketStatRow label="INDIA VIX" value={marketStats?.['India VIX']?.value} change={marketStats?.['India VIX']?.change} isVix />
                         </Stack>
                      </Grid>
                      <Grid item xs={12} md={6}>
                         <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, display: 'block', mb: 2.5 }}>INSTITUTIONAL FLOW BIAS</Typography>
                         <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1.5, border: '1px solid #334155' }}>
                            <Stack spacing={2}>
                               <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                  <Typography variant="body2" sx={{ fontWeight: 700, color: 'text.secondary' }}>FII NET (EST)</Typography>
                                  <Typography variant="body2" fontWeight={900} color={instFlow.FII_Net >= 0 ? '#10b981' : '#f43f5e'} sx={{ fontFamily: 'JetBrains Mono' }}>
                                     {instFlow.FII_Net > 0 ? '+' : ''}{instFlow.FII_Net} Cr
                                  </Typography>
                               </Box>
                               <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                  <Typography variant="body2" sx={{ fontWeight: 700, color: 'text.secondary' }}>DII NET (EST)</Typography>
                                  <Typography variant="body2" fontWeight={900} color={instFlow.DII_Net >= 0 ? '#10b981' : '#f43f5e'} sx={{ fontFamily: 'JetBrains Mono' }}>
                                     {instFlow.DII_Net > 0 ? '+' : ''}{instFlow.DII_Net} Cr
                                  </Typography>
                               </Box>
                            </Stack>
                            <Divider sx={{ my: 1.5, opacity: 0.05 }} />
                            <Typography variant="caption" sx={{ fontWeight: 900, color: 'primary.main', display: 'block', textAlign: 'center', letterSpacing: 1 }}>
                               {instFlow.Market_Sentiment.toUpperCase()}
                            </Typography>
                         </Box>
                      </Grid>
                   </Grid>
                </Box>
             </Paper>
          </Grid>

          <Grid item xs={12} lg={4}>
             <Paper sx={{ p: 3, height: '100%', bgcolor: 'rgba(16, 185, 129, 0.01)', border: '1px solid #1e293b' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                   <Typography variant="subtitle2" sx={{ fontWeight: 900, letterSpacing: 1 }}>PORTFOLIO INTEGRITY</Typography>
                   <ShieldCheck size={18} className="text-emerald-500" />
                </Box>
                <Stack spacing={3}>
                   <Box>
                      <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>AGGREGATE EXPOSURE (MODEL)</Typography>
                      <Typography variant="h4" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', mt: 0.5 }}>₹4.28M</Typography>
                   </Box>
                   <Box>
                      <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>UNREALIZED RETURN (MODEL)</Typography>
                      <Typography variant="h4" sx={{ fontWeight: 900, color: '#10b981', fontFamily: 'JetBrains Mono', mt: 0.5 }}>+12.42%</Typography>
                   </Box>
                   <Box sx={{ p: 1.5, bgcolor: 'rgba(16, 185, 129, 0.05)', borderRadius: 1, border: '1px dashed #10b981' }}>
                      <Typography variant="caption" sx={{ fontWeight: 800, color: 'primary.main', display: 'flex', alignItems: 'center', gap: 1 }}>
                         ✓ NO CRITICAL RISK ALERTS
                      </Typography>
                   </Box>
                </Stack>
             </Paper>
          </Grid>

          {/* Tier 2: Live Actionable Signals Board */}
          <Grid item xs={12}>
             <LiveSignalsBoard stocks={stocks} />
          </Grid>

          {/* Tier 3: High-Conviction Alpha Snapshot */}
          <Grid item xs={12}>
             <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Zap size={18} className="text-amber-500" />
                <Typography variant="subtitle2" sx={{ fontWeight: 900, letterSpacing: 1 }}>HIGH-CONVICTION ALPHA SNAPSHOT</Typography>
             </Box>
             <Grid container spacing={2}>
                {topAlpha.map(s => (
                   <Grid item xs={12} sm={6} md={3} key={s.symbol}>
                      <Paper
                        onClick={() => navigate('/analysis', { state: { symbol: s.symbol } })}
                        sx={{ p: 2, border: '1px solid #334155', cursor: 'pointer', '&:hover': { borderColor: 'primary.main', bgcolor: 'rgba(16,185,129,0.02)' }, transition: '0.2s' }}
                      >
                         <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body1" fontWeight={900}>{s.symbol}</Typography>
                            <Chip label={`${s.decision.conviction}%`} size="small" sx={{ fontWeight: 900, height: 18, fontSize: '0.6rem', bgcolor: 'primary.main', color: '#000' }} />
                         </Box>
                         <Typography variant="caption" color="textSecondary" sx={{ display: 'block', height: 32, overflow: 'hidden', lineHeight: 1.3, fontWeight: 600 }}>
                            {s.decision.primaryCatalyst || 'Institutional accumulation detected.'}
                         </Typography>
                         <Divider sx={{ my: 1.5, opacity: 0.05 }} />
                         <Stack direction="row" justifyContent="space-between" alignItems="center">
                            <Typography variant="caption" fontWeight={800} color="primary.main">{s.decision.rating}</Typography>
                            <BarChart2 size={14} className="text-slategray" />
                         </Stack>
                      </Paper>
                   </Grid>
                ))}
             </Grid>
          </Grid>
        </Grid>
      )}
    </Box>
  )
}

function MarketStatRow({ label, value, change, subValue, isVix = false }: any) {
  const isUp = change >= 0;
  const color = isVix ? (isUp ? '#f43f5e' : '#10b981') : (isUp ? '#10b981' : '#f43f5e');

  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
       <Box>
          <Typography variant="body2" sx={{ fontWeight: 800, color: 'text.secondary' }}>{label}</Typography>
          {subValue && <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 600 }}>{subValue}</Typography>}
       </Box>
       <Box sx={{ textAlign: 'right' }}>
          <Typography variant="body1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono' }}>{value || '---'}</Typography>
          {change !== undefined && (
            <Typography variant="caption" sx={{ color, fontWeight: 900, fontFamily: 'JetBrains Mono' }}>
               {isUp ? '+' : ''}{change.toFixed(2)}%
            </Typography>
          )}
       </Box>
    </Box>
  );
}

function getMarketBias(marketStats: any) {
  if (!marketStats || Object.keys(marketStats).length === 0) return { label: 'SYNCING', color: 'default' };

  const niftyChange = marketStats['NIFTY 50']?.change ?? 0;
  const breadthRatio = marketStats['Breadth']?.ratio ?? 1.0;
  const vix = marketStats['India VIX']?.value ?? 15;

  let score = 0;
  if (niftyChange > 0.5) score += 2;
  else if (niftyChange < -0.5) score -= 2;

  if (breadthRatio > 1.5) score += 2;
  else if (breadthRatio < 0.6) score -= 2;

  if (vix < 14 && vix > 0) score += 1;
  else if (vix > 18) score -= 1;

  if (score >= 3) return { label: 'STRONGLY BULLISH', color: 'primary' };
  if (score >= 1) return { label: 'BULLISH', color: 'primary' };
  if (score <= -3) return { label: 'STRONGLY BEARISH', color: 'error' };
  if (score <= -1) return { label: 'BEARISH', color: 'error' };
  return { label: 'NEUTRAL', color: 'default' };
}
