import { useState, useEffect } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, CircularProgress, alpha, Grid } from '@mui/material';
import { getOptionChain } from '../../../api/client';

interface OptionChainTableProps {
  symbol: string;
}

export default function OptionChainTable({ symbol }: OptionChainTableProps) {
  const [loading, setLoading] = useState(true);
  const [chain, setChain] = useState<any>(null);

  useEffect(() => {
    const fetchChain = async () => {
      setLoading(true);
      try {
        const data = await getOptionChain(symbol);
        setChain(data);
      } catch (error) {
        console.error("Error fetching option chain:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchChain();
  }, [symbol]);

  if (loading) return (
     <Box sx={{ py: 10, textAlign: 'center' }}>
        <CircularProgress size={30} sx={{ mb: 2 }} />
        <Typography variant="caption" display="block" sx={{ fontWeight: 800 }}>SYNCING INSTITUTIONAL OPTION CHAIN...</Typography>
     </Box>
  );

  if (!chain || !chain.available) return (
     <Box sx={{ py: 10, textAlign: 'center', opacity: 0.5 }}>
        <Typography variant="body2">No F&O data available for this instrument.</Typography>
     </Box>
  );

  return (
    <Box>
       <Paper sx={{ p: 3, mb: 3, bgcolor: 'rgba(255,255,255,0.01)', border: '1px solid rgba(255,255,255,0.03)' }}>
          <Grid container spacing={3}>
             <Grid item xs={12} md={3}>
                <MetricBox label="PUT-CALL RATIO (PCR)" value={chain.pcr.toFixed(2)} color={chain.pcr > 1.1 ? '#10b981' : chain.pcr < 0.9 ? '#ef4444' : 'white'} />
             </Grid>
             <Grid item xs={12} md={3}>
                <MetricBox label="MAX PAIN LEVEL" value={`₹${Math.round(chain.max_pain).toLocaleString()}`} />
             </Grid>
             <Grid item xs={12} md={3}>
                <MetricBox label="TOTAL OPEN INTEREST" value={chain.total_oi.toLocaleString()} />
             </Grid>
             <Grid item xs={12} md={3}>
                <MetricBox label="ATM IV" value={`${(chain.iv_atm * 100).toFixed(1)}%`} color="#7C3AED" />
             </Grid>
          </Grid>
       </Paper>

       <Typography variant="caption" sx={{ color: 'slategray', mb: 2, display: 'block', fontWeight: 800 }}>
          LIVE OPTION CHAIN • EXPIRY: {new Date(chain.expiry).toLocaleDateString()}
       </Typography>

       <TableContainer component={Paper} sx={{ bgcolor: 'transparent', border: '1px solid rgba(255,255,255,0.05)' }}>
          <Table size="small">
             <TableHead>
                <TableRow>
                   <TableCell align="center" colSpan={3} sx={{ bgcolor: alpha('#10b981', 0.05), borderBottom: '2px solid #10b981' }}>CALLS</TableCell>
                   <TableCell align="center" sx={{ bgcolor: 'rgba(255,255,255,0.03)' }}>STRIKE</TableCell>
                   <TableCell align="center" colSpan={3} sx={{ bgcolor: alpha('#ef4444', 0.05), borderBottom: '2px solid #ef4444' }}>PUTS</TableCell>
                </TableRow>
                <TableRow>
                   <TableCell align="right">OI</TableCell>
                   <TableCell align="right">CHG</TableCell>
                   <TableCell align="right">LTP</TableCell>
                   <TableCell align="center" sx={{ fontWeight: 900 }}>PRICE</TableCell>
                   <TableCell align="left">LTP</TableCell>
                   <TableCell align="left">CHG</TableCell>
                   <TableCell align="left">OI</TableCell>
                </TableRow>
             </TableHead>
             <TableBody>
                {chain.strikes && chain.strikes.length > 0 ? (
                   chain.strikes.map((s: any, i: number) => (
                      <TableRow key={i} hover>
                         <TableCell align="right">{s.calls?.oi?.toLocaleString() || '—'}</TableCell>
                         <TableCell align="right" sx={{ color: (s.calls?.change || 0) >= 0 ? '#10b981' : '#ef4444' }}>
                            {s.calls?.change ? `${s.calls.change}%` : '—'}
                         </TableCell>
                         <TableCell align="right">₹{s.calls?.ltp?.toLocaleString() || '—'}</TableCell>
                         <TableCell align="center" sx={{ bgcolor: 'rgba(255,255,255,0.02)', fontWeight: 800 }}>{s.strike}</TableCell>
                         <TableCell align="left">₹{s.puts?.ltp?.toLocaleString() || '—'}</TableCell>
                         <TableCell align="left" sx={{ color: (s.puts?.change || 0) >= 0 ? '#10b981' : '#ef4444' }}>
                            {s.puts?.change ? `${s.puts.change}%` : '—'}
                         </TableCell>
                         <TableCell align="left">{s.puts?.oi?.toLocaleString() || '—'}</TableCell>
                      </TableRow>
                   ))
                ) : (
                   <TableRow>
                      <TableCell colSpan={7} align="center" sx={{ py: 10 }}>
                         <Typography variant="body2" color="textSecondary">No live strike data available.</Typography>
                      </TableCell>
                   </TableRow>
                )}
             </TableBody>
          </Table>
       </TableContainer>
    </Box>
  );
}

function MetricBox({ label, value, color = 'white' }: any) {
   return (
      <Box>
         <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray', letterSpacing: 1 }}>{label}</Typography>
         <Typography variant="h5" sx={{ fontWeight: 900, color }}>{value}</Typography>
      </Box>
   );
}
