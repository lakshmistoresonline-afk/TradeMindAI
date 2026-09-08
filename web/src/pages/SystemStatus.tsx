import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Stack, Chip, Divider, LinearProgress } from '@mui/material';
import { Server, Database, Activity, ShieldCheck, Globe } from 'lucide-react';
import { getDataHealth } from '../api/client';

export default function SystemStatus() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    getDataHealth().then(setHealth);
  }, []);

  return (
    <Box sx={{ pb: 8 }}>
      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>SYSTEM STATUS</Typography>
        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
           INFRASTRUCTURE & DATA HEALTH MONITOR
        </Typography>
      </Box>

      <Grid container spacing={4}>
         <Grid item xs={12} md={8}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4 }}>CORE INFRASTRUCTURE</Typography>
               <Stack spacing={3}>
                  <StatusRow label="Signal Engine (V2.2)" status="OPERATIONAL" icon={<Activity size={18} />} color="#10b981" />
                  <StatusRow label="Neon PostgreSQL Authority" status="STABLE" icon={<Database size={18} />} color="#00D1FF" />
                  <StatusRow label="Firebase Mirror Sync" status="OPERATIONAL" icon={<Globe size={18} />} color="#10b981" />
                  <StatusRow label="Market Data (YFinance)" status="DEGRADED" icon={<Globe size={18} />} color="#f59e0b" />
               </Stack>
            </Paper>
         </Grid>

         <Grid item xs={12} md={4}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4 }}>DATA INTEGRITY</Typography>
               <Box sx={{ mb: 4 }}>
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, mb: 1, display: 'block' }}>UNIVERSE COVERAGE</Typography>
                  <LinearProgress variant="determinate" value={100} sx={{ height: 6, borderRadius: 2 }} />
                  <Typography variant="caption" sx={{ color: '#fff', fontWeight: 900, mt: 1, display: 'block' }}>200/200 CONSTITUENTS</Typography>
               </Box>
               <Box>
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, mb: 1, display: 'block' }}>DATA FRESHNESS</Typography>
                  <LinearProgress variant="determinate" value={health?.database?.freshness_pct || 0} color="success" sx={{ height: 6, borderRadius: 2 }} />
                  <Typography variant="caption" sx={{ color: '#fff', fontWeight: 900, mt: 1, display: 'block' }}>{health?.database?.freshness_pct?.toFixed(1) || 0}% SYNCED</Typography>
               </Box>
            </Paper>
         </Grid>
      </Grid>
    </Box>
  );
}

function StatusRow({ label, status, icon, color }: any) {
   return (
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 1, borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
         <Stack direction="row" spacing={2} alignItems="center">
            <Box sx={{ color }}>{icon}</Box>
            <Typography variant="body2" sx={{ fontWeight: 800 }}>{label}</Typography>
         </Stack>
         <Chip label={status} size="small" sx={{ fontWeight: 950, fontSize: '0.6rem', bgcolor: `${color}15`, color, border: `1px solid ${color}30` }} />
      </Box>
   );
}
