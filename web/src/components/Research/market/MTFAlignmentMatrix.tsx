import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Chip, CircularProgress, Tooltip } from '@mui/material';
import { Layers, CheckCircle2, AlertCircle, HelpCircle } from 'lucide-react';
import { getMTFAlignment } from '../../../api/client';

export default function MTFAlignmentMatrix({ symbol }: { symbol: string }) {
  const [alignment, setAlignment] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (symbol) {
      setLoading(true);
      getMTFAlignment(symbol)
        .then(setAlignment)
        .catch(err => console.error("MTF Error:", err))
        .finally(() => setLoading(false));
    }
  }, [symbol]);

  if (loading) return <Box sx={{ py: 4, textAlign: 'center' }}><CircularProgress size={24} /></Box>;
  if (!alignment) return null;

  const getBiasColor = (bias: string) => {
    if (bias === 'BULLISH') return '#10b981';
    if (bias === 'BEARISH') return '#f43f5e';
    return '#94a3b8';
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" fontWeight={800} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Layers size={20} className="text-indigo-400" /> Multi-Timeframe Alignment
        </Typography>
        <Chip
          label={alignment.alignment_status}
          size="small"
          color={alignment.alignment_status === 'ALIGNED' ? 'primary' : 'warning'}
          sx={{ fontWeight: 900, height: 20, fontSize: '0.6rem' }}
        />
      </Box>

      <Paper sx={{ p: 2, border: '1px solid #1e293b', bgcolor: 'rgba(255,255,255,0.01)' }}>
        <Grid container spacing={2}>
           {Object.entries(alignment.timeframes).map(([tf, data]: any) => (
             <Grid item xs={2.4} key={tf}>
               <Box sx={{
                 textAlign: 'center',
                 p: 1.5,
                 borderRadius: 1,
                 border: `1px solid ${getBiasColor(data.bias)}20`,
                 bgcolor: `${getBiasColor(data.bias)}05`
               }}>
                 <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, display: 'block', mb: 1 }}>{tf}</Typography>
                 <Box sx={{
                   width: 12,
                   height: 12,
                   borderRadius: '50%',
                   bgcolor: getBiasColor(data.bias),
                   margin: '0 auto 8px',
                   boxShadow: `0 0 10px ${getBiasColor(data.bias)}40`
                 }} />
                 <Typography variant="body2" sx={{ fontWeight: 900, color: getBiasColor(data.bias), fontSize: '0.7rem' }}>
                   {data.bias}
                 </Typography>
               </Box>
             </Grid>
           ))}
        </Grid>

        <Box sx={{ mt: 3, p: 2, bgcolor: 'rgba(15, 23, 42, 0.5)', borderRadius: 1, display: 'flex', gap: 2, alignItems: 'center' }}>
           {alignment.alignment_status === 'ALIGNED' ? (
             <CheckCircle2 size={20} className="text-emerald-500" />
           ) : (
             <AlertCircle size={20} className="text-amber-500" />
           )}
           <Box>
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.secondary' }}>
                {alignment.summary}
              </Typography>
              <Typography variant="caption" sx={{ color: 'slategray', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                Verified via Fractal Momentum Analysis <Tooltip title="Institutional order flow is highest when multiple timeframes align in direction."><HelpCircle size={10} /></Tooltip>
              </Typography>
           </Box>
        </Box>
      </Paper>
    </Box>
  );
}
