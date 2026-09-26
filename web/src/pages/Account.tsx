import { Box, Typography, Paper, Grid, Stack, Button, Divider, alpha, TextField } from '@mui/material';
import { CreditCard, User, Zap, Send, ShieldCheck, Copy, Check } from 'lucide-react';
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
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    getUserReferrals()
      .then((data: any) => {
        setReferrals(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        console.warn("User referrals notice:", err);
        setReferrals([]);
      });
  }, []);

  const handleCopyCode = () => {
    const code = `TM-${user?.uid?.substring(0, 6).toUpperCase() || 'MEMBER'}`;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSendReferral = async () => {
    if (!refEmail) return;
    setLoading(true);
    try {
        await new Promise(resolve => setTimeout(resolve, 800));
        const currentList = Array.isArray(referrals) ? referrals : [];
        setReferrals([...currentList, { id: Date.now(), referred_email: refEmail, status: 'SENT', reward_earned: 0 }]);
        setRefEmail('');
    } finally {
        setLoading(false);
    }
  };

  return (
    <Box sx={{ pb: { xs: 14, md: 10 }, width: '100%', maxWidth: 1280, mx: 'auto', px: { xs: 2, sm: 4, lg: 6 }, pt: 4, color: 'white', boxSizing: 'border-box' }}>
      <Box sx={{ mb: 5 }}>
        <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>ACCOUNT & REFERRALS</Typography>
        <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 800, letterSpacing: 1.5 }}>
           MANAGE YOUR INSTITUTIONAL TERMINAL ACCESS & REWARDS
        </Typography>
      </Box>

      <Grid container spacing={4}>
         {/* 1. Profile Overview */}
         <Grid item xs={12} md={6}>
            <Paper sx={{ p: 4, bgcolor: 'rgba(15, 23, 42, 0.85)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2 }}>
               <Stack direction="row" spacing={2.5} alignItems="center" mb={3}>
                  <Box sx={{ width: 56, height: 56, bgcolor: '#7C3AED', borderRadius: 2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                     <User size={28} color="white" />
                  </Box>
                  <Box>
                     <Typography variant="h6" sx={{ fontWeight: 950 }}>{user?.email || 'TradeMind User'}</Typography>
                     <Typography variant="caption" sx={{ color: '#00D1FF', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.2 }}>
                        <ShieldCheck size={12} /> Institutional Terminal Member
                     </Typography>
                  </Box>
               </Stack>
               <Divider sx={{ opacity: 0.08, mb: 3 }} />
               <Stack spacing={2}>
                  <DetailItem label="Status" val="Active" color="#10b981" />
                  <DetailItem label="Market Region" val="India (NSE Spot & F&O)" />
                  <DetailItem label="Terminal UID" val={user?.uid?.substring(0, 16)} isMono />
               </Stack>
            </Paper>
         </Grid>

         {/* 2. Subscription Details */}
         <Grid item xs={12} md={6}>
            <Paper sx={{ p: 4, bgcolor: 'rgba(15, 23, 42, 0.85)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2, position: 'relative', overflow: 'hidden' }}>
               <Box sx={{ position: 'absolute', top: -10, right: -10, opacity: 0.04 }}><Zap size={140} color="#00D1FF" /></Box>
               <Typography variant="caption" sx={{ fontWeight: 950, color: '#64748b', mb: 1, display: 'block', letterSpacing: 1 }}>CURRENT SUBSCRIPTION TIER</Typography>
               <Typography variant="h3" sx={{ fontWeight: 950, color: '#00D1FF', mb: 0.5 }}>FREE TIER</Typography>
               <Typography variant="body2" sx={{ color: '#94a3b8', fontWeight: 600, mb: 3 }}>Standard market research access active.</Typography>

               <Button
                  fullWidth
                  variant="contained"
                  onClick={() => navigate('/pricing')}
                  startIcon={<Zap size={18} />}
                  sx={{ py: 1.5, fontWeight: 950, bgcolor: '#00D1FF', color: '#000', '&:hover': { bgcolor: '#38bdf8' } }}
               >
                  UPGRADE TO PRO TERMINAL →
               </Button>
            </Paper>
         </Grid>

         {/* 3. Refer & Earn Box */}
         <Grid item xs={12}>
            <Paper sx={{ p: 4, bgcolor: alpha('#7C3AED', 0.03), border: '1px solid rgba(124, 58, 237, 0.2)', borderRadius: 2 }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 950, color: '#a855f7', mb: 2, letterSpacing: 1 }}>REFERRAL CODE PROGRAM</Typography>
               <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                     <Box sx={{ p: 2, bgcolor: 'rgba(2, 6, 23, 0.5)', borderRadius: 1.5, border: '1px solid rgba(255,255,255,0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="body2" sx={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 950, letterSpacing: 1, color: '#00D1FF' }}>
                           TM-{user?.uid?.substring(0, 6).toUpperCase() || 'MEMBER'}
                        </Typography>
                        <Button size="small" onClick={handleCopyCode} startIcon={copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />} sx={{ color: copied ? '#10b981' : '#a855f7', fontWeight: 900 }}>
                           {copied ? 'COPIED' : 'COPY CODE'}
                        </Button>
                     </Box>
                     <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block', lineHeight: 1.5 }}>
                        Share your referral link with fellow traders. Receive a 15% credit on their first subscription month.
                     </Typography>
                  </Grid>

                  <Grid item xs={12} md={6}>
                     <Stack direction="row" spacing={1} mb={2}>
                        <TextField
                          fullWidth
                          size="small"
                          placeholder="Enter invitee email address"
                          value={refEmail}
                          onChange={(e) => setRefEmail(e.target.value)}
                          sx={{ bgcolor: 'rgba(2, 6, 23, 0.5)' }}
                        />
                        <Button variant="contained" color="secondary" onClick={handleSendReferral} sx={{ px: 3, fontWeight: 950 }}><Send size={16} /></Button>
                     </Stack>

                     <Grid container spacing={2} sx={{ pt: 1 }}>
                        <Grid item xs={6}>
                           <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 900, display: 'block' }}>TOTAL REFERRED</Typography>
                           <Typography variant="h5" sx={{ fontWeight: 950, fontFamily: 'JetBrains Mono, monospace' }}>{Array.isArray(referrals) ? referrals.length : 0}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                           <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 900, display: 'block' }}>REWARDS EARNED</Typography>
                           <Typography variant="h5" sx={{ fontWeight: 950, color: '#10b981', fontFamily: 'JetBrains Mono, monospace' }}>₹{Array.isArray(referrals) ? referrals.reduce((sum, r) => sum + (r.reward_earned || 0), 0) : 0}</Typography>
                        </Grid>
                     </Grid>
                  </Grid>
               </Grid>
            </Paper>
         </Grid>

         {/* 4. Billing History & Referrals */}
         <Grid item xs={12}>
            <Paper sx={{ p: 4, bgcolor: 'rgba(15, 23, 42, 0.85)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2 }}>
               <Stack direction="row" spacing={1.5} alignItems="center" mb={3}>
                  <CreditCard size={20} color="#00D1FF" />
                  <Typography variant="subtitle2" sx={{ fontWeight: 950, letterSpacing: 1 }}>TRANSACTION LEDGER</Typography>
               </Stack>

               {Array.isArray(referrals) && referrals.length > 0 && (
                  <Box sx={{ mb: 4 }}>
                     <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 950, mb: 2, display: 'block' }}>REFERRAL ACTIVITY</Typography>
                     {referrals.map((r, i) => (
                        <Box key={i} sx={{ py: 1.5, display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                           <Typography variant="caption" sx={{ fontWeight: 800 }}>{r.referred_email}</Typography>
                           <Stack direction="row" spacing={2}>
                              <Typography variant="caption" sx={{ color: r.status === 'CONVERTED' ? '#10b981' : '#64748b', fontWeight: 900 }}>{r.status}</Typography>
                              {r.reward_earned > 0 && <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 900 }}>+₹{r.reward_earned}</Typography>}
                           </Stack>
                        </Box>
                     ))}
                  </Box>
               )}

               <Box sx={{ py: 5, textAlign: 'center', bgcolor: 'rgba(2, 6, 23, 0.4)', borderRadius: 1.5, border: '1px dashed rgba(255,255,255,0.08)' }}>
                  <Typography variant="body2" sx={{ color: '#64748b', fontWeight: 700 }}>NO RECENT BILLING TRANSACTIONS FOUND</Typography>
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
            <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 800 }}>{label}</Typography>
            <Typography variant="caption" sx={{ color, fontWeight: 950, fontFamily: isMono ? 'JetBrains Mono, monospace' : 'inherit' }}>{val}</Typography>
        </Box>
    );
}
