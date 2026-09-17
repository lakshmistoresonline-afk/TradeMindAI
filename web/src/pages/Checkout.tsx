import { useState } from 'react';
import { Box, Typography, Paper, Grid, Stack, Button, Divider, alpha, CircularProgress } from '@mui/material';
import { ShieldCheck, CreditCard, CheckCircle2 } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';

export default function Checkout() {
  const { planId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const plan = planId?.toUpperCase() || 'PRO';
  const price = plan === 'ALPHA' ? '7,999' : '2,499';

  const handlePayment = async () => {
    setLoading(true);
    // Simulate Payment Provider Redirect & Webhook Delay
    setTimeout(() => {
      setLoading(false);
      setSuccess(true);
    }, 2000);
  };

  if (success) {
    return (
      <Box sx={{ py: 15, textAlign: 'center', maxWidth: 600, mx: 'auto' }}>
        <CheckCircle2 size={80} color="#10b981" style={{ margin: '0 auto 24px' }} />
        <Typography variant="h3" sx={{ fontWeight: 950, mb: 2 }}>PAYMENT SUCCESSFUL</Typography>
        <Typography variant="body1" sx={{ color: 'slategray', mb: 6 }}>
          Your institutional access to {plan} intelligence is now active.
          The Signal Ledger has been updated with your entitlements.
        </Typography>
        <Button variant="contained" size="large" onClick={() => navigate('/dashboard')} fullWidth sx={{ py: 2, fontWeight: 950 }}>
          GO TO TERMINAL
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ pb: 10, maxWidth: 1000, mx: 'auto', p: 4, color: 'white' }}>
      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>CHECKOUT</Typography>
        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
           FINALIZE YOUR INSTITUTIONAL SUBSCRIPTION
        </Typography>
      </Box>

      <Grid container spacing={4}>
         <Grid item xs={12} md={7}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 950, mb: 4, letterSpacing: 1 }}>PAYMENT METHOD</Typography>
               <Stack spacing={2}>
                  <Box sx={{ p: 3, border: '2px solid #00D1FF', borderRadius: 1, bgcolor: alpha('#00D1FF', 0.05), display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                     <Stack direction="row" spacing={2} alignItems="center">
                        <CreditCard size={24} color="#00D1FF" />
                        <Box>
                           <Typography variant="body2" sx={{ fontWeight: 900 }}>UPI / CARD / NETBANKING</Typography>
                           <Typography variant="caption" sx={{ color: 'slategray' }}>Secure Institutional Gateway</Typography>
                        </Box>
                     </Stack>
                     <CheckCircle2 size={20} color="#00D1FF" />
                  </Box>
               </Stack>
               <Divider sx={{ my: 4, opacity: 0.05 }} />
               <Typography variant="caption" sx={{ color: 'slategray', display: 'block', mb: 4 }}>
                  By clicking "Complete Payment", you agree to the TradeMind AI Terms of Service and Subscription Policy.
                  Subscription renews automatically at the end of the period.
               </Typography>
               <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={loading}
                  onClick={handlePayment}
                  sx={{ py: 2, fontWeight: 950 }}
               >
                  {loading ? <CircularProgress size={24} color="inherit" /> : `COMPLETE PAYMENT (₹${price})`}
               </Button>
            </Paper>
         </Grid>

         <Grid item xs={12} md={5}>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="subtitle2" sx={{ fontWeight: 950, mb: 4, letterSpacing: 1 }}>ORDER SUMMARY</Typography>
               <Stack spacing={3}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                     <Typography variant="body2" sx={{ color: 'slategray', fontWeight: 700 }}>Plan</Typography>
                     <Typography variant="body2" sx={{ fontWeight: 900 }}>TRADEMIND {plan}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                     <Typography variant="body2" sx={{ color: 'slategray', fontWeight: 700 }}>Period</Typography>
                     <Typography variant="body2" sx={{ fontWeight: 900 }}>Monthly</Typography>
                  </Box>
                  <Divider sx={{ opacity: 0.05 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                     <Typography variant="h6" sx={{ fontWeight: 950 }}>TOTAL</Typography>
                     <Typography variant="h6" sx={{ fontWeight: 950, color: 'primary.main' }}>₹{price}</Typography>
                  </Box>
               </Stack>

               <Box sx={{ mt: 6, p: 2, bgcolor: 'rgba(16, 185, 129, 0.05)', borderRadius: 1, border: '1px solid rgba(16, 185, 129, 0.1)' }}>
                  <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 900, display: 'flex', alignItems: 'center', gap: 1 }}>
                     <ShieldCheck size={14} /> ENCRYPTED TRANSACTION
                  </Typography>
               </Box>
            </Paper>
         </Grid>
      </Grid>
    </Box>
  );
}
