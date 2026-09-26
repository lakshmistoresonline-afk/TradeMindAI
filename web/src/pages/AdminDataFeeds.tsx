import { useEffect } from 'react';
import { Box, Typography, Paper, Grid, Stack, Button, alpha, LinearProgress, Chip, Divider } from '@mui/material';
import { Database, RefreshCw, AlertTriangle } from 'lucide-react';
import { getDataHealth } from '../api/client';

export default function AdminDataFeeds() {
  useEffect(() => {
    getDataHealth().catch(console.error);
  }, []);

  return (
    <Box sx={{ pb: { xs: 14, md: 10 }, maxWidth: 1200, mx: 'auto', p: { xs: 2, sm: 4 }, color: 'white', boxSizing: 'border-box' }}>
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
           <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>DATA PIPELINES</Typography>
           <Typography variant="caption" sx={{ color: '#a855f7', fontWeight: 800, letterSpacing: 1.5 }}>
              INSTITUTIONAL INGESTION & MARKET DATA HEALTH
           </Typography>
        </Box>
        <Button variant="contained" color="secondary" startIcon={<RefreshCw size={18} />} sx={{ fontWeight: 950, bgcolor: '#7C3AED', '&:hover': { bgcolor: '#6d28d9' } }}>FORCE PIPELINE SYNC</Button>
      </Box>

      <Grid container spacing={4}>
         <Grid item xs={12} md={8}>
            <Paper sx={{ p: 4, bgcolor: 'rgba(15, 23, 42, 0.85)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2 }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 950, mb: 4, letterSpacing: 1 }}>DATA PROVIDER STATUS</Typography>
               <Stack spacing={3.5}>
                  <ProviderRow name="YFinance Canonical Feed" status="ONLINE" latency="240ms" lastSync="2m ago" />
                  <ProviderRow name="Groww Institutional Feed" status="STANDBY" latency="--" lastSync="18h ago" />
                  <ProviderRow name="Neon PostgreSQL Master" status="HEALTHY" latency="45ms" lastSync="Active" />
                  <ProviderRow name="Firestore Shadow Mirror" status="SYNCED" latency="12ms" lastSync="Active" />
               </Stack>
            </Paper>
         </Grid>

         <Grid item xs={12} md={4}>
            <Paper sx={{ p: 4, bgcolor: 'rgba(15, 23, 42, 0.85)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2 }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 950, mb: 4, letterSpacing: 1 }}>INGESTION HEALTH</Typography>
               <Box sx={{ mb: 4 }}>
                  <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 900, mb: 1, display: 'block' }}>NIFTY-200 UNIVERSE SYNC</Typography>
                  <LinearProgress variant="determinate" value={100} color="success" sx={{ height: 6, borderRadius: 3 }} />
                  <Typography variant="caption" sx={{ mt: 1, display: 'block', fontWeight: 950, fontFamily: 'JetBrains Mono, monospace' }}>200 / 200 CONSTITUENTS</Typography>
               </Box>
               <Box sx={{ mb: 4 }}>
                  <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 900, mb: 1, display: 'block' }}>MISSING INTERVALS</Typography>
                  <LinearProgress variant="determinate" value={0} color="success" sx={{ height: 6, borderRadius: 3 }} />
                  <Typography variant="caption" sx={{ mt: 1, display: 'block', fontWeight: 950, color: '#10b981', fontFamily: 'JetBrains Mono, monospace' }}>0 SYMBOLS (100% COVERAGE)</Typography>
               </Box>
               <Divider sx={{ my: 3, opacity: 0.08 }} />
               <Box sx={{ p: 2, bgcolor: alpha('#10b981', 0.08), borderRadius: 1.5, border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                  <Stack direction="row" spacing={1.5} alignItems="center">
                     <AlertTriangle size={18} color="#10b981" />
                     <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 900 }}>Pipeline operating within nominal parameters.</Typography>
                  </Stack>
               </Box>
            </Paper>
         </Grid>
      </Grid>
    </Box>
  );
}

function ProviderRow({ name, status, latency, lastSync }: any) {
    const isOnline = status === 'ONLINE' || status === 'HEALTHY' || status === 'SYNCED';
    return (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Stack direction="row" spacing={2} alignItems="center">
                <Database size={20} color={isOnline ? '#10b981' : '#64748b'} />
                <Box>
                    <Typography variant="body2" sx={{ fontWeight: 950 }}>{name}</Typography>
                    <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 600 }}>Last Sync: {lastSync}</Typography>
                </Box>
            </Stack>
            <Stack direction="row" spacing={3} alignItems="center">
                <Typography variant="caption" sx={{ fontFamily: 'JetBrains Mono, monospace', color: '#64748b', fontWeight: 800 }}>{latency}</Typography>
                <Chip label={status} size="small" sx={{ fontWeight: 950, fontSize: '0.6rem', bgcolor: alpha(isOnline ? '#10b981' : '#64748b', 0.12), color: isOnline ? '#10b981' : '#64748b' }} />
            </Stack>
        </Box>
    );
}
