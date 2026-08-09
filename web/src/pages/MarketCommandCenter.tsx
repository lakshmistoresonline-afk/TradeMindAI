import { useEffect, useState } from 'react'
import { Box, Typography, Grid, Paper, Button, CircularProgress, Chip, Stack, Tabs, Tab, Tooltip } from '@mui/material'
import { MessageSquare, Play, Target, ShieldCheck, Zap, LineChart, AlertCircle, ChevronRight } from 'lucide-react'
import { getStocks, triggerBatchAnalysis, getMarketStats, getInstitutionalFlow } from '../api/client'
import MarketOutlook from '../components/Research/shared/MarketOutlook'
import TopOpportunities from '../components/Research/shared/TopOpportunities'
import QuickResearchDrawer from '../components/Research/QuickResearchDrawer'
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision'
import { useNavigate } from 'react-router-dom';

export default function MarketCommandCenter() {
  const navigate = useNavigate();
  const [stocks, setStocks] = useState<any[]>([])
  const [selectedTimeframe, setSelectedTimeframe] = useState('ALL')
  const [marketStats, setMarketStats] = useState<any>(null)
  const [instFlow, setInstFlow] = useState<any>({
    FII_Net: 0,
    DII_Net: 0,
    Market_Sentiment: 'Initializing...'
  })
  const [triggering, setTriggering] = useState(false)
  const [loading, setLoading] = useState(true)

  // Quick Research State
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedStockForDrawer, setSelectedStockForDrawer] = useState<any>(null);

  const handleTrigger = async () => {
    setTriggering(true)
    try {
      await triggerBatchAnalysis()
      alert("Analysis triggered successfully! It will take a few minutes to complete.")
      fetchData()
    } catch (error) {
      console.error('Error triggering analysis:', error)
      alert("Failed to trigger analysis. Is the backend running?")
    } finally {
      setTriggering(false)
    }
  }

  const fetchData = async () => {
    try {
      const [stocksData, statsData, flowData] = await Promise.all([
        getStocks(),
        getMarketStats(),
        getInstitutionalFlow()
      ])
      const normalizedStocks = stocksData.map((s: any) => ({ ...s, decision: normalizeAITradeDecision(s) }));
      setStocks(normalizedStocks)
      setMarketStats(statsData)
      setInstFlow(flowData)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  // Refined Market Bias Logic
  const getMarketBias = () => {
    if (!marketStats) return { label: 'NEUTRAL', color: 'default', drivers: [] };

    const niftyChange = marketStats['NIFTY 50']?.change || 0;
    const breadthRatio = marketStats['Breadth']?.ratio || 1.0;
    const vix = marketStats['India VIX']?.value || 15;

    let score = 0;
    const drivers = [];
    if (niftyChange > 0.5) { score += 2; drivers.push('Nifty Trend'); }
    else if (niftyChange < -0.5) { score -= 2; drivers.push('Nifty Trend'); }

    if (breadthRatio > 1.5) { score += 2; drivers.push('Market Breadth'); }
    else if (breadthRatio < 0.6) { score -= 2; drivers.push('Market Breadth'); }

    if (vix < 14) { score += 1; drivers.push('Volatility (VIX)'); }
    else if (vix > 18) { score -= 1; drivers.push('Volatility (VIX)'); }

    if (score >= 3) return { label: 'STRONGLY BULLISH', color: 'primary', drivers };
    if (score >= 1) return { label: 'BULLISH', color: 'primary', drivers };
    if (score <= -3) return { label: 'STRONGLY BEARISH', color: 'error', drivers };
    if (score <= -1) return { label: 'BEARISH', color: 'error', drivers };
    return { label: 'NEUTRAL', color: 'default', drivers };
  };

  const bias = getMarketBias();

  return (
    <Box>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 2 }}>
        <Tabs
          value={selectedTimeframe}
          onChange={(_, v) => setSelectedTimeframe(v)}
          variant="scrollable"
          scrollButtons="auto"
          textColor="primary"
          indicatorColor="primary"
        >
          <Tab label="ALL" value="ALL" sx={{ fontWeight: 900, px: 4 }} />
          <Tab label="INTRADAY" value="INTRADAY" sx={{ fontWeight: 900, px: 4 }} />
          <Tab label="SWING" value="SWING" sx={{ fontWeight: 900, px: 4 }} />
          <Tab label="POSITION" value="POSITION" sx={{ fontWeight: 900, px: 4 }} />
          <Tab label="LONG TERM" value="LONG_TERM" sx={{ fontWeight: 900, px: 4 }} />
        </Tabs>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 900 }}>Market Command Center</Typography>
          <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>INSTITUTIONAL INTEL HUB • v2.1 PRO</Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Play size={18} />}
          onClick={handleTrigger}
          disabled={triggering}
          sx={{ borderRadius: 1, px: 3, fontWeight: 900 }}
        >
          {triggering ? 'SCANNING...' : 'FORCE ANALYTICS'}
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 8, gap: 2 }}>
          <CircularProgress />
          <Typography color="textSecondary" sx={{ fontWeight: 600 }}>Calibrating multi-agent decision engine...</Typography>
        </Box>
      ) : (
        <Box>
          <Paper sx={{ p: 0, mb: 4, overflow: 'hidden', border: '1px solid #1e293b', bgcolor: '#0f172a' }}>
            <Grid container>
              {/* Market Pulse */}
              <Grid item xs={12} md={3} sx={{ p: 3, borderRight: '1px solid #1e293b' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                   <Typography variant="subtitle2" color="textSecondary" sx={{ fontWeight: 900 }}>MARKET PULSE</Typography>
                   <Chip label="LIVE" size="small" sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900, bgcolor: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }} />
                </Box>
                <Stack spacing={2}>
                  <IndexRow label="NIFTY 50" data={marketStats?.['NIFTY 50']} />
                  <IndexRow label="BANK NIFTY" data={marketStats?.['BANK NIFTY']} />
                  <IndexRow label="INDIA VIX" data={marketStats?.['India VIX']} isVix />
                </Stack>
              </Grid>

              {/* Market Breadth */}
              <Grid item xs={12} md={3} sx={{ p: 3, borderRight: '1px solid #1e293b' }}>
                <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 2, fontWeight: 900 }}>MARKET BREADTH</Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="h3" fontWeight={900} color="primary">{marketStats?.Breadth?.advancing || 0}</Typography>
                    <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>ADVANCING</Typography>
                  </Box>
                  <Box sx={{ height: 60, width: 2, bgcolor: 'rgba(255,255,255,0.05)' }} />
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="h3" fontWeight={900} color="error">{marketStats?.Breadth?.declining || 0}</Typography>
                    <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>DECLINING</Typography>
                  </Box>
                </Box>
                <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block', textAlign: 'center', fontWeight: 700 }}>
                   Ratio: {marketStats?.Breadth?.ratio?.toFixed(2) || '1.00'}
                </Typography>
              </Grid>

              {/* Institutional Flow */}
              <Grid item xs={12} md={3} sx={{ p: 3, borderRight: '1px solid #1e293b' }}>
                <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 2, fontWeight: 900 }}>INSTITUTIONAL FLOW</Typography>
                <Stack spacing={1}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>FII Net</Typography>
                    <Typography variant="body2" fontWeight="bold" color={(instFlow?.FII_Net || 0) >= 0 ? 'primary' : 'error'}>
                      {(instFlow?.FII_Net || 0) >= 0 ? '+' : ''}{instFlow?.FII_Net || 0} Cr
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>DII Net</Typography>
                    <Typography variant="body2" fontWeight="bold" color={(instFlow?.DII_Net || 0) >= 0 ? 'primary' : 'error'}>
                      {(instFlow?.DII_Net || 0) >= 0 ? '+' : ''}{instFlow?.DII_Net || 0} Cr
                    </Typography>
                  </Box>
                </Stack>
                <Box sx={{ mt: 2, p: 1, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, border: '1px dashed #334155' }}>
                   <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mb: 0.5, fontSize: '0.6rem', fontWeight: 900 }}>REGIME</Typography>
                   <Typography variant="subtitle2" fontWeight="bold" color="primary">{instFlow?.Market_Sentiment || 'Syncing...'}</Typography>
                </Box>
              </Grid>

              {/* Market Regime / Bias */}
              <Grid item xs={12} md={3} sx={{ p: 3, bgcolor: 'rgba(16, 185, 129, 0.02)' }}>
                 <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 2, fontWeight: 900 }}>AI MARKET BIAS</Typography>
                 <Box sx={{ textAlign: 'center', mt: 1 }}>
                    <Chip
                      label={bias.label}
                      color={bias.color as any}
                      sx={{ fontWeight: 900, borderRadius: 1, width: '100%', height: 40, fontSize: '0.8rem' }}
                    />
                    <Box sx={{ mt: 1.5, textAlign: 'left' }}>
                       <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, fontSize: '0.55rem', display: 'block', mb: 0.5 }}>DRIVERS</Typography>
                       <Stack direction="row" spacing={1}>
                          {bias.drivers.map((d, i) => (
                            <Chip key={i} label={d} size="small" sx={{ height: 14, fontSize: '0.5rem', fontWeight: 900 }} />
                          ))}
                       </Stack>
                    </Box>
                 </Box>
              </Grid>
            </Grid>
          </Paper>

          <Grid container spacing={3}>
            {/* Market Outlook & Top Opportunities */}
            <Grid item xs={12} lg={8}>
              <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                   <Typography variant="h6" fontWeight={800}>Market Outlook</Typography>
                   <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>Updated {new Date().toLocaleTimeString()}</Typography>
                </Box>
                <MarketOutlook />
              </Box>

              <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                   <Typography variant="h6" fontWeight={800}>Top Opportunities</Typography>
                   <Button size="small" endIcon={<ChevronRight size={14} />} onClick={() => navigate('/ranking')}>View Full Scanner</Button>
                </Box>
                <TopOpportunities />
              </Box>
            </Grid>

            {/* Live Trade Signals */}
            <Grid item xs={12} lg={4}>
              <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column', border: '1px solid #1e293b' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                   <Typography variant="subtitle2" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 900 }}>
                      <LineChart size={16} /> LIVE TRADE SIGNALS
                   </Typography>
                   <Tooltip title="Actionable setups with specific entry/target levels.">
                      <AlertCircle size={14} style={{ color: '#94a3b8' }} />
                   </Tooltip>
                </Box>
                <Box sx={{ overflowY: 'auto', flexGrow: 1 }}>
                  {stocks.filter(s => {
                    if (!s.analysis) return false;
                    const timeframe = s.decision.timeframe;
                    return selectedTimeframe === 'ALL' || timeframe === selectedTimeframe;
                  }).length > 0 ? (
                    stocks.filter(s => {
                      if (!s.analysis) return false;
                      const timeframe = s.decision.timeframe;
                      return selectedTimeframe === 'ALL' || timeframe === selectedTimeframe;
                    }).map((stock) => {
                      const decision = stock.decision;

                      return (
                        <FeedItem
                          key={stock.symbol}
                          symbol={stock.symbol}
                          action={decision.rating}
                          timeframe={decision.timeframe}
                          entry={decision.entry}
                          target={decision.target}
                          stopLoss={decision.stopLoss}
                          conviction={decision.conviction}
                          catalyst={decision.primaryCatalyst || 'Analyzing session dynamics...'}
                          reason={decision.thesis}
                          onClick={() => {
                             setSelectedStockForDrawer(stock);
                             setDrawerOpen(true);
                          }}
                        />
                      );
                    })
                  ) : (
                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 2, opacity: 0.5 }}>
                      <MessageSquare size={48} />
                      <Typography color="textSecondary" align="center" sx={{ fontWeight: 600 }}>No {selectedTimeframe} active signals.</Typography>
                    </Box>
                  )}
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      )}

      <QuickResearchDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        stock={selectedStockForDrawer}
      />
    </Box>
  )
}

function IndexRow({ label, data, isVix = false }: any) {
  const isUp = (data?.change || 0) >= 0;
  const color = isVix ? (isUp ? '#f43f5e' : '#10b981') : (isUp ? '#10b981' : '#f43f5e');

  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <Typography variant="body2" sx={{ fontWeight: 700 }}>{label}</Typography>
      <Box sx={{ textAlign: 'right' }}>
        <Typography variant="body1" fontWeight={800} sx={{ fontFamily: 'JetBrains Mono' }}>
          {data?.value?.toLocaleString() || '---'}
        </Typography>
        <Typography variant="caption" sx={{ color: color, fontWeight: 'bold' }}>
          {isUp ? '+' : ''}{data?.change || 0}%
        </Typography>
      </Box>
    </Box>
  );
}

function FeedItem({ symbol, action, reason, conviction, catalyst, timeframe, entry, target, stopLoss, onClick }: any) {
  const isBuy = action?.toUpperCase().includes('BUY');
  const isSell = action?.toUpperCase().includes('SELL');

  return (
    <Box
      onClick={onClick}
      sx={{
        mb: 2, p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 2,
        borderLeft: `4px solid ${isBuy ? '#10b981' : isSell ? '#f43f5e' : '#fbbf24'}`,
        cursor: 'pointer',
        transition: '0.2s',
        '&:hover': { bgcolor: 'rgba(255,255,255,0.05)', transform: 'translateX(4px)' }
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Box>
          <Typography fontWeight="bold" sx={{ fontSize: '1rem' }}>{symbol}</Typography>
          <Typography variant="caption" color="primary" fontWeight="bold">{timeframe}</Typography>
        </Box>
        <Box sx={{ textAlign: 'right' }}>
           <Chip label={action} size="small" color={isBuy ? 'primary' : isSell ? 'error' : 'warning'} sx={{ fontWeight: 'bold', height: 20, fontSize: '0.65rem' }} />
           <Typography variant="caption" display="block" color="textSecondary" sx={{ mt: 0.5, fontWeight: 700 }}>{conviction}% AI</Typography>
        </Box>
      </Box>

      {target && (
        <Stack direction="row" spacing={2} sx={{ my: 1.5 }} justifyContent="space-between">
           <Box>
              <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 700 }}>
                 <Zap size={10} /> ENTRY
              </Typography>
              <Typography variant="body2" fontWeight="bold">₹{Math.round(entry)}</Typography>
           </Box>
           <Box>
              <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 700 }}>
                 <Target size={10} /> TARGET
              </Typography>
              <Typography variant="body2" fontWeight="bold" color="primary">₹{Math.round(target)}</Typography>
           </Box>
           <Box>
              <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 700 }}>
                 <ShieldCheck size={10} /> STOP
              </Typography>
              <Typography variant="body2" fontWeight="bold" color="error">₹{Math.round(stopLoss)}</Typography>
           </Box>
        </Stack>
      )}

      <Typography variant="caption" color="textSecondary" sx={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', lineHeight: 1.4, fontWeight: 500 }}>
         {catalyst || reason}
      </Typography>
    </Box>
  )
}
