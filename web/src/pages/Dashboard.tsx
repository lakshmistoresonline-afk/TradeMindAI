import { useEffect, useState } from 'react'
import { Box, Typography, Grid, Paper, Button } from '@mui/material'
import { TrendingUp, BarChart2, MessageSquare, ShieldCheck, Play } from 'lucide-react'
import { getStocks, triggerBatchAnalysis } from '../api/client'

export default function Dashboard() {
  const [stocks, setStocks] = useState<any[]>([])
  const [triggering, setTriggering] = useState(false)

  const handleTrigger = async () => {
    setTriggering(true)
    try {
      await triggerBatchAnalysis()
      alert("Analysis triggered successfully! It will take a few minutes to complete.")
    } catch (error) {
      console.error('Error triggering analysis:', error)
      alert("Failed to trigger analysis.")
    } finally {
      setTriggering(false)
    }
  }

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const data = await getStocks()
        setStocks(data)
      } catch (error) {
        console.error('Error fetching stocks:', error)
      }
    }
    fetchStocks()
  }, [])

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>Market Overview</Typography>
        <Button
          variant="contained"
          startIcon={<Play size={18} />}
          onClick={handleTrigger}
          disabled={triggering}
          sx={{ borderRadius: 2 }}
        >
          {triggering ? 'Triggering...' : 'Run Adhoc Analysis'}
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Dashboard Stats */}
        <Grid item xs={12} md={3}>
          <StatCard title="NIFTY 50" value="23,542.10" change="+1.2%" icon={<BarChart2 />} />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard title="BANK NIFTY" value="51,280.45" change="-0.4%" icon={<TrendingUp />} />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard title="India VIX" value="14.25" change="-2.1%" icon={<ShieldCheck />} />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatCard title="AI Signal" value="Strong Buy" change="85% Conf." icon={<MessageSquare />} />
        </Grid>

        {/* Main Content Area */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography variant="h5" color="textSecondary">
              TradingView Charts Integration Coming Soon
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '400px', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>AI Consensus Feed</Typography>
            <Box sx={{ overflowY: 'auto' }}>
              {stocks.length > 0 ? (
                stocks.map((stock) => (
                  <FeedItem
                    key={stock.symbol}
                    symbol={stock.symbol}
                    action={stock.last_price > 0 ? 'BUY' : 'HOLD'}
                    reason={`Price: ${stock.last_price} | Sector: ${stock.sector}`}
                  />
                ))
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                  <Typography color="textSecondary">No stocks analyzed yet.</Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
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
      <Typography variant="caption" color={change.startsWith('+') ? 'primary' : 'error'}>
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
