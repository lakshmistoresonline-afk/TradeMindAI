import { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Grid, Paper, Stack, Chip, Divider,
  CircularProgress, alpha, LinearProgress
} from '@mui/material';
import {
  Brain, TrendingUp, Users, BarChart3, Globe, ShieldCheck
} from 'lucide-react';
import { apiClient } from '../api/client';

export default function IntelligenceDashboard() {
  const [market, setMarket] = useState<any>(null);
  const [sectors, setSectors] = useState<any[]>([]);
  const [fno, setFno] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [mRes, sRes, fRes] = await Promise.all([
        apiClient.get('/shadow/intelligence/market'),
        apiClient.get('/shadow/intelligence/sectors'),
        apiClient.get('/shadow/intelligence/fno')
      ]);
      setMarket(mRes.data);
      setSectors(sRes.data);
      setFno(fRes.data);
    } catch (err) {
      console.error("Intelligence fetch failed", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, [fetchData]);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>;

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 900 }}>ADVANCED INTELLIGENCE <Chip label="RC-7C" color="primary" size="small" /></Typography>

      <Grid container spacing={3}>
        {/* Market Regime */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
              <Globe size={20} color="#3b82f6" />
              <Typography variant="h6" fontWeight={800}>MARKET REGIME</Typography>
            </Stack>
            <Box sx={{ textAlign: 'center', py: 2 }}>
               <Typography variant="h3" fontWeight={950} color="primary.main">{market?.regime || 'SIDEWAYS'}</Typography>
               <Typography variant="caption" color="text.secondary">SENTIMENT SCORE: {market?.sentiment?.toFixed(2) || '0.50'}</Typography>
            </Box>
            <Divider sx={{ my: 2 }} />
            <Typography variant="overline" color="text.secondary">INSTITUTIONAL BIAS</Typography>
            <Typography variant="h6" fontWeight={800} color={market?.institutional_bias?.bias === 'BULLISH' ? '#10b981' : '#ef4444'}>
              {market?.institutional_bias?.bias || 'NEUTRAL'}
            </Typography>
          </Paper>
        </Grid>

        {/* Sector Rotation */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 3 }}>
              <TrendingUp size={20} color="#10b981" />
              <Typography variant="h6" fontWeight={800}>SECTOR ROTATION (RANKED)</Typography>
            </Stack>
            <Grid container spacing={2}>
              {sectors.slice(0, 8).map((s: any) => (
                <Grid item xs={12} sm={6} md={3} key={s.sector}>
                   <Box sx={{ p: 2, bgcolor: alpha('#fff', 0.02), borderRadius: 1, border: '1px solid rgba(255,255,255,0.05)' }}>
                      <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray' }}>RANK #{s.rank}</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 900, mb: 1 }}>{s.sector}</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(100, Math.max(0, s.relative_strength * 10))}
                        sx={{ height: 4, borderRadius: 1, bgcolor: alpha('#fff', 0.05) }}
                      />
                   </Box>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>

        {/* F&O Sentiment */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
              <ShieldCheck size={20} color="#7c3aed" />
              <Typography variant="h6" fontWeight={800}>F&O SENTIMENT (INDEX)</Typography>
            </Stack>
            <Grid container spacing={4}>
               <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">NIFTY PCR</Typography>
                  <Typography variant="h4" fontWeight={900}>{fno?.nifty_pcr?.toFixed(2) || '1.00'}</Typography>
               </Grid>
               <Grid item xs={6}>
                  <Typography variant="caption" color="text.secondary">OVERALL BIAS</Typography>
                  <Typography variant="h4" fontWeight={900} color={fno?.sentiment === 'BULLISH' ? '#10b981' : '#ef4444'}>
                    {fno?.sentiment || 'NEUTRAL'}
                  </Typography>
               </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* AI Synthesis Teaser */}
        <Grid item xs={12} md={6}>
           <Paper sx={{ p: 3, bgcolor: alpha('#7c3aed', 0.05), border: '1px solid rgba(124, 58, 237, 0.2)' }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                 <Brain size={20} color="#7c3aed" />
                 <Typography variant="h6" fontWeight={800}>AI INTELLIGENCE SYNTHESIS</Typography>
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Decision provenance is now active. Every signal generated by Strategy V2.2 is now context-enriched with multi-tier intelligence snapshots.
              </Typography>
              <Chip label="PROVENANCE_ID ACTIVE" size="small" sx={{ fontWeight: 900 }} />
           </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
