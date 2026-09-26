import { Box, Typography, Paper, Grid, Stack } from '@mui/material';
import { ShieldCheck, Lock, Activity, BarChart2 } from 'lucide-react';

export default function Trust() {
  return (
    <Box sx={{ pb: { xs: 14, md: 10 }, maxWidth: 1000, mx: 'auto', p: { xs: 2, sm: 4 }, color: 'white', boxSizing: 'border-box' }}>
      <Box sx={{ mb: 8, textAlign: 'center' }}>
        <Typography variant="h3" sx={{ fontWeight: 950, letterSpacing: -2, mb: 2 }}>TRUST CENTER</Typography>
        <Typography variant="h6" sx={{ color: '#00D1FF', fontWeight: 800 }}>TRANSPARENCY • TRACEABILITY • ACCOUNTABILITY</Typography>
      </Box>

      <Grid container spacing={4}>
         <Grid item xs={12} md={6}>
            <TrustCard
               icon={<ShieldCheck size={32} color="#10b981" />}
               title="Zero Fabrication Policy"
               text="Every signal shown in TradeMind AI is backed by an authoritative database record. We do not manufacture history or cherry-pick winners. All 50 historical calls are visible in the ledger."
            />
         </Grid>
         <Grid item xs={12} md={6}>
            <TrustCard
               icon={<Lock size={32} color="#00D1FF" />}
               title="Strategy Freeze (V2.2)"
               text="The underlying investment strategy (V2.2) is frozen. All performance metrics are calculated against this immutable baseline to ensure consistency and prevent over-fitting."
            />
         </Grid>
         <Grid item xs={12} md={6}>
            <TrustCard
               icon={<Activity size={32} color="#7C3AED" />}
               title="Shadow Execution"
               text="TradeMind AI operates in a 'Shadow Signal' mode. We monitor live market data and record decisions in real-time, but REAL TRADING is disabled. No broker orders are ever submitted."
            />
         </Grid>
         <Grid item xs={12} md={6}>
            <TrustCard
               icon={<BarChart2 size={32} color="#10b981" />}
               title="Auditable Outcomes"
               text="Every terminal outcome (Target Hit / Stop Loss) is verified against official NSE spot prices. We document all limitations, including same-bar ambiguity and survivorship bias."
            />
         </Grid>
      </Grid>

      <Box sx={{ mt: 10 }}>
         <Typography variant="h5" sx={{ fontWeight: 900, mb: 4 }}>System Reliability</Typography>
         <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
            <Stack spacing={3}>
               <ReliabilityItem label="Data Freshness" status="VERIFIED" text="Active signal prices are refreshed every 5 minutes from institutional providers." />
               <ReliabilityItem label="Identity Integrity" status="VERIFIED" text="100% of signals are traceable from prediction ID to terminal outcome." />
               <ReliabilityItem label="Temporal Soundness" status="VERIFIED" text="Strict 'No Look-Ahead' enforcement ensures models only see data available at the decision timestamp." />
            </Stack>
         </Paper>
      </Box>

      <Box sx={{ mt: 10, p: 4, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, border: '1px dashed rgba(255,255,255,0.1)' }}>
         <Typography variant="caption" sx={{ color: '#708090', fontStyle: 'italic', lineHeight: 1.6, display: 'block' }}>
            TradeMind AI is a research and signal intelligence platform.
            All metrics are derived from observed shadow execution on historical and live market data.
            Investing in equities involves significant risk of loss.
         </Typography>
      </Box>
    </Box>
  );
}

function TrustCard({ icon, title, text }: any) {
    return (
        <Paper sx={{ p: 4, height: '100%', bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
            <Box sx={{ mb: 3 }}>{icon}</Box>
            <Typography variant="h6" sx={{ fontWeight: 900, mb: 2 }}>{title}</Typography>
            <Typography variant="body2" sx={{ color: '#708090', lineHeight: 1.8 }}>{text}</Typography>
        </Paper>
    );
}

function ReliabilityItem({ label, status, text }: any) {
    return (
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 3 }}>
            <Box sx={{ minWidth: 120 }}>
                <Typography variant="caption" sx={{ fontWeight: 950, color: '#00D1FF', display: 'block' }}>{label}</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                    <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: '#10b981' }} />
                    <Typography variant="caption" sx={{ fontWeight: 900, fontSize: '0.6rem', color: '#10b981' }}>{status}</Typography>
                </Box>
            </Box>
            <Typography variant="body2" sx={{ color: '#708090' }}>{text}</Typography>
        </Box>
    );
}
