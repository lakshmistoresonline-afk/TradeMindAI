import { Box, Typography, Paper, Grid, Stack, Button, Divider, alpha, TextField } from '@mui/material';
import { CreditCard, User, Zap, Send } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { getUserReferrals } from '../api/client';
import { useState, useEffect } from 'react';

export default function Account() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [referrals, setReferrals] = useState<any[]>([]);
  const [refEmail, setRefEmail] = useState('');
  const [, setLoading] = useState(false);

  useEffect(() => {
    getUserReferrals().then(setReferrals).catch(console.error);
  }, []);

  const handleSendReferral = async () => {
    if (!refEmail) return;
    setLoading(true);
    try {
        // Mocking API call to user.post("/referrals")
        await new Promise(resolve => setTimeout(resolve, 1000));
        setReferrals([...referrals, { id: Date.now(), referred_email: refEmail, status: 'SENT', reward_earned: 0 }]);
        setRefEmail('');
    } finally {
        setLoading(true);
    }
  };

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

            <Paper sx={{ p: 4, mt: 4, bgcolor: alpha('#7C3AED', 0.03), border: '1px solid rgba(124, 58, 237, 0.1)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 950, color: 'secondary.main', mb: 3, letterSpacing: 1 }}>REFER & EARN</Typography>
               <Box sx={{ p: 2, bgcolor: 'rgba(0,0,0,0.2)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="body2" sx={{ fontFamily: 'JetBrains Mono', fontWeight: 900 }}>TM-{user?.uid?.substring(0, 6).toUpperCase()}</Typography>
                  <Button size="small" sx={{ fontWeight: 800 }}>COPY LINK</Button>
               </Box>

               <Stack direction="row" spacing={1} mb={3}>
                  <TextField
                    fullWidth
                    size="small"
                    placeholder="Friend's Email"
                    value={refEmail}
                    onChange={(e) => setRefEmail(e.target.value)}
                    sx={{ bgcolor: 'rgba(0,0,0,0.2)' }}
                  />
                  <Button variant="contained" color="secondary" onClick={handleSendReferral}><Send size={16} /></Button>
               </Stack>

               <Typography variant="caption" sx={{ color: 'slategray', display: 'block', mb: 3 }}>
                  Refer a friend and receive 15% credit on their first subscription month.
               </Typography>
               <Grid container spacing={2}>
                  <Grid item xs={6}>
                     <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, display: 'block' }}>REFERRED</Typography>
                     <Typography variant="h6" sx={{ fontWeight: 950 }}>{referrals.length}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                     <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, display: 'block' }}>EARNED</Typography>
                     <Typography variant="h6" sx={{ fontWeight: 950, color: '#10b981' }}>₹{referrals.reduce((sum, r) => sum + r.reward_earned, 0)}</Typography>
                  </Grid>
               </Grid>
            </Paper>
         </Grid>

         {/* 3. Billing History & Referrals */}
         <Grid item xs={12}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Stack direction="row" spacing={1.5} alignItems="center" mb={4}>
                  <CreditCard size={20} color="#00D1FF" />
                  <Typography variant="subtitle2" sx={{ fontWeight: 950, letterSpacing: 1 }}>TRANSACTION LEDGER</Typography>
               </Stack>

               {referrals.length > 0 && (
                  <Box sx={{ mb: 6 }}>
                     <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 950, mb: 2, display: 'block' }}>REFERRAL ACTIVITY</Typography>
                     {referrals.map((r, i) => (
                        <Box key={i} sx={{ py: 1.5, display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                           <Typography variant="caption" sx={{ fontWeight: 800 }}>{r.referred_email}</Typography>
                           <Stack direction="row" spacing={2}>
                              <Typography variant="caption" sx={{ color: r.status === 'CONVERTED' ? '#10b981' : 'slategray', fontWeight: 900 }}>{r.status}</Typography>
                              {r.reward_earned > 0 && <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 900 }}>+₹{r.reward_earned}</Typography>}
                           </Stack>
                        </Box>
                     ))}
                  </Box>
               )}

               <Box sx={{ py: 6, textAlign: 'center', bgcolor: 'rgba(255,255,255,0.01)', borderRadius: 1, border: '1px dashed rgba(255,255,255,0.05)' }}>
                  <Typography variant="body2" sx={{ color: 'slategray', fontWeight: 700 }}>NO RECENT BILLING TRANSACTIONS FOUND</Typography>
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
