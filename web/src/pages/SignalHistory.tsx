import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, TextField, MenuItem, Stack } from '@mui/material';
import { getShadowSignals } from '../api/client';

export default function SignalHistory() {
  const [signals, setSignals] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('V2.2_HISTORICAL_REPLAY');

  useEffect(() => {
    const params = {
        dataset_type: typeFilter === 'ALL' ? undefined : typeFilter,
        status: statusFilter === 'ALL' ? undefined : statusFilter,
        limit: 200
    };
    getShadowSignals(params).then(res => {
      setSignals(res.signals || []);
    });
  }, [typeFilter, statusFilter]);

  return (
    <Box sx={{ pb: 8 }}>
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <Box>
           <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>SIGNAL HISTORY</Typography>
           <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
              FORENSIC PERFORMANCE AUDIT • ALL RESOLVED SETUPS
           </Typography>
        </Box>

        <Stack direction="row" spacing={2}>
            <TextField
                select
                size="small"
                label="DATASET"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                sx={{ width: 220 }}
            >
                <MenuItem value="ALL">ALL DATASETS</MenuItem>
                <MenuItem value="V2.2_VERIFIED_REFERENCE">VERIFIED REFERENCE</MenuItem>
                <MenuItem value="V2.2_HISTORICAL_REPLAY">HISTORICAL REPLAY</MenuItem>
                <MenuItem value="V2.2_CURRENT_SHADOW">CURRENT SHADOW</MenuItem>
            </TextField>

            <TextField
                select
                size="small"
                label="OUTCOME"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                sx={{ width: 180 }}
            >
                <MenuItem value="ALL">ALL OUTCOMES</MenuItem>
                <MenuItem value="TARGET_HIT">TARGET HIT</MenuItem>
                <MenuItem value="STOP_LOSS">STOP LOSS</MenuItem>
                <MenuItem value="EXPIRED">EXPIRED</MenuItem>
                <MenuItem value="ACTIVE">ACTIVE</MenuItem>
            </TextField>
        </Stack>
      </Box>

      <TableContainer component={Paper} sx={{ bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
         <Table size="small">
            <TableHead>
               <TableRow>
                  <TableCell>DATE</TableCell>
                  <TableCell>SYMBOL</TableCell>
                  <TableCell align="center">DIRECTION</TableCell>
                  <TableCell align="right">ENTRY</TableCell>
                  <TableCell align="right">EXIT</TableCell>
                  <TableCell align="right">RESULT %</TableCell>
                  <TableCell align="center">OUTCOME</TableCell>
               </TableRow>
            </TableHead>
            <TableBody>
               {signals.map((s, i) => (
                  <TableRow key={s.id || i} hover>
                     <TableCell sx={{ color: 'slategray', fontSize: '0.75rem', fontWeight: 700 }}>
                        {new Date(s.timestamp).toLocaleDateString()}
                     </TableCell>
                     <TableCell sx={{ fontWeight: 900, color: '#00D1FF' }}>{s.symbol}</TableCell>
                     <TableCell align="center">
                        <Typography variant="caption" sx={{ fontWeight: 900, color: s.direction === 'LONG' ? '#10b981' : '#ef4444' }}>{s.direction}</Typography>
                     </TableCell>
                     <TableCell align="right" sx={{ fontFamily: 'JetBrains Mono', fontSize: '0.8rem' }}>{s.entry_price?.toFixed(2)}</TableCell>
                     <TableCell align="right" sx={{ fontFamily: 'JetBrains Mono', fontSize: '0.8rem' }}>{s.exit_price?.toFixed(2) || '—'}</TableCell>
                     <TableCell align="right" sx={{ fontWeight: 900, color: (s.net_return || 0) >= 0 ? '#10b981' : '#ef4444' }}>
                        {(s.net_return || 0).toFixed(2)}%
                     </TableCell>
                     <TableCell align="center">
                        <Chip
                            label={(s.status)?.replace(/_/g, ' ')}
                            size="small"
                            color={s.status === 'TARGET_HIT' ? 'success' : s.status === 'STOP_LOSS' ? 'error' : 'default'}
                            sx={{ height: 20, fontSize: '0.6rem', fontWeight: 900, borderRadius: 0.5 }}
                        />
                     </TableCell>
                  </TableRow>
               ))}
               {signals.length === 0 && (
                   <TableRow>
                       <TableCell colSpan={7} align="center" sx={{ py: 4, color: 'slategray' }}>No signals found for this selection.</TableCell>
                   </TableRow>
               )}
            </TableBody>
         </Table>
      </TableContainer>
    </Box>
  );
}
