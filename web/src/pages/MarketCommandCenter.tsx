import { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Grid, Paper, Stack, Chip, Divider,
  CircularProgress, alpha, LinearProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import {
  Globe, Zap, Users, Activity
} from 'lucide-react';
import { apiClient } from '../api/client';

export default function MarketCommandCenter() {
  const [market, setMarket] = useState<any>(null);
  const [radar, setRadar] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [mRes, rRes, sRes] = await Promise.all([
        apiClient.get('/shadow/intelligence/market'),
        apiClient.get('/shadow/intelligence/radar'),
        apiClient.get('/shadow/summary')
      ]);
      setMarket(mRes.data);
      setRadar(rRes.data);
      setSummary(sRes.data);
    } catch (err) {
      console.error("Command Center fetch failed", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>;

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 900 }}>MARKET COMMAND CENTER <Chip label="PRODUCTION LIVE" color="success" size="small" /></Typography>

      <Grid container spacing={3}>
        {/* Tier 1: Core Indices & Regime */}
        <Grid item xs={12} md={4}>
           <Paper sx={{ p: 3, height: '100%', bgcolor: alpha('#3b82f6', 0.05), border: '1px solid rgba(59, 130, 246, 0.2)' }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                 <Globe size={20} color="#3b82f6" />
                 <Typography variant="h6" fontWeight={800}>REGIME: {market?.regime || 'SIDEWAYS'}</Typography>
              </Stack>
              <Typography variant="h2" fontWeight={950} sx={{ textAlign: 'center', my: 2 }}>{Math.round((market?.sentiment || 0.5) * 100)}%</Typography>
              <Typography variant="caption" color="text.secondary" align="center" display="block">BULLISH SENTIMENT SCORE</Typography>
              <Divider sx={{ my: 3 }} />
              <Stack spacing={2}>
                 <StatRow label="NIFTY 50" value="25,235.10" change="+0.45%" />
                 <StatRow label="BANKNIFTY" value="51,800.00" change="+0.12%" />
                 <StatRow label="INDIA VIX" value="13.25" change="-2.40%" color="#10b981" />
              </Stack>
           </Paper>
        </Grid>

        {/* Tier 1: Portfolio Snapshot */}
        <Grid item xs={12} md={4}>
           <Paper sx={{ p: 3, height: '100%' }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                 <Activity size={20} color="#00D1FF" />
                 <Typography variant="h6" fontWeight={800}>PORTFOLIO EQUITY</Typography>
              </Stack>
              <Typography variant="h3" fontWeight={950} sx={{ textAlign: 'center', my: 2 }}>₹{summary?.equity?.toLocaleString()}</Typography>
              <Divider sx={{ my: 3 }} />
              <Stack spacing={2}>
                 <StatRow label="GROSS EXPOSURE" value={`₹${summary?.gross_exposure?.toLocaleString()}`} />
                 <StatRow label="NET EXPOSURE" value={`₹${summary?.net_exposure?.toLocaleString()}`} />
                 <StatRow label="PROFIT FACTOR" value={summary?.profit_factor || '1.0'} />
              </Stack>
           </Paper>
        </Grid>

        {/* Tier 1: Institutional Flow */}
        <Grid item xs={12} md={4}>
           <Paper sx={{ p: 3, height: '100%' }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                 <Users size={20} color="#7c3aed" />
                 <Typography variant="h6" fontWeight={800}>INSTITUTIONAL BIAS</Typography>
              </Stack>
              <Box sx={{ textAlign: 'center', py: 2 }}>
                 <Chip
                    label={market?.institutional_bias?.bias || 'NEUTRAL'}
                    color={market?.institutional_bias?.bias === 'BULLISH' ? 'success' : 'error'}
                    sx={{ fontWeight: 900, px: 2 }}
                 />
              </Box>
              <Divider sx={{ my: 3 }} />
              <Stack spacing={2}>
                 <StatRow label="FII NET (CR)" value={`₹${market?.institutional_bias?.fii_net_today?.toLocaleString()}`} />
                 <StatRow label="DII NET (CR)" value={`₹${market?.institutional_bias?.dii_net_today?.toLocaleString()}`} />
                 <StatRow label="FII AVG (10D)" value={`₹${market?.institutional_bias?.fii_avg_10d?.toLocaleString()}`} />
              </Stack>
           </Paper>
        </Grid>

        {/* Tier 2: Opportunity Radar */}
        <Grid item xs={12}>
           <Paper sx={{ p: 3 }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 3 }}>
                 <Zap size={20} color="#f59e0b" />
                 <Typography variant="h6" fontWeight={800}>OPPORTUNITY RADAR (ALPHA DISCOVERY)</Typography>
              </Stack>
              <TableContainer>
                 <Table size="small">
                    <TableHead>
                       <TableRow>
                          <TableCell>SYMBOL</TableCell>
                          <TableCell>TYPE</TableCell>
                          <TableCell>INTELLIGENCE SCORE</TableCell>
                          <TableCell>THESIS</TableCell>
                          <TableCell align="right">AGE</TableCell>
                       </TableRow>
                    </TableHead>
                    <TableBody>
                       {radar.slice(0, 5).map((opp: any) => (
                          <TableRow key={opp.id} hover>
                             <TableCell sx={{ fontWeight: 900, color: '#00D1FF' }}>{opp.symbol}</TableCell>
                             <TableCell><Chip label={opp.type} size="small" sx={{ fontWeight: 800, fontSize: '0.6rem' }} /></TableCell>
                             <TableCell>
                                <Stack direction="row" spacing={2} alignItems="center">
                                   <Typography variant="body2" fontWeight={800}>{opp.conviction_score}%</Typography>
                                   <LinearProgress variant="determinate" value={opp.conviction_score} sx={{ flexGrow: 1, height: 4, borderRadius: 1 }} />
                                </Stack>
                             </TableCell>
                             <TableCell sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>{opp.ai_thesis}</TableCell>
                             <TableCell align="right" sx={{ fontSize: '0.65rem' }}>LIVE</TableCell>
                          </TableRow>
                       ))}
                    </TableBody>
                 </Table>
              </TableContainer>
           </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function StatRow({ label, value, change, color }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
       <Typography variant="caption" sx={{ fontWeight: 800, color: 'slategray' }}>{label}</Typography>
       <Stack direction="row" spacing={1} alignItems="center">
          <Typography variant="body2" sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
          {change && <Typography variant="caption" sx={{ fontWeight: 900, color: color || '#10b981' }}>{change}</Typography>}
       </Stack>
    </Box>
  );
}
