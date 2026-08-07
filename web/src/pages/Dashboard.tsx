import { useEffect, useState } from 'react'
import { Box, Typography, Grid, Paper, Button, CircularProgress, Divider, Chip, Stack } from '@mui/material'
import { MessageSquare, Play } from 'lucide-react'
import { getStocks, triggerBatchAnalysis, getMarketStats, getInstitutionalFlow } from '../api/client'
import MarketBrief from '../components/Research/MarketBrief'
import OpportunityEngine from '../components/Research/OpportunityEngine'
import QuickResearchDrawer from '../components/Research/QuickResearchDrawer'

export default function Dashboard() {
  const [stocks, setStocks] = useState<any[]>([])
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
    } catch (error) {
      console.error('Error triggering analysis:', error)
      alert("Failed to trigger analysis. Is the backend running?")
    } finally {
      setTriggering(false)
    }
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [stocksData, statsData, flowData] = await Promise.all([
          getStocks(),
          getMarketStats(),
          getInstitutionalFlow()
        ])
        setStocks(stocksData)
        setMarketStats(statsData)
        setInstFlow(flowData)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  // Calculate Aggregate AI Signal
  const buySignals = stocks.filter(s => s.analysis?.consensus?.toUpperCase().includes('BUY')).length;
  const signalStrength = stocks.length > 0 ? Math.round((buySignals / stocks.length) * 100) : 0;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>Market Overview</Typography>
          <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 'bold' }}>
             TRADING SESSION: {new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Play size={18} />}
          onClick={handleTrigger}
          disabled={triggering}
          sx={{ borderRadius: 2, px: 3 }}
        >
          {triggering ? 'Triggering...' : 'Run Adhoc Analysis'}
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 8, gap: 2 }}>
          <CircularProgress />
          <Typography color="textSecondary">Connecting to institutional agents...</Typography>
        </Box>
      ) : (
        <Box>
          {/* RC-4: Unified Market Pulse Header */}
          <Paper sx={{ p: 0, mb: 4, overflow: 'hidden', border: '1px solid #1e293b', bgcolor: '#0f172a' }}>
            <Grid container>
              {/* Indices Pulse */}
              <Grid item xs={12} md={4} sx={{ p: 3, borderRight: { md: '1px solid #1e293b' }, borderBottom: { xs: '1px solid #1e293b', md: 'none' } }}>
                <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 2 }}>MARKET INDICES</Typography>
                <Stack spacing={2}>
                  <IndexRow label="NIFTY 50" data={marketStats?.['NIFTY 50']} />
                  <IndexRow label="BANK NIFTY" data={marketStats?.['BANK NIFTY']} />
                  <IndexRow label="INDIA VIX" data={marketStats?.['India VIX']} isVix />
                </Stack>
              </Grid>

              {/* Breadth & Sentiment Pulse */}
              <Grid item xs={12} md={4} sx={{ p: 3, borderRight: { md: '1px solid #1e293b' }, borderBottom: { xs: '1px solid #1e293b', md: 'none' } }}>
                <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 2 }}>SESSION BREADTH</Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="h3" fontWeight={900} color="primary">{marketStats?.Breadth?.advancing || 0}</Typography>
                    <Typography variant="caption" color="textSecondary">ADVANCING</Typography>
                  </Box>
                  <Box sx={{ height: 60, width: 2, bgcolor: 'rgba(255,255,255,0.05)' }} />
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="h3" fontWeight={900} color="error">{marketStats?.Breadth?.declining || 0}</Typography>
                    <Typography variant="caption" color="textSecondary">DECLINING</Typography>
                  </Box>
                </Box>
                <Divider sx={{ my: 2, opacity: 0.05 }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" color="textSecondary">AI SENTIMENT</Typography>
                  <Chip
                    label={signalStrength > 60 ? 'BULLISH' : signalStrength < 40 ? 'BEARISH' : 'NEUTRAL'}
                    size="small"
                    color={signalStrength > 60 ? 'primary' : signalStrength < 40 ? 'error' : 'default'}
                    sx={{ fontWeight: 'bold', borderRadius: 1 }}
                  />
                </Box>
              </Grid>

              {/* Institutional Flow Pulse */}
              <Grid item xs={12} md={4} sx={{ p: 3, bgcolor: 'rgba(16, 185, 129, 0.02)' }}>
                <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 2 }}>INSTITUTIONAL FLOW (EST.)</Typography>
                <Stack spacing={1}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">FII Net</Typography>
                    <Typography variant="body2" fontWeight="bold" color={(instFlow?.FII_Net || 0) >= 0 ? 'primary' : 'error'}>
                      {(instFlow?.FII_Net || 0) >= 0 ? '+' : ''}{instFlow?.FII_Net || 0} Cr
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">DII Net</Typography>
                    <Typography variant="body2" fontWeight="bold" color={(instFlow?.DII_Net || 0) >= 0 ? 'primary' : 'error'}>
                      {(instFlow?.DII_Net || 0) >= 0 ? '+' : ''}{instFlow?.DII_Net || 0} Cr
                    </Typography>
                  </Box>
                </Stack>
                <Box sx={{ mt: 3, p: 1.5, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, border: '1px dashed #334155' }}>
                   <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mb: 0.5 }}>INSTITUTIONAL BIAS</Typography>
                   <Typography variant="subtitle2" fontWeight="bold" color="primary">{instFlow?.Market_Sentiment || 'Syncing...'}</Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>

          <Grid container spacing={3}>
            {/* Live Signals & Market Brief */}
            <Grid item xs={12} lg={8}>
              <MarketBrief />
              <OpportunityEngine />
            </Grid>

            <Grid item xs={12} lg={4}>
              <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column', border: '1px solid #1e293b' }}>
                <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 3 }}>LIVE AI SIGNALS</Typography>
                <Box sx={{ overflowY: 'auto', flexGrow: 1 }}>
                  {stocks.filter(s => s.analysis).length > 0 ? (
                    stocks.filter(s => s.analysis).map((stock) => {
                      const analysis = stock.analysis || {};
                      const structured = stock.structured_consensus || {};
                      const rating = structured.rating || (analysis.consensus?.toUpperCase().includes('BUY') ? 'BUY' : 'HOLD');

                      return (
                        <FeedItem
                          key={stock.symbol}
                          symbol={stock.symbol}
                          action={rating}
                          conviction={structured.conviction || stock.ai_investment_score || 0}
                          catalyst={structured.key_catalysts?.[0] || 'Analyzing session dynamics...'}
                          reason={structured.thesis || analysis.consensus}
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
                      <Typography color="textSecondary" align="center">No live signals found.</Typography>
                      <Button variant="outlined" size="small" onClick={handleTrigger}>Start Analysis</Button>
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
      <Typography variant="body2" sx={{ fontWeight: 600 }}>{label}</Typography>
      <Box sx={{ textAlign: 'right' }}>
        <Typography variant="body1" fontWeight={800}>
          {data?.value?.toLocaleString() || '---'}
        </Typography>
        <Typography variant="caption" sx={{ color: color, fontWeight: 'bold' }}>
          {isUp ? '+' : ''}{data?.change || 0}%
        </Typography>
      </Box>
    </Box>
  );
}

function FeedItem({ symbol, action, reason, conviction, catalyst, onClick }: any) {
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
        <Typography fontWeight="bold" sx={{ fontSize: '1rem' }}>{symbol}</Typography>
        <Box sx={{ textAlign: 'right' }}>
           <Chip label={action} size="small" color={isBuy ? 'primary' : isSell ? 'error' : 'warning'} sx={{ fontWeight: 'bold', height: 20, fontSize: '0.65rem' }} />
           <Typography variant="caption" display="block" color="textSecondary" sx={{ mt: 0.5 }}>{conviction}% Conviction</Typography>
        </Box>
      </Box>
      <Typography variant="caption" color="textSecondary" sx={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', lineHeight: 1.4 }}>
         {catalyst || reason}
      </Typography>
    </Box>
  )
}
