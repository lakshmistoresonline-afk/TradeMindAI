import { useEffect } from 'react';
import { Box, Typography, Paper, Grid, Stack, Button, alpha, LinearProgress, Chip, Divider } from '@mui/material';
import { Database, RefreshCw, AlertTriangle } from 'lucide-react';
import { getDataHealth } from '../api/client';

export default function AdminDataFeeds() {
  useEffect(() => {
    getDataHealth().catch(console.error);
  }, []);

  return (
    <Box sx={{ pb: 10, maxWidth: 1200, mx: 'auto', p: 4, color: 'white' }}>
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
           <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>DATA FEEDS</Typography>
           <Typography variant="caption" sx={{ color: 'secondary.main', fontWeight: 800, letterSpacing: 1.5 }}>
              INSTITUTIONAL INGESTION & PIPELINE MONITOR
           </Typography>
        </Box>
        <Button variant="contained" color="secondary" startIcon={<RefreshCw size={18} />} sx={{ fontWeight: 950 }}>FORCE GLOBAL SYNC</Button>
      </Box>

      <Grid container spacing={4}>
         <Grid item xs={12} md={8}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4 }}>PROVIDER STATUS</Typography>
               <Stack spacing={4}>
                  <ProviderRow name="YFinance Canonical" status="ONLINE" latency="240ms" lastSync="2m ago" />
                  <ProviderRow name="Groww Institutional" status="STANDBY" latency="--" lastSync="18h ago" />
                  <ProviderRow name="Neon PostgreSQL" status="HEALTHY" latency="45ms" lastSync="Active" />
                  <ProviderRow name="Firestore Mirror" status="SYNCED" latency="12ms" lastSync="Active" />
               </Stack>
            </Paper>
         </Grid>

         <Grid item xs={12} md={4}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4 }}>INGESTION HEALTH</Typography>
               <Box sx={{ mb: 4 }}>
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, mb: 1, display: 'block' }}>UNIVERSE SYNC</Typography>
                  <LinearProgress variant="determinate" value={98} color="success" sx={{ height: 6, borderRadius: 3 }} />
                  <Typography variant="caption" sx={{ mt: 1, display: 'block', fontWeight: 900 }}>202 / 202 CONSTITUENTS</Typography>
               </Box>
               <Box sx={{ mb: 4 }}>
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, mb: 1, display: 'block' }}>MISSING INTERVALS</Typography>
                  <LinearProgress variant="determinate" value={2} color="error" sx={{ height: 6, borderRadius: 3 }} />
                  <Typography variant="caption" sx={{ mt: 1, display: 'block', fontWeight: 900 }}>4 SYMBOLS (DATA LIMITED)</Typography>
               </Box>
               <Divider sx={{ my: 3, opacity: 0.05 }} />
               <Box sx={{ p: 2, bgcolor: alpha('#f59e0b', 0.05), borderRadius: 1, border: '1px solid rgba(245, 158, 11, 0.1)' }}>
                  <Stack direction="row" spacing={2} alignItems="center">
                     <AlertTriangle size={20} color="#f59e0b" />
                     <Typography variant="caption" sx={{ color: '#f59e0b', fontWeight: 800 }}>Warning: NSE Gap detection active for 12 symbols.</Typography>
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
                <Database size={20} color={isOnline ? '#10b981' : 'slategray'} />
                <Box>
                    <Typography variant="body2" sx={{ fontWeight: 900 }}>{name}</Typography>
                    <Typography variant="caption" sx={{ color: 'slategray' }}>Last Sync: {lastSync}</Typography>
                </Box>
            </Stack>
            <Stack direction="row" spacing={3} alignItems="center">
                <Typography variant="caption" sx={{ fontFamily: 'JetBrains Mono', color: 'slategray' }}>{latency}</Typography>
                <Chip label={status} size="small" sx={{ fontWeight: 950, fontSize: '0.6rem', bgcolor: alpha(isOnline ? '#10b981' : 'slategray', 0.1), color: isOnline ? '#10b981' : 'slategray' }} />
            </Stack>
        </Box>
    );
}
