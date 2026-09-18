import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Button, Stack, alpha } from '@mui/material';
import { FileText, Download, Lock, Zap } from 'lucide-react';
import { getUserReports } from '../api/client';
import { useNavigate } from 'react-router-dom';

export default function MyReports() {
  const [reports, setReports] = useState<any[]>([]);
  const [, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getUserReports().then(data => {
        setReports(data || []);
        setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <Box sx={{ pb: 10, maxWidth: 1200, mx: 'auto', p: 4, color: 'white' }}>
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
           <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>MY REPORTS</Typography>
           <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
              YOUR AUTHORITATIVE RESEARCH ARTIFACTS
           </Typography>
        </Box>
        <Button variant="contained" startIcon={<Zap size={18} />} onClick={() => navigate('/pricing')} sx={{ fontWeight: 950 }}>GENERATE NEW REPORT</Button>
      </Box>

      <TableContainer component={Paper} sx={{ bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1 }}>
         <Table>
            <TableHead>
               <TableRow sx={{ '& th': { color: 'slategray', fontWeight: 900, borderBottom: '1px solid rgba(255,255,255,0.05)' } }}>
                  <TableCell>REPORT NAME</TableCell>
                  <TableCell>TYPE</TableCell>
                  <TableCell>SYMBOL</TableCell>
                  <TableCell>DATE</TableCell>
                  <TableCell>STATUS</TableCell>
                  <TableCell align="right">ACTION</TableCell>
               </TableRow>
            </TableHead>
            <TableBody>
               {reports.length > 0 ? reports.map((r) => (
                  <TableRow key={r.id}>
                     <TableCell sx={{ fontWeight: 800 }}>{r.symbol} Deep Dive Audit</TableCell>
                     <TableCell><Chip label={r.type} size="small" variant="outlined" sx={{ fontWeight: 900, fontSize: '0.6rem' }} /></TableCell>
                     <TableCell sx={{ fontFamily: 'JetBrains Mono', fontWeight: 900 }}>{r.symbol}</TableCell>
                     <TableCell sx={{ color: 'slategray' }}>{new Date(r.created_at).toLocaleDateString()}</TableCell>
                     <TableCell>
                        <Chip label={r.status} size="small" sx={{ bgcolor: alpha('#10b981', 0.1), color: '#10b981', fontWeight: 950, fontSize: '0.6rem' }} />
                     </TableCell>
                     <TableCell align="right">
                        <Button size="small" startIcon={<Download size={14} />} sx={{ fontWeight: 900 }}>VIEW</Button>
                     </TableCell>
                  </TableRow>
               )) : (
                  <TableRow>
                     <TableCell colSpan={6} sx={{ py: 10, textAlign: 'center' }}>
                        <FileText size={48} color="slategray" style={{ opacity: 0.2, marginBottom: 16 }} />
                        <Typography sx={{ color: 'slategray', fontWeight: 700 }}>You haven't generated any institutional reports yet.</Typography>
                        <Typography variant="caption" sx={{ color: 'slategray' }}>PRO members can generate unlimited structural deep-dive reports.</Typography>
                     </TableCell>
                  </TableRow>
               )}
            </TableBody>
         </Table>
      </TableContainer>

      <Box sx={{ mt: 8, p: 4, bgcolor: alpha('#00D1FF', 0.02), border: '1px dashed #00D1FF', borderRadius: 1 }}>
         <Stack direction="row" spacing={3} alignItems="center">
            <Lock size={24} color="#00D1FF" />
            <Box>
               <Typography variant="subtitle2" sx={{ fontWeight: 950 }}>PREMIUM RESEARCH CAPABILITIES</Typography>
               <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700 }}>
                  Unlock multi-horizon audit reports, sector correlation matrixes, and institutional flow forensic artifacts with TradeMind PRO.
               </Typography>
            </Box>
         </Stack>
      </Box>
    </Box>
  );
}
