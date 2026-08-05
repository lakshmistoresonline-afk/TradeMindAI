import { Box, Typography, Paper, Grid, Table, TableBody, TableCell, TableHead, TableRow, Chip } from '@mui/material';
import { LineChart } from 'lucide-react';

export default function TechnicalDeepDive({ data }: { data: any }) {
  if (!data?.indicators) return null;

  const indicators = [
    { name: 'EMA (20)', value: data.indicators.EMA_20?.toFixed(2), signal: 'BULLISH' },
    { name: 'EMA (50)', value: data.indicators.EMA_50?.toFixed(2), signal: 'BULLISH' },
    { name: 'EMA (200)', value: data.indicators.EMA_200?.toFixed(2), signal: 'NEUTRAL' },
    { name: 'RSI (14)', value: data.indicators.RSI?.toFixed(2), signal: data.indicators.RSI > 70 ? 'OVERBOUGHT' : data.indicators.RSI < 30 ? 'OVERSOLD' : 'NEUTRAL' },
    { name: 'MACD', value: data.indicators.MACD_12_26_9?.toFixed(2), signal: 'BULLISH' },
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <LineChart size={20} className="text-blue-500" /> Technical Deep Dive
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 0, overflow: 'hidden' }}>
            <Table size="small">
              <TableHead sx={{ bgcolor: 'rgba(255,255,255,0.02)' }}>
                <TableRow>
                  <TableCell>Indicator</TableCell>
                  <TableCell>Value</TableCell>
                  <TableCell align="right">Signal</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {indicators.map((ind) => (
                  <TableRow key={ind.name} hover>
                    <TableCell sx={{ py: 1.5 }}>{ind.name}</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>{ind.value}</TableCell>
                    <TableCell align="right">
                      <Chip
                        label={ind.signal}
                        size="small"
                        color={ind.signal === 'BULLISH' ? 'success' : ind.signal === 'BEARISH' ? 'error' : 'default'}
                        variant="outlined"
                        sx={{ fontSize: '0.65rem', height: 20 }}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>SUPPORT & RESISTANCE (PIVOT)</Typography>
            <Box sx={{ mt: 2, flexGrow: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
               <LevelRow label="R2 (Resistance)" value={`₹${data.indicators.R2?.toFixed(2)}`} color="#f43f5e" />
               <LevelRow label="R1 (Resistance)" value={`₹${data.indicators.R1?.toFixed(2)}`} color="#fb7185" />
               <LevelRow label="Pivot Point" value={`₹${data.indicators.Pivot?.toFixed(2)}`} color="#94a3b8" />
               <LevelRow label="S1 (Support)" value={`₹${data.indicators.S1?.toFixed(2)}`} color="#34d399" />
               <LevelRow label="S2 (Support)" value={`₹${data.indicators.S2?.toFixed(2)}`} color="#10b981" />
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function LevelRow({ label, value, color }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 1, borderLeft: `4px solid ${color}`, bgcolor: 'rgba(255,255,255,0.02)' }}>
      <Typography variant="caption" fontWeight="bold">{label}</Typography>
      <Typography variant="body2" fontWeight="bold">{value}</Typography>
    </Box>
  );
}
