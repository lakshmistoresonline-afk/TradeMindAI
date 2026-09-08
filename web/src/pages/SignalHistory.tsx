import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, TextField, MenuItem, alpha } from '@mui/material';
import { getPerformanceSignals } from '../api/client';

export default function SignalHistory() {
  const [signals, setSignals] = useState<any[]>([]);
  const [filter, setFilter] = useState('ALL');

  useEffect(() => {
    getPerformanceSignals().then(data => {
      setSignals(data || []);
    });
  }, []);

  const filtered = useMemo(() => {
     if (filter === 'ALL') return signals;
     return signals.filter(s => (s.status || s.outcome) === filter);
  }, [signals, filter]);

  return (
    <Box sx={{ pb: 8 }}>
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <Box>
           <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>SIGNAL HISTORY</Typography>
           <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
              FORENSIC PERFORMANCE AUDIT • ALL RESOLVED SETUPS
           </Typography>
        </Box>

        <TextField
          select
          size="small"
          label="OUTCOME"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          sx={{ width: 200 }}
        >
           <MenuItem value="ALL">ALL OUTCOMES</MenuItem>
           <MenuItem value="TARGET_HIT">TARGET HIT</MenuItem>
           <MenuItem value="STOP_LOSS">STOP LOSS</MenuItem>
           <MenuItem value="EXPIRED">EXPIRED</MenuItem>
        </TextField>
      </Box>

      <TableContainer component={Paper} sx={{ bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
         <Table size="small">
            <TableHead>
               <TableRow>
                  <TableCell>DATE</TableCell>
                  <TableCell>SYMBOL</TableCell>
                  <TableCell align="center">DIRECTION</TableCell>
                  <TableCell align="right">RESULT %</TableCell>
                  <TableCell align="center">OUTCOME</TableCell>
                  <TableCell align="center">STRATEGY</TableCell>
               </TableRow>
            </TableHead>
            <TableBody>
               {filtered.map((s, i) => (
                  <TableRow key={i} hover>
                     <TableCell sx={{ color: 'slategray', fontSize: '0.75rem', fontWeight: 700 }}>
                        {new Date(s.timestamp || s.date).toLocaleDateString()}
                     </TableCell>
                     <TableCell sx={{ fontWeight: 900 }}>{s.symbol}</TableCell>
                     <TableCell align="center">
                        <Typography variant="caption" sx={{ fontWeight: 900, color: s.direction === 'LONG' ? '#10b981' : '#ef4444' }}>{s.direction}</Typography>
                     </TableCell>
                     <TableCell align="right" sx={{ fontWeight: 900, color: (s.profit_pct || s.net_return || 0) >= 0 ? '#10b981' : '#ef4444' }}>
                        {(s.profit_pct || s.net_return || 0).toFixed(2)}%
                     </TableCell>
                     <TableCell align="center">
                        <Chip
                            label={(s.status || s.outcome)?.replace(/_/g, ' ')}
                            size="small"
                            sx={{ height: 20, fontSize: '0.6rem', fontWeight: 900, borderRadius: 0.5 }}
                        />
                     </TableCell>
                     <TableCell align="center">
                        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700 }}>V2.2</Typography>
                     </TableCell>
                  </TableRow>
               ))}
            </TableBody>
         </Table>
      </TableContainer>
    </Box>
  );
}
