import { Box, Typography, Paper, Grid, Stack, Button, Divider } from '@mui/material';
import { CreditCard, User, Zap } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

export default function Account() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <Box sx={{ pb: 10, maxWidth: 1000, mx: 'auto', p: 4, color: 'white' }}>
      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>ACCOUNT SETTINGS</Typography>
        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
           MANAGE YOUR INSTITUTIONAL TERMINAL ACCESS
        </Typography>
      </Box>

      <Grid container spacing={4}>
         {/* 1. Profile Overview */}
         <Grid item xs={12} md={6}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Stack direction="row" spacing={3} alignItems="center" mb={4}>
                  <Box sx={{ width: 60, height: 60, bgcolor: 'secondary.main', borderRadius: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                     <User size={32} color="white" />
                  </Box>
                  <Box>
                     <Typography variant="h6" sx={{ fontWeight: 900 }}>{user?.email}</Typography>
                     <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>MEMBER SINCE SEP 2026</Typography>
                  </Box>
               </Stack>
               <Divider sx={{ opacity: 0.05, mb: 4 }} />
               <Stack spacing={2}>
                  <DetailItem label="Status" val="Active" color="#10b981" />
                  <DetailItem label="Region" val="India (NSE)" />
                  <DetailItem label="Terminal UID" val={user?.uid?.substring(0, 12)} isMono />
               </Stack>
            </Paper>
         </Grid>

         {/* 2. Subscription Details */}
         <Grid item xs={12} md={6}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', position: 'relative', overflow: 'hidden' }}>
               <Box sx={{ position: 'absolute', top: 10, right: 10, opacity: 0.05 }}><Zap size={120} color="#00D1FF" /></Box>
               <Typography variant="subtitle2" sx={{ fontWeight: 950, color: 'slategray', mb: 3, letterSpacing: 1 }}>CURRENT PLAN</Typography>
               <Typography variant="h3" sx={{ fontWeight: 950, color: '#00D1FF', mb: 1 }}>FREE TIER</Typography>
               <Typography variant="body2" sx={{ color: 'slategray', fontWeight: 700, mb: 4 }}>Standard research access enabled.</Typography>

               <Button
                  fullWidth
                  variant="contained"
                  onClick={() => navigate('/pricing')}
                  startIcon={<Zap size={18} />}
                  sx={{ py: 1.5, fontWeight: 950 }}
               >
                  UPGRADE TO PRO
               </Button>
            </Paper>
         </Grid>

         {/* 3. Billing History */}
         <Grid item xs={12}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Stack direction="row" spacing={1.5} alignItems="center" mb={4}>
                  <CreditCard size={20} color="#00D1FF" />
                  <Typography variant="subtitle2" sx={{ fontWeight: 950, letterSpacing: 1 }}>BILLING HISTORY</Typography>
               </Stack>
               <Box sx={{ py: 6, textAlign: 'center', bgcolor: 'rgba(255,255,255,0.01)', borderRadius: 1, border: '1px dashed rgba(255,255,255,0.05)' }}>
                  <Typography variant="body2" sx={{ color: 'slategray', fontWeight: 700 }}>NO RECENT TRANSACTIONS FOUND</Typography>
               </Box>
            </Paper>
         </Grid>
      </Grid>
    </Box>
  );
}

function DetailItem({ label, val, color = '#fff', isMono = false }: any) {
    return (
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>{label}</Typography>
            <Typography variant="caption" sx={{ color, fontWeight: 950, fontFamily: isMono ? 'JetBrains Mono' : 'inherit' }}>{val}</Typography>
        </Box>
    );
}
