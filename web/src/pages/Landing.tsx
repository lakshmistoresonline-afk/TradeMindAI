import { Box, Typography, Button, Container, Grid, Stack, Divider } from '@mui/material';
import { ShieldCheck, Zap, Search, Clock, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <Box sx={{ bgcolor: '#020617', color: 'white', minHeight: '100vh', overflowX: 'hidden' }}>
      {/* 1. HERO SECTION */}
      <Box sx={{
        pt: { xs: 10, md: 20 },
        pb: { xs: 15, md: 25 },
        background: 'radial-gradient(circle at 50% 0%, #0f172a, #020617)',
        textAlign: 'center'
      }}>
        <Container maxWidth="lg">
          <Typography variant="h1" sx={{
            fontSize: { xs: '2.5rem', md: '5rem' },
            fontWeight: 950,
            letterSpacing: -3,
            lineHeight: 1,
            mb: 3
          }}>
            TRADEMIND AI
          </Typography>
          <Typography variant="h4" sx={{
            fontSize: { xs: '1.25rem', md: '2rem' },
            fontWeight: 700,
            color: '#00D1FF',
            letterSpacing: 2,
            mb: 4
          }}>
            EVIDENCE-DRIVEN SIGNAL INTELLIGENCE<br/>FOR INDIAN EQUITIES
          </Typography>
          <Typography variant="body1" sx={{
            fontSize: '1.25rem',
            color: 'slategray',
            maxWidth: 800,
            mx: 'auto',
            mb: 6,
            fontWeight: 500,
            lineHeight: 1.8
          }}>
            "Discover structured market opportunities, understand the evidence behind every signal, and follow each call from creation to outcome."
          </Typography>

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} justifyContent="center">
            <Button
              size="large"
              variant="contained"
              onClick={() => navigate('/login')}
              endIcon={<ArrowRight size={20} />}
              sx={{ px: 6, py: 2, fontSize: '1rem', fontWeight: 950 }}
            >
              EXPLORE TRADEMIND
            </Button>
            <Button
              size="large"
              variant="outlined"
              onClick={() => navigate('/how-it-works')}
              sx={{ px: 6, py: 2, fontSize: '1rem', fontWeight: 800, borderColor: 'rgba(255,255,255,0.1)', color: 'white' }}
            >
              SEE HOW IT WORKS
            </Button>
          </Stack>
        </Container>
      </Box>

      {/* 2. CORE PILLARS */}
      <Container maxWidth="lg" sx={{ py: 15 }}>
        <Grid container spacing={6}>
          <Grid item xs={12} md={3}>
            <PillarItem
              icon={<Search size={32} color="#00D1FF" />}
              title="DISCOVER"
              text="Identify institutional-grade momentum setups across the NIFTY-200 universe."
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <PillarItem
              icon={<Zap size={32} color="#10b981" />}
              title="UNDERSTAND"
              text="Analyze the machine-learning evidence and structural logic behind every signal."
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <PillarItem
              icon={<Clock size={32} color="#7C3AED" />}
              title="TRACK"
              text="Monitor signal evolution in real-time from publication to terminal state."
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <PillarItem
              icon={<ShieldCheck size={32} color="#00D1FF" />}
              title="VERIFY"
              text="Audit our 100% transparent historical ledger of observed outcomes."
            />
          </Grid>
        </Grid>
      </Container>

      {/* 3. PRODUCT PHILOSOPHY */}
      <Box sx={{ py: 15, bgcolor: '#070a0f', borderTop: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <Container maxWidth="md" sx={{ textAlign: 'center' }}>
          <Typography variant="h3" sx={{ fontWeight: 950, letterSpacing: -1, mb: 4 }}>DON'T JUST GET A SIGNAL.<br/>UNDERSTAND IT.</Typography>
          <Typography variant="body1" sx={{ color: 'slategray', fontSize: '1.25rem', lineHeight: 2, mb: 8 }}>
            TradeMind AI is not a stock tip service. It is a professional terminal for auditable signal intelligence.
            Every decision is backed by verifiable market data and a traceable machine-learning lifecycle.
          </Typography>
          <Divider sx={{ mb: 8, opacity: 0.1 }} />
          <Grid container spacing={4} justifyContent="center">
            <Grid item xs={12} md={4}>
              <Typography variant="h5" sx={{ fontWeight: 950, color: '#00D1FF', mb: 2 }}>59.18%</Typography>
              <Typography variant="caption" sx={{ fontWeight: 900, letterSpacing: 1, color: 'white' }}>OBSERVED WIN RATE</Typography>
              <Typography variant="caption" sx={{ display: 'block', color: 'slategray', mt: 1 }}>N=49 Resolved Signals</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
               <Typography variant="h5" sx={{ fontWeight: 950, color: '#00D1FF', mb: 2 }}>2.73</Typography>
               <Typography variant="caption" sx={{ fontWeight: 900, letterSpacing: 1, color: 'white' }}>PROFIT FACTOR</Typography>
               <Typography variant="caption" sx={{ display: 'block', color: 'slategray', mt: 1 }}>Observed Performance</Typography>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* 4. FOOTER */}
      <Container maxWidth="lg" sx={{ py: 10 }}>
        <Grid container spacing={8}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" sx={{ fontWeight: 950, mb: 3 }}>TRADEMIND AI</Typography>
            <Typography variant="body2" sx={{ color: 'slategray', maxWidth: 400, mb: 4 }}>
              Institutional AI investment operating system for the next generation of professional investors.
            </Typography>
            <Stack direction="row" spacing={2}>
              <Button size="small" sx={{ color: 'slategray', fontWeight: 800 }}>TRUST</Button>
              <Button size="small" sx={{ color: 'slategray', fontWeight: 800 }}>METHODOLOGY</Button>
              <Button size="small" sx={{ color: 'slategray', fontWeight: 800 }}>LEGAL</Button>
            </Stack>
          </Grid>
          <Grid item xs={12} md={6} sx={{ textAlign: { md: 'right' } }}>
             <Typography variant="caption" sx={{ color: 'slategray', display: 'block', mb: 2 }}>
               TradeMind AI uses machine-learning systems to process market information. <br/>
               Model outputs are estimates and are not guarantees of future outcomes.
             </Typography>
             <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>
               © 2026 TRADEMIND AI • STRATEGY V2.2
             </Typography>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}

function PillarItem({ icon, title, text }: any) {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>{icon}</Box>
      <Typography variant="h6" sx={{ fontWeight: 950, letterSpacing: 1, mb: 1.5 }}>{title}</Typography>
      <Typography variant="body2" sx={{ color: 'slategray', lineHeight: 1.8 }}>{text}</Typography>
    </Box>
  );
}
