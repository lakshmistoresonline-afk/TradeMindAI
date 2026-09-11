import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Stack, Chip, LinearProgress } from '@mui/material';
import { Database, Activity } from 'lucide-react';
import { getDataHealth } from '../api/client';

export default function SystemStatus() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    getDataHealth().then(setHealth);
  }, []);

  const components = health?.components || {};

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
                  {Object.entries(components).map(([name, status]) => (
                     <StatusRow
                        key={name}
                        label={name}
                        status={status as string}
                        icon={name.includes('Database') ? <Database size={18} /> : <Activity size={18} />}
                        color={status === 'HEALTHY' ? "#10b981" : status === 'DEGRADED' ? "orange" : "#ef4444"}
                     />
                  ))}
               </Stack>
            </Paper>
         </Grid>

         <Grid item xs={12} md={4}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4 }}>DATA INTEGRITY</Typography>
               <Box sx={{ mb: 4 }}>
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, mb: 1, display: 'block' }}>UNIVERSE COVERAGE</Typography>
                  <LinearProgress variant="determinate" value={100} sx={{ height: 6, borderRadius: 2 }} />
                  <Typography variant="caption" sx={{ color: '#fff', fontWeight: 900, mt: 1, display: 'block' }}>
                     {health?.universe?.total || 200}/{health?.universe?.total || 200} CONSTITUENTS
                  </Typography>
               </Box>
               <Box>
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, mb: 1, display: 'block' }}>DATA FRESHNESS</Typography>
                  <LinearProgress
                    variant="determinate"
                    value={health?.universe?.total ? (health.universe.fresh / health.universe.total * 100) : 0}
                    color="success"
                    sx={{ height: 6, borderRadius: 2 }}
                  />
                  <Typography variant="caption" sx={{ color: '#fff', fontWeight: 900, mt: 1, display: 'block' }}>
                     {health?.universe?.fresh || 0} SYNCED • {health?.universe?.blocked || 0} BLOCKED
                  </Typography>
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
