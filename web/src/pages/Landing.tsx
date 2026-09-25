import { Box, Typography, Button, Container, Grid, Stack, Divider, Chip, Paper } from '@mui/material';
import { ShieldCheck, Zap, Search, Clock, ArrowRight, TrendingUp, Cpu } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <Box sx={{ bgcolor: '#020617', color: 'white', minHeight: '100vh', overflowX: 'hidden' }}>
      {/* Top Accent Line */}
      <Box sx={{ height: 2, background: 'linear-gradient(90deg, #00D1FF, #7C3AED, #10b981)' }} />

      {/* 1. HERO SECTION */}
      <Box sx={{
        pt: { xs: 10, md: 16 },
        pb: { xs: 12, md: 20 },
        background: 'radial-gradient(circle at 50% 0%, rgba(15, 23, 42, 0.9), #020617)',
        textAlign: 'center',
        position: 'relative'
      }}>
        <Container maxWidth="lg">
          <Chip
            icon={<Cpu size={14} color="#00D1FF" />}
            label="STRATEGY V2.3 QUANTITATIVE ENSEMBLE ENGINE"
            size="medium"
            sx={{
              mb: 4,
              px: 1.5,
              py: 0.5,
              fontWeight: 950,
              fontSize: '0.7rem',
              letterSpacing: 1,
              bgcolor: 'rgba(0, 209, 255, 0.08)',
              color: '#00D1FF',
              border: '1px solid rgba(0, 209, 255, 0.25)',
              borderRadius: 2
            }}
          />

          <Typography variant="h1" sx={{
            fontSize: { xs: '2.5rem', md: '4.5rem' },
            fontWeight: 950,
            letterSpacing: -2.5,
            lineHeight: 1.05,
            mb: 3,
            fontFamily: 'JetBrains Mono, monospace'
          }}>
            TRADEMIND AI
          </Typography>

          <Typography variant="h4" sx={{
            fontSize: { xs: '1.25rem', md: '1.75rem' },
            fontWeight: 800,
            color: '#00D1FF',
            letterSpacing: 1,
            mb: 4,
            lineHeight: 1.4
          }}>
            EVIDENCE-DRIVEN SIGNAL INTELLIGENCE FOR NIFTY-200 EQUITIES
          </Typography>

          <Typography variant="body1" sx={{
            fontSize: '1.15rem',
            color: '#94a3b8',
            maxWidth: 780,
            mx: 'auto',
            mb: 6,
            fontWeight: 500,
            lineHeight: 1.8
          }}>
            Identify institutional momentum setups across Indian equities. Understand the machine-learning evidence behind every call, and track each signal with complete forensic auditability.
          </Typography>

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} justifyContent="center">
            <Button
              size="large"
              variant="contained"
              onClick={() => navigate('/login')}
              endIcon={<ArrowRight size={20} />}
              sx={{ px: 6, py: 2, fontSize: '1rem', fontWeight: 950, bgcolor: '#00D1FF', color: '#000', '&:hover': { bgcolor: '#38bdf8' } }}
            >
              LAUNCH TERMINAL
            </Button>
            <Button
              size="large"
              variant="outlined"
              onClick={() => navigate('/performance')}
              sx={{ px: 6, py: 2, fontSize: '1rem', fontWeight: 900, borderColor: 'rgba(255,255,255,0.15)', color: 'white', '&:hover': { borderColor: '#00D1FF', bgcolor: 'rgba(255,255,255,0.02)' } }}
            >
              AUDIT TRACK RECORD
            </Button>
          </Stack>
        </Container>
      </Box>

      {/* 2. CORE PILLARS */}
      <Container maxWidth="lg" sx={{ py: 12 }}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={3}>
            <PillarItem
              icon={<Search size={28} color="#00D1FF" />}
              title="DISCOVER"
              text="Identify institutional momentum breakouts across the NIFTY-200 universe."
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <PillarItem
              icon={<Zap size={28} color="#10b981" />}
              title="UNDERSTAND"
              text="Analyze the machine-learning evidence, ATR risk geometry, and Wyckoff logic behind every signal."
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <PillarItem
              icon={<Clock size={28} color="#a855f7" />}
              title="TRACK"
              text="Monitor signal evolution in real-time from breakout trigger to terminal state."
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <PillarItem
              icon={<ShieldCheck size={28} color="#00D1FF" />}
              title="VERIFY"
              text="Audit our 100% transparent historical signal ledger of observed outcomes."
            />
          </Grid>
        </Grid>
      </Container>

      {/* 3. PRODUCT PHILOSOPHY */}
      <Box sx={{ py: 12, bgcolor: '#070d19', borderTop: '1px solid rgba(255,255,255,0.06)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <Container maxWidth="md" sx={{ textAlign: 'center' }}>
          <Typography variant="h3" sx={{ fontWeight: 950, letterSpacing: -1, mb: 3 }}>
            DON'T JUST GET A SIGNAL.<br/>UNDERSTAND IT.
          </Typography>
          <Typography variant="body1" sx={{ color: '#94a3b8', fontSize: '1.15rem', lineHeight: 1.8, mb: 6, fontWeight: 500 }}>
            TradeMind AI is a professional terminal for auditable signal intelligence.
            Every call is backed by verifiable market data, 15-stage quality gates, and a traceable ML lifecycle.
          </Typography>
          <Divider sx={{ mb: 6, opacity: 0.08 }} />
          <Grid container spacing={4} justifyContent="center">
            <Grid item xs={12} md={4}>
              <Typography variant="h4" sx={{ fontWeight: 950, color: '#10b981', fontFamily: 'JetBrains Mono, monospace', mb: 1 }}>75.0%</Typography>
              <Typography variant="caption" sx={{ fontWeight: 950, letterSpacing: 1, color: 'white', display: 'block' }}>OBSERVED WIN RATE</Typography>
              <Typography variant="caption" sx={{ display: 'block', color: '#64748b', mt: 0.5 }}>Shadow Validation Ledger</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
               <Typography variant="h4" sx={{ fontWeight: 950, color: '#00D1FF', fontFamily: 'JetBrains Mono, monospace', mb: 1 }}>2.78</Typography>
               <Typography variant="caption" sx={{ fontWeight: 950, letterSpacing: 1, color: 'white', display: 'block' }}>PROFIT FACTOR</Typography>
               <Typography variant="caption" sx={{ display: 'block', color: '#64748b', mt: 0.5 }}>Forensic Accuracy Audit</Typography>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* 4. FOOTER */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Grid container spacing={6}>
          <Grid item xs={12} md={6}>
            <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 2 }}>
              <TrendingUp size={24} color="#00D1FF" />
              <Typography variant="h6" sx={{ fontWeight: 950, fontFamily: 'JetBrains Mono, monospace' }}>TRADEMIND AI</Typography>
            </Stack>
            <Typography variant="body2" sx={{ color: '#64748b', maxWidth: 420, mb: 3, fontWeight: 500, lineHeight: 1.6 }}>
              Institutional AI investment operating system for professional equity market research.
            </Typography>
            <Stack direction="row" spacing={3}>
              <Button size="small" onClick={() => navigate('/trust')} sx={{ color: '#94a3b8', fontWeight: 800 }}>TRUST CENTER</Button>
              <Button size="small" onClick={() => navigate('/methodology')} sx={{ color: '#94a3b8', fontWeight: 800 }}>METHODOLOGY</Button>
              <Button size="small" onClick={() => navigate('/pricing')} sx={{ color: '#94a3b8', fontWeight: 800 }}>PRICING</Button>
            </Stack>
          </Grid>
          <Grid item xs={12} md={6} sx={{ textAlign: { md: 'right' } }}>
             <Typography variant="caption" sx={{ color: '#64748b', display: 'block', mb: 2, lineHeight: 1.6 }}>
               TradeMind AI uses quantitative ensemble models to process market information. <br/>
               Model outputs are estimates and not guarantees of future outcomes.
             </Typography>
             <Typography variant="caption" sx={{ color: '#475569', fontWeight: 800, fontFamily: 'JetBrains Mono, monospace' }}>
               © 2026 TRADEMIND AI • STRATEGY V2.3 ENSEMBLE
             </Typography>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}

function PillarItem({ icon, title, text }: any) {
  return (
    <Paper sx={{ p: 3.5, height: '100%', bgcolor: 'rgba(15, 23, 42, 0.85)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2 }}>
      <Box sx={{ mb: 2 }}>{icon}</Box>
      <Typography variant="h6" sx={{ fontWeight: 950, letterSpacing: 1, mb: 1 }}>{title}</Typography>
      <Typography variant="body2" sx={{ color: '#94a3b8', lineHeight: 1.7, fontWeight: 500 }}>{text}</Typography>
    </Paper>
  );
}
