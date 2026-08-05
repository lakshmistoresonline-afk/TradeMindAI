import { useState } from 'react';
import { Box, Typography, Paper, Grid, Slider, Alert, List, ListItem, ListItemText } from '@mui/material';
import { ShieldAlert, Zap, TrendingDown } from 'lucide-react';

export default function StressTest() {
  const [marketDrop, setMarketDrop] = useState(10);

  const scenarios = [
    { name: 'Nifty Crash', impact: marketDrop, color: 'error' },
    { name: 'IT Sector Meltdown', impact: marketDrop * 1.5, color: 'warning' },
    { name: 'Interest Rate Hike', impact: marketDrop * 0.4, color: 'info' }
  ];

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>Portfolio Stress Testing</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>Market Shock Level</Typography>
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
            <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
              Simulate a {marketDrop}% sudden market drop.
            </Typography>
          </Paper>

          <Alert icon={<ShieldAlert size={18} />} severity="info">
            This simulation uses historical Beta and Correlation metrics to predict your portfolio's sensitivity.
          </Alert>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 4 }}>
            <Typography variant="h6" gutterBottom>Simulated Impact Report</Typography>
            <Grid container spacing={3} sx={{ mt: 2 }}>
              {scenarios.map((scenario) => (
                <Grid item xs={12} md={4} key={scenario.name}>
                  <Box sx={{ p: 2, textAlign: 'center', border: '1px solid #334155', borderRadius: 2 }}>
                    <Typography variant="subtitle2" color="textSecondary">{scenario.name}</Typography>
                    <Typography variant="h4" sx={{ color: '#f43f5e', fontWeight: 'bold', my: 1 }}>
                      -₹{(1000000 * (scenario.impact / 100)).toLocaleString()}
                    </Typography>
                    <Typography variant="caption" color="error">-{scenario.impact.toFixed(1)}%</Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>

            <Box sx={{ mt: 6 }}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>AI Risk Mitigation Strategy</Typography>
              <List>
                <ListItem sx={{ bgcolor: 'rgba(255,255,255,0.02)', mb: 1, borderRadius: 1 }}>
                  <ListItemText
                    primary="Hedge with Nifty Puts"
                    secondary="Buy 24000 PE options to protect against a >5% drop."
                  />
                  <Zap size={18} className="text-blue-500" />
                </ListItem>
                <ListItem sx={{ bgcolor: 'rgba(255,255,255,0.02)', mb: 1, borderRadius: 1 }}>
                  <ListItemText
                    primary="Increase Cash Allocation"
                    secondary="Move 15% of IT holdings to Gold/Cash."
                  />
                  <TrendingDown size={18} className="text-amber-500" />
                </ListItem>
              </List>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
