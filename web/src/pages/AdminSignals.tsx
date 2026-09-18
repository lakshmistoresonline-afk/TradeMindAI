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
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
           <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>SIGNAL OPERATIONS</Typography>
           <Typography variant="caption" sx={{ color: 'secondary.main', fontWeight: 800, letterSpacing: 1.5 }}>
              MASTER PUBLICATION & LIFECYCLE GATE
           </Typography>
        </Box>
      </Box>

      <TableContainer component={Paper} sx={{ bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1 }}>
         <Table>
            <TableHead>
               <TableRow sx={{ '& th': { color: 'slategray', fontWeight: 900, borderBottom: '1px solid rgba(255,255,255,0.05)' } }}>
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
                  <TableRow key={s.id} hover sx={{ cursor: 'pointer' }}>
                     <TableCell sx={{ fontFamily: 'JetBrains Mono', fontSize: '0.6rem', color: 'slategray' }}>{s.id}</TableCell>
                     <TableCell sx={{ fontWeight: 950 }}>{s.symbol}</TableCell>
                     <TableCell>
                        <Chip label={s.direction} size="small" sx={{ fontWeight: 950, height: 20, bgcolor: alpha(s.direction === 'LONG' ? '#10b981' : '#ef4444', 0.1), color: s.direction === 'LONG' ? '#10b981' : '#ef4444' }} />
                     </TableCell>
                     <TableCell sx={{ fontWeight: 900, color: '#00D1FF' }}>{Math.round(s.conviction)}%</TableCell>
                     <TableCell sx={{ fontFamily: 'JetBrains Mono' }}>₹{s.entry_price?.toLocaleString()}</TableCell>
                     <TableCell>
                        <Chip label={s.status} size="small" variant="outlined" sx={{ fontWeight: 900, fontSize: '0.5rem', height: 18, color: 'slategray' }} />
                     </TableCell>
                     <TableCell>
                        <Stack direction="row" spacing={1} alignItems="center">
                           <CheckCircle2 size={12} color="#10b981" />
                           <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 900, fontSize: '0.6rem' }}>PASSED</Typography>
                        </Stack>
                     </TableCell>
                     <TableCell align="right">
                        <Stack direction="row" spacing={1} justifyContent="flex-end">
                           <Button size="small" variant="outlined" color="error" sx={{ fontSize: '0.6rem', fontWeight: 900 }}>REJECT</Button>
                           <Button size="small" variant="outlined" color="primary" onClick={() => navigate(`/signals/${s.id}`)} sx={{ fontSize: '0.6rem', fontWeight: 900 }}>AUDIT</Button>
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
