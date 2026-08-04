import { useEffect, useState } from 'react'
import { Box, Typography, Grid, Paper, Button, CircularProgress, Stack } from '@mui/material'
import { TrendingUp, BarChart2, MessageSquare, ShieldCheck, Play } from 'lucide-react'
import { getStocks, triggerBatchAnalysis, getMarketStats } from '../api/client'

export default function Dashboard() {
  const [stocks, setStocks] = useState<any[]>([])
  const [marketStats, setMarketStats] = useState<any>(null)
  const [triggering, setTriggering] = useState(false)
  const [loading, setLoading] = useState(true)

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
        const [stocksData, statsData] = await Promise.all([
          getStocks(),
          getMarketStats()
        ])
        setStocks(stocksData)
        setMarketStats(statsData)
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>Market Overview</Typography>
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
        <Grid container spacing={3}>
          {/* Dashboard Stats */}
          <Grid item xs={12} md={3}>
            <StatCard
              title="NIFTY 50"
              value={marketStats?.['NIFTY 50']?.value?.toLocaleString() || '---'}
              change={marketStats?.['NIFTY 50'] ? `${marketStats?.['NIFTY 50'].change}%` : '0%'}
              icon={<BarChart2 />}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <StatCard
              title="BANK NIFTY"
              value={marketStats?.['BANK NIFTY']?.value?.toLocaleString() || '---'}
              change={marketStats?.['BANK NIFTY'] ? `${marketStats?.['BANK NIFTY'].change}%` : '0%'}
              icon={<TrendingUp />}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <StatCard
              title="India VIX"
              value={marketStats?.['India VIX']?.value?.toString() || '---'}
              change={marketStats?.['India VIX'] ? `${marketStats?.['India VIX'].change}%` : '0%'}
              icon={<ShieldCheck />}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <StatCard
              title="AI Sentiment"
              value={signalStrength > 60 ? 'Bullish' : signalStrength < 40 ? 'Bearish' : 'Neutral'}
              change={`${signalStrength}% Conf.`}
              icon={<MessageSquare />}
            />
          </Grid>

          {/* TradingView Chart */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 0, height: '500px', overflow: 'hidden' }}>
              <iframe
                src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_76d87&symbol=NSE%3ANIFTY&interval=D&hidesidetoolbar=1&hidetoptoolbar=1&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=%5B%5D&theme=dark&style=1&timezone=Etc%2FUTC&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=en&utm_source=localhost&utm_medium=widget&utm_campaign=chart&utm_term=NSE%3ANIFTY"
                width="100%"
                height="100%"
                frameBorder="0"
                allowTransparency
                allowFullScreen
              ></iframe>
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, height: '500px', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom>Live AI Signals</Typography>
              <Box sx={{ overflowY: 'auto' }}>
                {stocks.filter(s => s.analysis).length > 0 ? (
                  stocks.filter(s => s.analysis).map((stock) => (
                    <FeedItem
                      key={stock.symbol}
                      symbol={stock.symbol}
                      action={stock.analysis.consensus.toUpperCase().includes('BUY') ? 'BUY' : 'HOLD'}
                      reason={stock.analysis.recommendations[0]?.analysis.substring(0, 100) + '...'}
                    />
                  ))
                ) : (
                  <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                    <Typography color="textSecondary" align="center">No live signals found. <br/> Trigger analysis to populate data.</Typography>
                  </Box>
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  )
}

function StatCard({ title, value, change, icon }: any) {
  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography color="textSecondary" variant="subtitle2">{title}</Typography>
        <Box className="text-emerald-500">{icon}</Box>
      </Box>
      <Typography variant="h5" fontWeight="bold">{value}</Typography>
      <Typography variant="caption" color={change.startsWith('-') ? 'error' : 'primary'}>
        {change} Today
      </Typography>
    </Paper>
  )
}

function FeedItem({ symbol, action, reason }: any) {
  return (
    <Box sx={{ mb: 2, p: 1, borderBottom: '1px solid #334155' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Typography fontWeight="bold">{symbol}</Typography>
        <Typography color={action === 'BUY' ? 'primary' : 'warning'}>{action}</Typography>
      </Box>
      <Typography variant="caption" color="textSecondary">{reason}</Typography>
    </Box>
  )
}
