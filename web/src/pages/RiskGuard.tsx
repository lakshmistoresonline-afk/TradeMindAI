import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Stack, Chip, LinearProgress, Divider } from '@mui/material';
import { ShieldCheck, AlertTriangle, Crosshair, Activity, Info } from 'lucide-react';
import { getStocks, getPortfolioHealth } from '../api/client';

export default function RiskGuard() {
  const [holdings, setHoldings] = useState<any[]>([]);
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    getStocks().then(data => {
       const mockHoldings = data.filter((s:any) => ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK'].includes(s.symbol));
       setHoldings(mockHoldings);
    });
    getPortfolioHealth().then(setHealth);
  }, []);

  const portfolioRiskScore = health?.health_score || 0;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
         <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <ShieldCheck size={32} className="text-emerald-500" />
            <Box>
               <Typography variant="h4" sx={{ fontWeight: 900 }}>Risk Guard</Typography>
               <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>PORTFOLIO INTEGRITY & EXPOSURE MONITOR</Typography>
            </Box>
         </Box>
         <Stack direction="row" spacing={2}>
            <Chip label="RISK MODE: BALANCED" color="primary" variant="outlined" sx={{ fontWeight: 900 }} />
            <Chip icon={<Activity size={14} />} label="HEDGING ACTIVE" color="info" sx={{ fontWeight: 900 }} />
         </Stack>
      </Box>

      <Grid container spacing={3}>
         {/* 1. Portfolio Risk Score Card */}
         <Grid item xs={12} md={4}>
            <Paper sx={{ p: 4, height: '100%', border: '1px solid #1e293b' }}>
               <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 3, fontWeight: 900 }}>AGGREGATE RISK SCORE (BENCHMARK)</Typography>
               <Box sx={{ textAlign: 'center', mb: 4 }}>
                  <Typography variant="h1" sx={{ fontWeight: 900, color: 'primary.main', mb: 1 }}>{Math.round(portfolioRiskScore)}</Typography>
                  <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>{health?.risk_level === 'HIGH' ? 'HIGH' : 'OPTIMAL'} VOLATILITY SENSITIVITY</Typography>
               </Box>
               <LinearProgress variant="determinate" value={portfolioRiskScore} color="primary" sx={{ height: 8, borderRadius: 4, mb: 3 }} />
               <Divider sx={{ my: 3, opacity: 0.1 }} />
               <Stack spacing={2}>
                  <RiskFactor label="Beta Sensitivity" value={health?.avg_beta?.toFixed(2) || '1.00'} status={health?.avg_beta > 1.2 ? 'HIGH' : 'NORMAL'} />
                  <RiskFactor label="Diversification" value={`${Math.round(health?.diversification_score || 0)}%`} status={health?.diversification_score > 70 ? 'NORMAL' : 'LOW'} />
                  <RiskFactor label="Asset Correlation" value={health?.asset_correlation?.toFixed(2) || '0.50'} status="NORMAL" />
               </Stack>
            </Paper>
         </Grid>

         {/* 2. Position Risk Grid */}
         <Grid item xs={12} md={8}>
            <Paper sx={{ p: 0, overflow: 'hidden', border: '1px solid #1e293b' }}>
               <Box sx={{ p: 3, borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900 }}>POSITION-LEVEL EXPOSURE</Typography>
                  <Crosshair size={18} className="text-slategray" />
               </Box>
               <Box sx={{ p: 3 }}>
                  <Grid container spacing={3}>
                     {holdings.map(h => (
                        <Grid item xs={12} sm={6} lg={4} key={h.symbol}>
                           <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 2, border: '1px solid #334155' }}>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                                 <Typography variant="body2" fontWeight={900}>{h.symbol}</Typography>
                                 <Chip label="ACTIVE" size="small" sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900 }} />
                              </Box>
                              <Box sx={{ mb: 2 }}>
                                 <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                    <Typography variant="caption" color="textSecondary">Risk Contribution</Typography>
                                    <Typography variant="caption" fontWeight="bold">{(h.beta / (health?.avg_beta || 1) * 10).toFixed(1)}%</Typography>
                                 </Box>
                                 <LinearProgress variant="determinate" value={(h.beta / (health?.avg_beta || 1) * 10)} color="warning" sx={{ height: 4, borderRadius: 2 }} />
                              </Box>
                              <Typography variant="caption" color="textSecondary" sx={{ display: 'block', fontWeight: 600 }}>VaR (95%): ₹{Math.round(health?.var_95 / 5).toLocaleString()}</Typography>
                           </Box>
                        </Grid>
                     ))}
                  </Grid>
               </Box>
            </Paper>
         </Grid>

         {/* 3. AI Risk Mitigation Strategy */}
         <Grid item xs={12} md={7}>
            <Paper sx={{ p: 4, border: '1px solid #1e293b' }}>
               <Stack direction="row" spacing={1} alignItems="center" mb={3}>
                  <AlertTriangle size={20} className="text-amber-500" />
                  <Typography variant="h6" fontWeight={900}>AI Intelligence Alerts</Typography>
               </Stack>
               <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <RiskAlert
                    title="High Sector Correlation Detected"
                    desc="Your holdings in TCS and INFY show a 0.88 correlation over the last 30 days. Recommend trimming one position to reduce sector-specific risk."
                  />
                  <RiskAlert
                    title="Gamma Exposure Warning"
                    desc="Near-term options expiry in HDFCBANK suggests heightened volatility. Ensure stop-loss levels are adjusted for wider ATR."
                  />
                  <RiskAlert
                    title="Institutional Distribution Pattern"
                    desc="Large block selling detected in RELIANCE at 2550 resistance. Institutional flow is turning negative for the weekly timeframe."
                  />
               </Box>
            </Paper>
         </Grid>

         {/* 4. Portfolio Concentration */}
         <Grid item xs={12} md={5}>
            <Paper sx={{ p: 4, height: '100%', border: '1px solid #1e293b' }}>
               <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 3, fontWeight: 900 }}>CONCENTRATION MATRIX</Typography>
               <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                  <Box>
                     <Typography variant="caption" color="textSecondary" fontWeight={800} display="block" sx={{ mb: 1 }}>TOP 3 ASSETS EXPOSURE</Typography>
                     <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="h5" fontWeight={900}>58.2%</Typography>
                        <Chip label="HIGH" size="small" color="error" sx={{ fontWeight: 900, height: 18, fontSize: '0.6rem' }} />
                     </Box>
                     <LinearProgress variant="determinate" value={58} color="error" sx={{ height: 6, borderRadius: 3 }} />
                  </Box>
                  <Divider sx={{ opacity: 0.05 }} />
                  <Box>
                     <Typography variant="caption" color="textSecondary" fontWeight={800} display="block" sx={{ mb: 1 }}>SECTOR DIVERSIFICATION</Typography>
                     <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                        {health?.sector_allocation && Object.entries(health.sector_allocation).map(([sector, pct]) => (
                           <Chip key={sector} label={`${sector}: ${Math.round(pct as number)}%`} size="small" variant="outlined" sx={{ fontWeight: 700 }} />
                        ))}
                     </Stack>
                  </Box>
               </Box>
            </Paper>
         </Grid>
      </Grid>
    </Box>
  );
}

function RiskFactor({ label, value, status }: any) {
   return (
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
         <Typography variant="body2" sx={{ fontWeight: 700, color: 'text.secondary' }}>{label}</Typography>
         <Stack direction="row" spacing={1} alignItems="center">
            <Typography variant="body1" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
            <Typography variant="caption" sx={{ fontWeight: 900, color: status === 'NORMAL' ? 'primary.main' : 'error.main', fontSize: '0.6rem' }}>{status}</Typography>
         </Stack>
      </Box>
   );
}

function RiskAlert({ title, desc }: any) {
   return (
      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, p: 2, bgcolor: 'rgba(255,255,255,0.01)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.05)' }}>
         <Box sx={{ mt: 0.5 }}><Info size={16} className="text-slategray" /></Box>
         <Box>
            <Typography variant="body2" fontWeight={800} color="primary.main">{title}</Typography>
            <Typography variant="caption" sx={{ mt: 0.5, display: 'block', color: 'text.secondary', lineHeight: 1.5 }}>{desc}</Typography>
         </Box>
      </Box>
   );
}
