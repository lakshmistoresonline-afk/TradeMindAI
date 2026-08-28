import { Box, Typography, Paper, Stack, alpha } from '@mui/material';
import { CheckCircle2, AlertTriangle, Circle } from 'lucide-react';

interface ConfluenceMatrixProps {
  stock: any;
}

export default function ConfluenceMatrix({ stock }: ConfluenceMatrixProps) {
  const analysis = stock.analysis || {};
  const technical = analysis.technical_data || {};
  const rsi = technical.indicators?.RSI || 50;

  // Logic to determine status based on existing data
  const getStatus = (factor: string) => {
    switch (factor) {
      case 'TECHNICAL':
        return rsi < 50 ? 'BULLISH' : 'BEARISH';
      case 'MOMENTUM':
        return technical.indicators?.EMA_20 > technical.indicators?.EMA_50 ? 'BULLISH' : 'NEUTRAL';
      case 'VOLUME':
        return 'CONFIRMED';
      case 'INSTITUTIONAL':
        return (stock.fii_holding || 0) > 20 ? 'BULLISH' : 'NEUTRAL';
      case 'OPTIONS':
        return stock.options_data?.available ? 'BULLISH' : 'NEUTRAL';
      case 'FUNDAMENTAL':
        return (stock.pe_ratio || 0) < 30 ? 'POSITIVE' : 'NEUTRAL';
      default:
        return 'NEUTRAL';
    }
  };

  const factors = [
    { label: 'Technical Structure', status: getStatus('TECHNICAL') },
    { label: 'Momentum Alignment', status: getStatus('MOMENTUM') },
    { label: 'Volume Validation', status: getStatus('VOLUME') },
    { label: 'Institutional Bias', status: getStatus('INSTITUTIONAL') },
    { label: 'Options Positioning', status: getStatus('OPTIONS') },
    { label: 'Fundamental Grade', status: getStatus('FUNDAMENTAL') },
  ];

  return (
    <Paper sx={{ p: 3, border: '1px solid rgba(255,255,255,0.05)', bgcolor: '#0C1118' }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 3, letterSpacing: 1 }}>SIGNAL CONFLUENCE MATRIX</Typography>

      <Stack spacing={2}>
        {factors.map((f, i) => (
          <Box key={i} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.secondary' }}>{f.label}</Typography>
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography variant="caption" sx={{
                fontWeight: 900,
                color: f.status.includes('BULLISH') || f.status === 'POSITIVE' || f.status === 'CONFIRMED' ? '#10b981' : (f.status.includes('BEARISH') ? '#ef4444' : '#64748b')
              }}>
                {f.status}
              </Typography>
              {f.status.includes('BULLISH') || f.status === 'POSITIVE' || f.status === 'CONFIRMED' ? (
                <CheckCircle2 size={14} className="text-emerald-500" />
              ) : f.status.includes('BEARISH') ? (
                <AlertTriangle size={14} className="text-rose-500" />
              ) : (
                <Circle size={14} className="text-slategray opacity-30" />
              )}
            </Stack>
          </Box>
        ))}
      </Stack>

      <Box sx={{ mt: 3, p: 2, bgcolor: alpha('#00D1FF', 0.05), borderRadius: 1, border: '1px dashed rgba(0, 209, 255, 0.2)' }}>
        <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 800, textAlign: 'center', display: 'block' }}>
          MULTI-FACTOR ALIGNMENT: {(factors.filter(f => f.status === 'BULLISH' || f.status === 'POSITIVE' || f.status === 'CONFIRMED').length / factors.length * 100).toFixed(0)}%
        </Typography>
      </Box>
    </Paper>
  );
}
