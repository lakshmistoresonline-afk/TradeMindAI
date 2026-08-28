import { Box, Typography, Paper, Table, TableBody, TableCell, TableHead, TableRow, LinearProgress } from '@mui/material';
import { useAITradeDecision } from '../../../hooks/useAITradeDecision';

export default function PeerBenchmark({ stock }: { stock: any }) {
  const decision = useAITradeDecision(stock);

  const peers = [
    { symbol: stock.symbol, conviction: decision.conviction, pe: stock.pe_ratio || 24.5, margin: '18.2%' },
    { symbol: 'PEER_A', conviction: 65, pe: 32.1, margin: '15.4%' },
    { symbol: 'PEER_B', conviction: 42, pe: 18.4, margin: '12.8%' },
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight={800} gutterBottom>Peer Benchmark</Typography>
      <Paper sx={{ p: 0, overflow: 'hidden', border: '1px solid #1e293b' }}>
        <Table size="small">
          <TableHead sx={{ bgcolor: 'rgba(255,255,255,0.02)' }}>
            <TableRow>
              <TableCell sx={{ pl: 3 }}>Peer</TableCell>
              <TableCell align="right">AI Conviction</TableCell>
              <TableCell align="right">P/E Ratio</TableCell>
              <TableCell align="right">Op. Margin</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {peers.map((p) => (
              <TableRow key={p.symbol} hover>
                <TableCell sx={{ fontWeight: 900, pl: 3 }}>{p.symbol}</TableCell>
                <TableCell align="right">
                   <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 1 }}>
                      <Typography variant="caption" sx={{ fontWeight: 800, fontFamily: 'JetBrains Mono' }}>{p.conviction}%</Typography>
                      <Box sx={{ width: 40 }}><LinearProgress variant="determinate" value={p.conviction} sx={{ height: 4, borderRadius: 2 }} /></Box>
                   </Box>
                </TableCell>
                <TableCell align="right" sx={{ fontWeight: 600 }}>{p.pe.toFixed(1)}</TableCell>
                <TableCell align="right">{p.margin}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}
