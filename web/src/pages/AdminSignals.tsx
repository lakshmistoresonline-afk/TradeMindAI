import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Stack, Button, alpha, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';
import { CheckCircle2, RefreshCw } from 'lucide-react';
import { getEquitySignals } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { useTurboSync } from '../hooks/useTurboSync';
import { mapCanonicalSignal } from '../hooks/useAITradeDecision';

export default function AdminSignals() {
  const [signals, setSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { firestoreSignals } = useTurboSync();

  const fetchSignals = () => {
    setLoading(true);
    getEquitySignals({ limit: 100 }).then(data => {
        const normalized = (data || []).map((s: any) => mapCanonicalSignal(s));
        setSignals(normalized);
        setLoading(false);
    }).catch(() => {
        setLoading(false);
    });
  };

  useEffect(() => {
    fetchSignals();
  }, []);

  useEffect(() => {
    if (firestoreSignals.length === 0) return;
    const normalizedFS = firestoreSignals.map(s => mapCanonicalSignal(s));

    setSignals(prev => {
        const mergedMap = new Map();
        prev.forEach(s => mergedMap.set(s.id, s));
        normalizedFS.forEach(s => mergedMap.set(s.id, s));

        return Array.from(mergedMap.values()).sort((a,b) =>
            new Date(b.decision?.generatedAt || 0).getTime() - new Date(a.decision?.generatedAt || 0).getTime()
        );
    });
  }, [firestoreSignals]);

  return (
    <Box sx={{ pb: 10, maxWidth: 1400, mx: 'auto', p: 4, color: 'white' }}>
      <Box sx={{ mb: 5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
           <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>SIGNAL OPERATIONS</Typography>
           <Typography variant="caption" sx={{ color: '#a855f7', fontWeight: 800, letterSpacing: 1.5 }}>
              MASTER PUBLICATION & LIFECYCLE GATE (STRATEGY V2.5 SHAP & GEX)
           </Typography>
        </Box>
        <Button
           variant="outlined"
           color="secondary"
           startIcon={<RefreshCw size={16} />}
           onClick={fetchSignals}
           sx={{ fontWeight: 950, borderColor: 'rgba(255,255,255,0.15)' }}
        >
           REFRESH OPERATIONAL GATE
        </Button>
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
                  <TableCell>STOP LOSS</TableCell>
                  <TableCell>STATUS</TableCell>
                  <TableCell>VALIDATION</TableCell>
                  <TableCell align="right">OPERATIONS</TableCell>
               </TableRow>
            </TableHead>
            <TableBody>
               {signals.length === 0 && !loading ? (
                  <TableRow>
                     <TableCell colSpan={9} align="center" sx={{ py: 6, color: '#64748b', fontWeight: 800 }}>
                        No active signals detected in Operational Lifecycle Gate.
                     </TableCell>
                  </TableRow>
               ) : (
                  signals.map((s) => {
                     const dec = s.decision || s;
                     const isBuy = dec.rating?.includes('BUY') || dec.direction === 'LONG';
                     return (
                        <TableRow key={s.id || s.symbol} hover sx={{ cursor: 'pointer', '& td': { borderBottom: '1px solid rgba(255,255,255,0.03)' } }}>
                           <TableCell sx={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '0.65rem', color: '#64748b' }}>{s.id}</TableCell>
                           <TableCell sx={{ fontWeight: 950, fontFamily: 'JetBrains Mono, monospace' }}>{s.symbol}</TableCell>
                           <TableCell>
                              <Chip
                                 label={isBuy ? 'LONG ▲' : 'SHORT ▼'}
                                 size="small"
                                 sx={{ fontWeight: 950, height: 20, bgcolor: alpha(isBuy ? '#10b981' : '#f43f5e', 0.12), color: isBuy ? '#10b981' : '#f43f5e' }}
                              />
                           </TableCell>
                           <TableCell sx={{ fontWeight: 950, color: '#00D1FF', fontFamily: 'JetBrains Mono, monospace' }}>{dec.conviction || 75}%</TableCell>
                           <TableCell sx={{ fontFamily: 'JetBrains Mono, monospace' }}>₹{dec.entry ? dec.entry.toLocaleString() : '—'}</TableCell>
                           <TableCell sx={{ fontFamily: 'JetBrains Mono, monospace', color: '#f43f5e', fontWeight: 800 }}>₹{dec.stopLoss ? dec.stopLoss.toLocaleString() : '—'}</TableCell>
                           <TableCell>
                              <Chip label={dec.status || 'ACTIVE'} size="small" variant="outlined" sx={{ fontWeight: 950, fontSize: '0.55rem', height: 20, color: '#64748b', borderColor: 'rgba(255,255,255,0.15)' }} />
                           </TableCell>
                           <TableCell>
                              <Stack direction="row" spacing={1} alignItems="center">
                                 <CheckCircle2 size={12} color="#10b981" />
                                 <Typography variant="caption" sx={{ color: '#10b981', fontWeight: 950, fontSize: '0.65rem' }}>PASSED V2.5 GATE</Typography>
                              </Stack>
                           </TableCell>
                           <TableCell align="right">
                              <Stack direction="row" spacing={1} justifyContent="flex-end">
                                 <Button size="small" variant="outlined" color="primary" onClick={() => navigate(`/signals/${s.id}`)} sx={{ fontSize: '0.65rem', fontWeight: 900 }}>AUDIT</Button>
                              </Stack>
                           </TableCell>
                        </TableRow>
                     );
                  })
               )}
            </TableBody>
         </Table>
      </TableContainer>
    </Box>
  );
}
