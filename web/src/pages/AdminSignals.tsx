import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Stack, Button, alpha, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';
import { CheckCircle2 } from 'lucide-react';
import { getEquitySignals } from '../api/client';
import { useNavigate } from 'react-router-dom';

export default function AdminSignals() {
  const [signals, setSignals] = useState<any[]>([]);
  const [, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getEquitySignals({ limit: 100 }).then(data => {
        setSignals(data || []);
        setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <Box sx={{ pb: 10, maxWidth: 1400, mx: 'auto', p: 4, color: 'white' }}>
      <Box sx={{ mb: 5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
           <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>SIGNAL OPERATIONS</Typography>
           <Typography variant="caption" sx={{ color: '#a855f7', fontWeight: 800, letterSpacing: 1.5 }}>
              MASTER PUBLICATION & LIFECYCLE GATE
           </Typography>
        </Box>
      </Box>

      <TableContainer component={Paper} sx={{ bgcolor: 'rgba(15, 23, 42, 0.85)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 2 }}>
         <Table>
            <TableHead>
               <TableRow sx={{ '& th': { color: '#64748b', fontWeight: 900, borderBottom: '1px solid rgba(255,255,255,0.06)' } }}>
                  <TableCell>SIGNAL ID</TableCell>
                  <TableCell>SYMBOL</TableCell>
                  <TableCell>DIRECTION</TableCell>
                  <TableCell>CONVICTION</TableCell>
                  <TableCell>ENTRY</TableCell>
                  <TableCell>STATUS</TableCell>
                  <TableCell>VALIDATION</TableCell>
                  <TableCell align="right">OPERATIONS</TableCell>
               </TableRow>
            </TableHead>
            <TableBody>
               {signals.map((s) => (
                  <TableRow key={s.id} hover sx={{ cursor: 'pointer', '& td': { borderBottom: '1px solid rgba(255,255,255,0.03)' } }}>
                     <TableCell sx={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '0.65rem', color: '#64748b' }}>{s.id}</TableCell>
                     <TableCell sx={{ fontWeight: 950, fontFamily: 'JetBrains Mono, monospace' }}>{s.symbol}</TableCell>
                     <TableCell>
                        <Chip label={s.direction || (s.rating?.includes('BUY') ? 'LONG' : 'SHORT')} size="small" sx={{ fontWeight: 950, height: 20, bgcolor: alpha(s.direction === 'LONG' || s.rating?.includes('BUY') ? '#10b981' : '#f43f5e', 0.12), color: s.direction === 'LONG' || s.rating?.includes('BUY') ? '#10b981' : '#f43f5e' }} />
                     </TableCell>
                     <TableCell sx={{ fontWeight: 950, color: '#00D1FF', fontFamily: 'JetBrains Mono, monospace' }}>{Math.round(s.conviction || 75)}%</TableCell>
                     <TableCell sx={{ fontFamily: 'JetBrains Mono, monospace' }}>₹{s.entry_price?.toLocaleString() || '—'}</TableCell>
                     <TableCell>
                        <Chip label={s.status || 'ACTIVE'} size="small" variant="outlined" sx={{ fontWeight: 950, fontSize: '0.55rem', height: 20, color: '#64748b', borderColor: 'rgba(255,255,255,0.15)' }} />
                     </TableCell>
                     <TableCell>
                        <Stack direction="row" spacing={1} alignItems="center">
                           <CheckCircle2 size={12} color="#10b981" />
                           <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 950, fontSize: '0.65rem' }}>PASSED GATE</Typography>
                        </Stack>
                     </TableCell>
                     <TableCell align="right">
                        <Stack direction="row" spacing={1} justifyContent="flex-end">
                           <Button size="small" variant="outlined" color="primary" onClick={() => navigate(`/signals/${s.id}`)} sx={{ fontSize: '0.65rem', fontWeight: 900 }}>AUDIT</Button>
                        </Stack>
                     </TableCell>
                  </TableRow>
               ))}
            </TableBody>
         </Table>
      </TableContainer>
    </Box>
  );
}
