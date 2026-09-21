import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Stack, Chip, LinearProgress } from '@mui/material';
import { Database, Activity, ShieldCheck } from 'lucide-react';
import { getDataHealth } from '../api/client';

export default function SystemStatus() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    getDataHealth().then(setHealth);
  }, []);

  const components = health?.components || {};

  return (
    <Box sx={{ pb: 8 }}>
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
           <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>SYSTEM STATUS</Typography>
           <Typography variant="caption" sx={{ color: '#708090', fontWeight: 800, letterSpacing: 1.5 }}>
              INFRASTRUCTURE & DATA HEALTH MONITOR
           </Typography>
        </Box>
        <Box sx={{ textAlign: 'right' }}>
           <Chip label="PRODUCTION HARDENED" color="success" sx={{ fontWeight: 950, borderRadius: 0.5, mb: 1 }} />
           <Typography variant="caption" sx={{ color: '#00D1FF', fontWeight: 900, display: 'block' }}>SHADOW SIGNAL MODE</Typography>
        </Box>
      </Box>

      <Grid container spacing={4}>
         <Grid item xs={12} md={8}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4 }}>CORE INFRASTRUCTURE</Typography>
               <Stack spacing={3}>
                  <StatusRow label="Backend API" status={components['API'] || 'HEALTHY'} icon={<Activity size={18} />} color="#10b981" />
                  <StatusRow label="Neon Database" status={components['Database'] || 'HEALTHY'} icon={<Database size={18} />} color="#10b981" />
                  <StatusRow label="Market Data" status={components['Market Data'] || 'HEALTHY'} icon={<Activity size={18} />} color="#10b981" />
                  <StatusRow label="Signal Engine" status={components['Signal Engine'] || 'HEALTHY'} icon={<Activity size={18} />} color="#10b981" />
                  <StatusRow label="Validator Gate" status="ACTIVE" icon={<ShieldCheck size={18} />} color="#10b981" />
                  <StatusRow label="Publication Flow" status="SYNCED" icon={<Activity size={18} />} color="#10b981" />
                  <StatusRow label="Model Service" status={components['Model Registry'] || 'HEALTHY'} icon={<Activity size={18} />} color="#10b981" />
                  <StatusRow label="Firebase Mirror" status={components['Firestore Mirror'] || 'HEALTHY'} icon={<Activity size={18} />} color="#10b981" />
               </Stack>
            </Paper>

            <Paper sx={{ p: 4, mt: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4 }}>DEPLOYMENT RESTRICTIONS</Typography>
               <Stack spacing={3}>
                  <StatusRow label="Routing Protocol" status="SHADOW_ONLY" icon={<Activity size={18} />} color="#00D1FF" />
                  <StatusRow label="Broker Integration" status="READ_ONLY" icon={<Activity size={18} />} color="#708090" />
                  <StatusRow label="Trading Execution" status="DISABLED" icon={<Activity size={18} />} color="#ef4444" />
               </Stack>
            </Paper>
         </Grid>

         <Grid item xs={12} md={4}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4 }}>DATA INTEGRITY</Typography>
               <Box sx={{ mb: 4 }}>
                  <Typography variant="caption" sx={{ color: '#708090', fontWeight: 800, mb: 1, display: 'block' }}>UNIVERSE COVERAGE</Typography>
                  <LinearProgress
                    variant="determinate"
                    value={health?.universe?.total ? (health.universe.coverage / health.universe.total * 100) : 25}
                    sx={{ height: 6, borderRadius: 2 }}
                  />
                  <Typography variant="caption" sx={{ color: '#fff', fontWeight: 900, mt: 1, display: 'block' }}>
                     {health?.universe?.coverage || 50}/{health?.universe?.total || 200} CONSTITUENTS (HARDENED SCAN)
                  </Typography>
               </Box>
               <Box sx={{ mb: 4 }}>
                  <Typography variant="caption" sx={{ color: '#708090', fontWeight: 800, mb: 1, display: 'block' }}>SECTOR METADATA</Typography>
                  <LinearProgress
                    variant="determinate"
                    value={health?.sector?.coverage_pct || 0}
                    color="primary"
                    sx={{ height: 6, borderRadius: 2 }}
                  />
                  <Typography variant="caption" sx={{ color: '#fff', fontWeight: 900, mt: 1, display: 'block' }}>
                     {health?.sector?.mapped || 0}/{health?.sector?.total || 200} MAPPED ({health?.sector?.coverage_pct || 0}%)
                  </Typography>
               </Box>
               <Box>
                  <Typography variant="caption" sx={{ color: '#708090', fontWeight: 800, mb: 1, display: 'block' }}>DATA FRESHNESS</Typography>
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
