import { Box, Typography, Container, Grid, Paper, AppBar, Toolbar } from '@mui/material'
import { TrendingUp, BarChart2, MessageSquare, ShieldCheck } from 'lucide-react'

function App() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" color="transparent" elevation={0} sx={{ borderBottom: '1px solid #334155' }}>
        <Toolbar>
          <TrendingUp className="text-emerald-500 mr-2" />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            TradeMind AI
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4 }}>
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
                <FeedItem symbol="RELIANCE" action="BUY" reason="Order Block rejection at 2450" />
                <FeedItem symbol="TCS" action="HOLD" reason="RSI Divergence on Daily" />
                <FeedItem symbol="INFY" action="BUY" reason="FVG Fill + Bullish Engulfing" />
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Container>
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

export default App
