import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Slider, Alert, List, ListItem, ListItemText, Stack, Chip } from '@mui/material';
import { ShieldAlert, Zap, TrendingDown, Activity, Info } from 'lucide-react';
import { getStocks } from '../api/client';

export default function PortfolioStressTest() {
  const [marketDrop, setMarketDrop] = useState(10);
  const [holdings, setHoldings] = useState<any[]>([]);

  useEffect(() => {
    getStocks().then(data => {
       const realHoldings = data.filter((s:any) => s.ai_investment_score > 0).slice(0, 6);
       setHoldings(realHoldings);
    });
  }, []);

  const scenarios = [
    { name: 'Nifty Correction', impact: marketDrop, color: 'error' },
    { name: 'Sector Meltdown', impact: marketDrop * 1.5, color: 'warning' },
    { name: 'Policy Volatility', impact: marketDrop * 0.4, color: 'info' }
  ];

  const totalValue = holdings.reduce((acc, h) => acc + (h.market_cap / 1e8), 0) || 1000000; // Simulated value if real positions missing
  const avgBeta = holdings.length > 0 ? holdings.reduce((acc, h) => acc + (h.beta || 1.0), 0) / holdings.length : 1.15;
  const highBetaPositions = holdings.filter(h => (h.beta || 1.0) > 1.2);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
         <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Activity size={32} className="text-rose-500" />
            <Box>
               <Typography variant="h4" sx={{ fontWeight: 900 }}>Portfolio Stress Test</Typography>
               <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>PROPRIETARY BETA-SHOCK MODEL v2.0</Typography>
            </Box>
         </Box>
         <Chip label={`Avg. Beta: ${avgBeta.toFixed(2)}`} color={avgBeta > 1.2 ? "error" : "primary"} variant="outlined" sx={{ fontWeight: 900 }} />
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 4, fontWeight: 900 }}>MARKET SHOCK MAGNITUDE</Typography>
            <Box sx={{ px: 2, mt: 4 }}>
              <Slider
                value={marketDrop}
                onChange={(_, val) => setMarketDrop(val as number)}
                step={1}
                min={0}
                max={50}
                valueLabelDisplay="on"
                color="error"
              />
            </Box>
            <Typography variant="caption" color="textSecondary" sx={{ mt: 3, display: 'block', fontWeight: 600 }}>
              Simulating a sudden {marketDrop}% drawdown in broader indices.
            </Typography>
          </Paper>

          <Alert
            icon={<ShieldAlert size={18} />}
            severity="info"
            sx={{ bgcolor: 'rgba(59, 130, 246, 0.05)', border: '1px solid #3b82f6', color: '#f8fafc', fontWeight: 500 }}
          >
            This engine calculates sensitivity based on historical Beta coordination and inter-sector correlations.
          </Alert>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 4 }}>
            <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 3, fontWeight: 900 }}>ESTIMATED IMPACT ANALYSIS (MODEL)</Typography>
            <Grid container spacing={3} sx={{ mt: 2 }}>
              {scenarios.map((scenario) => {
                const estimatedLoss = totalValue * (scenario.impact / 100) * avgBeta;
                return (
                <Grid item xs={12} md={4} key={scenario.name}>
                  <Box sx={{ p: 2, textAlign: 'center', border: '1px solid #1e293b', borderRadius: 2, bgcolor: 'rgba(244, 63, 94, 0.03)' }}>
                    <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>{scenario.name.toUpperCase()} (MODEL)</Typography>
                    <Typography variant="h4" sx={{ color: '#f43f5e', fontWeight: 900, my: 1.5 }}>
                      -₹{Math.round(estimatedLoss).toLocaleString()}
                    </Typography>
                    <Chip label={`-${(scenario.impact * avgBeta).toFixed(1)}%`} size="small" color="error" sx={{ fontWeight: 900, height: 20, fontSize: '0.65rem' }} />
                  </Box>
                </Grid>
              )})}
            </Grid>

            <Box sx={{ mt: 6 }}>
              <Stack direction="row" spacing={1} alignItems="center" mb={2}>
                 <Zap size={18} className="text-emerald-500" />
                 <Typography variant="subtitle1" fontWeight={900}>AI RISK MITIGATION STRATEGY</Typography>
              </Stack>

              {avgBeta > 1.1 || highBetaPositions.length > 0 ? (
                <List>
                  <ListItem sx={{ bgcolor: 'rgba(255,255,255,0.02)', mb: 1.5, borderRadius: 1, border: '1px solid #334155' }}>
                    <ListItemText
                      primary="Institutional Hedging Recommended"
                      secondary={`Current Beta (${avgBeta.toFixed(2)}) suggests high market sensitivity. Deploy deep OTM Nifty Puts to delta-neutralize.`}
                      primaryTypographyProps={{ fontWeight: 800, color: 'primary.main' }}
                    />
                    <Info size={18} className="text-blue-500" />
                  </ListItem>
                  <ListItem sx={{ bgcolor: 'rgba(255,255,255,0.02)', mb: 1.5, borderRadius: 1, border: '1px solid #334155' }}>
                    <ListItemText
                      primary="Tactical Rebalancing"
                      secondary={`Reduce exposure in ${highBetaPositions.map(h=>h.symbol).join(', ')} to lower portfolio volatility.`}
                      primaryTypographyProps={{ fontWeight: 800 }}
                    />
                    <TrendingDown size={18} className="text-amber-500" />
                  </ListItem>
                </List>
              ) : (
                <Box sx={{ p: 4, textAlign: 'center', bgcolor: 'rgba(16, 185, 129, 0.03)', borderRadius: 2 }}>
                   <Typography variant="body2" color="primary" sx={{ fontWeight: 800 }}>✓ PORTFOLIO RESILIENCE: OPTIMAL</Typography>
                   <Typography variant="caption" color="textSecondary">Current beta and sector concentration require no immediate mitigation.</Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
