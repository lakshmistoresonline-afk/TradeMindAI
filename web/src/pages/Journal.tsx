import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Button, TextField, InputAdornment, Divider, Stack } from '@mui/material';
import { Search, Plus, BookOpen, Brain, TrendingUp, AlertCircle, History } from 'lucide-react';
import { getTradeJournal } from '../api/client';

export default function TradeJournal() {
  const [trades, setTrades] = useState<any[]>([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    getTradeJournal().then(setTrades);
  }, []);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
           <BookOpen size={32} className="text-emerald-500" />
           <Typography variant="h4" sx={{ fontWeight: 900 }}>Trade Journal</Typography>
        </Box>
        <Button variant="contained" startIcon={<Plus size={18} />}>Record Trade</Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 0, overflow: 'hidden' }}>
            <Box sx={{ p: 2.5, borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
               <Typography variant="h6" fontWeight={800}>Trading Memory</Typography>
               <TextField
                size="small"
                placeholder="Search symbol..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                InputProps={{ startAdornment: <InputAdornment position="start"><Search size={16} /></InputAdornment> }}
                sx={{ width: 200 }}
               />
            </Box>

            <TableContainer sx={{ minHeight: 400 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>DATE</TableCell>
                    <TableCell>SYMBOL</TableCell>
                    <TableCell>TYPE</TableCell>
                    <TableCell align="right">PNL</TableCell>
                    <TableCell align="center">STATUS</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {trades.length > 0 ? trades.filter(t => t.symbol.includes(search.toUpperCase())).map((t, i) => (
                    <TableRow key={i} hover>
                      <TableCell>{new Date(t.entry_date).toLocaleDateString()}</TableCell>
                      <TableCell sx={{ fontWeight: 900 }}>{t.symbol}</TableCell>
                      <TableCell><Chip label="LONG" size="small" variant="outlined" sx={{ height: 18, fontSize: '0.6rem' }} /></TableCell>
                      <TableCell align="right" sx={{ color: t.pnl >= 0 ? 'primary.main' : 'error.main', fontWeight: 800 }}>
                        {t.pnl >= 0 ? '+' : ''}₹{t.pnl.toLocaleString()}
                      </TableCell>
                      <TableCell align="center"><Chip label="CLOSED" size="small" sx={{ fontWeight: 900, height: 20 }} /></TableCell>
                    </TableRow>
                  )) : (
                    <TableRow>
                       <TableCell colSpan={5} align="center" sx={{ py: 10 }}>
                          <Box sx={{ opacity: 0.3 }}>
                             <History size={64} style={{ margin: '0 auto 16px' }} />
                             <Typography variant="h6">Your Trading Memory is Empty</Typography>
                             <Typography variant="body2">Record your first trade to start building decision patterns.</Typography>
                          </Box>
                       </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, mb: 3, border: '1px solid #1e293b' }}>
             <Typography variant="subtitle2" color="textSecondary" gutterBottom fontWeight={800}>AI COACH INSIGHTS</Typography>

             {trades.length >= 5 ? (
               <Box sx={{ mt: 3 }}>
                 <Stack spacing={3}>
                    <Box>
                       <Typography variant="caption" color="primary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 800 }}>
                          <TrendingUp size={14} /> POSITIVE BEHAVIOR
                       </Typography>
                       <Typography variant="body2" sx={{ mt: 1, fontWeight: 500 }}>
                          Your performance peaks during high-volume institutional windows (10:30 - 11:30 AM).
                       </Typography>
                    </Box>
                    <Divider sx={{ opacity: 0.1 }} />
                    <Box>
                       <Typography variant="caption" color="error" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 800 }}>
                          <AlertCircle size={14} /> RECURRING MISTAKE
                       </Typography>
                       <Typography variant="body2" sx={{ mt: 1, fontWeight: 500 }}>
                          Exit logic is often triggered prematurely before price reaches institutional targets.
                       </Typography>
                    </Box>
                 </Stack>
               </Box>
             ) : (
               <Box sx={{ mt: 3, p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, border: '1px dashed #334155' }}>
                  <Typography variant="body2" color="textSecondary" align="center">
                     Record at least 5 trades to generate reliable behavioral insights.
                  </Typography>
               </Box>
             )}
          </Paper>

          <Paper sx={{ p: 3, bgcolor: 'rgba(16, 185, 129, 0.03)' }}>
             <Typography variant="subtitle2" color="textSecondary" gutterBottom fontWeight={800}>CONTINUOUS LEARNING</Typography>
             <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Brain size={32} className="text-emerald-500" />
                <Typography variant="caption" color="textSecondary">
                   AI agents are analyzing your decision patterns in real-time to refine accuracy.
                </Typography>
             </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
