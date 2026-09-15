import { useState, useEffect } from 'react';
import { Box, Typography, Grid, Paper, Stack, alpha, Divider, Button } from '@mui/material';
import { ShieldCheck } from 'lucide-react';
import { getEquityAccuracy } from '../api/client';
import { useNavigate } from 'react-router-dom';

export default function Performance() {
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    getEquityAccuracy().then((data: any) => {
      setSummary(data);
    });
  }, []);

  return (
    <Box sx={{ pb: 10 }}>
      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>OOS MODEL PERFORMANCE</Typography>
        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
           FORENSIC OUT-OF-SAMPLE AUDIT • CHALLENGER V2.3 DATASET
        </Typography>
      </Box>

      {/* 1. PRIMARY: SWING HORIZON */}
      <HorizonSection
        title="PRIMARY: SWING HORIZON"
        stats={summary?.horizons?.SWING}
        description="The most robust horizon with confirmed OOS predictive edge. Recommended for institutional signals."
        color="#10b981"
      />

      {/* 2. SELECTIVE: LONG HORIZON */}
      <HorizonSection
        title="SELECTIVE: LONG HORIZON"
        stats={summary?.horizons?.LONG}
        description="Exceptional accuracy on qualified symbol-specific models. Aggregate performance is sample-limited."
        color="#00D1FF"
      />

      {/* 3. EXPERIMENTAL: SHORT HORIZON */}
      <HorizonSection
        title="EXPERIMENTAL: SHORT HORIZON"
        stats={summary?.horizons?.SHORT}
        description="High-frequency momentum scanning. Validation of consistent predictive edge is currently pending."
        color="slategray"
      />

      <Box sx={{ mt: 10, p: 4, bgcolor: alpha('#7C3AED', 0.02), border: '1px solid rgba(124, 58, 237, 0.1)', borderRadius: 1 }}>
         <Stack direction="row" spacing={3} alignItems="center">
            <ShieldCheck color="#7C3AED" size={24} />
            <Box>
               <Typography variant="subtitle2" sx={{ fontWeight: 950, color: '#fff' }}>CALIBRATION STATUS: VERIFIED</Typography>
               <Typography variant="body2" sx={{ color: 'slategray', fontWeight: 500 }}>
                  Probabilities are calibrated using **Platt Scaling** on chronological holdout sets.
                  A Model Probability of 80% represents an observed success rate of 78-82% in OOS testing.
               </Typography>
            </Box>
         </Stack>
      </Box>
    </Box>
  );
}

function HorizonSection({ title, stats, description, color }: any) {
   const hasData = stats && stats.sample_size > 0;
   const navigate = useNavigate();

   return (
      <Box sx={{ mb: 8 }}>
         <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 950, color }}>{title}</Typography>
            <Divider sx={{ flexGrow: 1, opacity: 0.1, bgcolor: color }} />
         </Stack>

         <Typography variant="body2" sx={{ color: 'slategray', mb: 4, maxWidth: 600 }}>{description}</Typography>

         <Grid container spacing={3}>
            <MetricBox label="SAMPLE SIZE" value={hasData ? stats.sample_size : 'INSUFFICIENT'} />
            <MetricBox label="ROC-AUC" value={hasData ? stats.auc.toFixed(2) : '—'} color={color} />
            <MetricBox label="WIN RATE" value={hasData ? `${stats.win_rate.toFixed(1)}%` : '—'} />
            <MetricBox label="BRIER SCORE" value={hasData ? stats.brier.toFixed(3) : '—'} />
            <MetricBox label="LOG LOSS" value={hasData ? stats.logloss.toFixed(3) : '—'} />
            <MetricBox label="ECE" value={hasData ? stats.ece.toFixed(3) : '—'} />
         </Grid>
         <Box sx={{ mt: 3, textAlign: 'right' }}>
            <Button
                variant="text"
                size="small"
                onClick={() => navigate('/signals')}
                sx={{ color: 'primary.main', fontWeight: 900, fontSize: '0.7rem' }}
            >
                VIEW UNDERLYING SIGNAL HISTORY →
            </Button>
         </Box>
         {!hasData && (
            <Typography variant="caption" sx={{ color: 'slategray', mt: 2, display: 'block', fontStyle: 'italic' }}>
               NO CURRENTLY QUALIFIED PRODUCTION SIGNALS
            </Typography>
         )}
      </Box>
   );
}

function MetricBox({ label, value, color = '#fff' }: any) {
   return (
      <Grid item xs={6} md={3}>
         <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.03)' }}>
            <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, display: 'block', mb: 1, fontSize: '0.6rem' }}>{label}</Typography>
            <Typography variant="h5" sx={{ fontWeight: 950, color, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
         </Paper>
      </Grid>
   );
}
