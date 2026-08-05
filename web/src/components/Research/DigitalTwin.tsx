import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Chip, Stack, CircularProgress, Divider } from '@mui/material';
import { Fingerprint, Activity, ShieldCheck, Zap, BrainCircuit } from 'lucide-react';
import { getDigitalTwin } from '../../api/client';

export default function DigitalTwin({ symbol }: { symbol: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getDigitalTwin(symbol).then(setData).finally(() => setLoading(false));
  }, [symbol]);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>;
  if (!data) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Fingerprint size={20} className="text-emerald-500" /> Stock Digital Twin: {symbol}
      </Typography>

      <Paper sx={{ p: 4, bgcolor: 'rgba(15, 23, 42, 0.3)', border: '1px solid #334155' }}>
         <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
               <Typography variant="subtitle2" color="textSecondary" gutterBottom>INTELLIGENCE DNA</Typography>
               <Stack spacing={2} sx={{ mt: 2 }}>
                  <DNARow label="AI Investment Score" value={data.intelligence_state.ai_score} />
                  <DNARow label="Investment Grade" value={data.intelligence_state.grade} color="primary.main" />
                  <DNARow label="Technical Posture" value={data.technical_posture.trend} />
                  <DNARow label="Volatility Regime" value={data.technical_posture.volatility} />
               </Stack>
            </Grid>

            <Grid item xs={12} md={4}>
               <Typography variant="subtitle2" color="textSecondary" gutterBottom>RISK SIGNATURE</Typography>
               <Stack spacing={2} sx={{ mt: 2 }}>
                  <DNARow label="Beta Coefficient" value={data.risk_profile.beta?.toFixed(2)} />
                  <DNARow label="Max Historical DD" value={`${(data.risk_profile.max_drawdown * 100).toFixed(1)}%`} color="error.main" />
                  <DNARow label="Model Confidence" value={`${data.risk_profile.confidence}%`} />
               </Stack>
            </Grid>

            <Grid item xs={12} md={4}>
               <Typography variant="subtitle2" color="textSecondary" gutterBottom>AI STATE SUMMARY</Typography>
               <Box sx={{ mt: 2, p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 2, borderLeft: '3px solid #10b981' }}>
                  <Typography variant="body2" sx={{ lineHeight: 1.6, fontStyle: 'italic' }}>
                     "{data.intelligence_state.consensus?.substring(0, 200)}..."
                  </Typography>
               </Box>
            </Grid>
         </Grid>

         <Divider sx={{ my: 4, opacity: 0.1 }} />

         <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', gap: 1 }}>
               <Chip label="Continuously Learning" size="small" variant="outlined" icon={<BrainCircuit size={12} />} />
               <Chip label="Real-time Synced" size="small" variant="outlined" icon={<Activity size={12} />} />
            </Box>
            <Typography variant="caption" color="textSecondary">Last DNA Sync: {new Date(data.updated_at).toLocaleString()}</Typography>
         </Box>
      </Paper>
    </Box>
  );
}

function DNARow({ label, value, color }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
       <Typography variant="body2" color="textSecondary">{label}</Typography>
       <Typography variant="body2" fontWeight="bold" sx={{ color: color || 'text.primary' }}>{value || 'N/A'}</Typography>
    </Box>
  );
}
