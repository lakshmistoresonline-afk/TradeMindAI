import { useState, useMemo } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, TextField, InputAdornment, Stack, Tabs, Tab, Button, Pagination } from '@mui/material';
import { Search, TrendingUp, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface LiveSignalsBoardProps {
  stocks: any[];
}

export default function LiveSignalsBoard({ stocks }: LiveSignalsBoardProps) {
  const navigate = useNavigate();
  const [tab, setTab] = useState('ALL');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const rowsPerPage = 5;

  const filteredSignals = useMemo(() => {
    return stocks.filter(s => {
      if (!s.analysis) return false;
      const decision = s.decision;
      const matchesSearch = s.symbol.toLowerCase().includes(search.toLowerCase());

      let matchesTab = true;
      if (tab === 'BUY') matchesTab = decision.rating.includes('BUY');
      if (tab === 'SELL') matchesTab = decision.rating.includes('SELL');
      if (tab === 'HIGH_CONVICTION') matchesTab = decision.conviction >= 80;

      return matchesSearch && matchesTab;
    }).sort((a, b) => b.decision.conviction - a.decision.conviction);
  }, [stocks, search, tab]);

  const pagedData = filteredSignals.slice((page - 1) * rowsPerPage, page * rowsPerPage);

  return (
    <Paper sx={{ p: 0, border: '1px solid #1e293b', overflow: 'hidden' }}>
      <Box sx={{ p: 2.5, borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
        <Stack direction="row" spacing={1} alignItems="center">
           <TrendingUp size={18} className="text-emerald-500" />
           <Typography variant="subtitle2" sx={{ fontWeight: 900, letterSpacing: 1 }}>LIVE ACTIONABLE SIGNALS</Typography>
        </Stack>

        <Stack direction="row" spacing={2}>
           <TextField
             size="small"
             placeholder="Search symbol..."
             value={search}
             onChange={(e) => setSearch(e.target.value)}
             InputProps={{
               startAdornment: <InputAdornment position="start"><Search size={14} /></InputAdornment>,
               sx: { fontSize: '0.75rem', height: 32 }
             }}
           />
           <Chip label={`${filteredSignals.length} ACTIVE`} size="small" sx={{ fontWeight: 900, height: 32, bgcolor: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }} />
        </Stack>
      </Box>

      <Box sx={{ borderBottom: '1px solid #1e293b' }}>
         <Tabs value={tab} onChange={(_, v) => { setTab(v); setPage(1); }} sx={{ minHeight: 40 }}>
            <Tab label="ALL" value="ALL" sx={{ fontWeight: 800, fontSize: '0.7rem', minHeight: 40 }} />
            <Tab label="BUY ONLY" value="BUY" sx={{ fontWeight: 800, fontSize: '0.7rem', minHeight: 40 }} />
            <Tab label="SELL ONLY" value="SELL" sx={{ fontWeight: 800, fontSize: '0.7rem', minHeight: 40 }} />
            <Tab label="HIGH CONVICTION" value="HIGH_CONVICTION" sx={{ fontWeight: 800, fontSize: '0.7rem', minHeight: 40 }} />
         </Tabs>
      </Box>

      <TableContainer>
         <Table size="small">
            <TableHead>
               <TableRow sx={{ bgcolor: 'rgba(255,255,255,0.01)' }}>
                  <TableCell>SYMBOL</TableCell>
                  <TableCell align="center">ACTION</TableCell>
                  <TableCell align="right">CONVICTION</TableCell>
                  <TableCell align="right">ENTRY</TableCell>
                  <TableCell align="right">TARGET</TableCell>
                  <TableCell align="right">STOP LOSS</TableCell>
                  <TableCell align="center">STATUS</TableCell>
                  <TableCell align="center">RESEARCH</TableCell>
               </TableRow>
            </TableHead>
            <TableBody>
               {pagedData.length > 0 ? pagedData.map((s) => (
                  <TableRow key={s.symbol} hover>
                     <TableCell sx={{ fontWeight: 900, fontSize: '0.85rem' }}>
                        {s.symbol}
                        <Typography variant="caption" color="textSecondary" sx={{ display: 'block', fontSize: '0.6rem' }}>{s.decision.timeframe}</Typography>
                     </TableCell>
                     <TableCell align="center">
                        <Chip
                          label={s.decision.rating}
                          size="small"
                          color={s.decision.rating.includes('BUY') ? 'primary' : s.decision.rating.includes('SELL') ? 'error' : 'warning'}
                          sx={{ fontWeight: 900, height: 18, fontSize: '0.6rem' }}
                        />
                        <Typography variant="caption" sx={{ display: 'block', mt: 0.5, fontWeight: 900, color: s.decision.rating.includes('BUY') ? 'primary.main' : 'error.main', fontSize: '0.5rem' }}>
                           {s.decision.rating.includes('BUY') ? 'LONG' : s.decision.rating.includes('SELL') ? 'SHORT' : 'NEUTRAL'}
                        </Typography>
                     </TableCell>
                     <TableCell align="right">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 1 }}>
                           <Typography variant="body2" sx={{ fontWeight: 800, fontFamily: 'JetBrains Mono' }}>{s.decision.conviction}%</Typography>
                           <Box sx={{ width: 30, height: 3, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 1 }}>
                              <Box sx={{ width: `${s.decision.conviction}%`, height: '100%', bgcolor: 'primary.main' }} />
                           </Box>
                        </Box>
                     </TableCell>
                     <TableCell align="right" sx={{ fontFamily: 'JetBrains Mono', fontWeight: 700 }}>
                        {s.decision.entry ? `₹${Math.round(s.decision.entry).toLocaleString()}` : '---'}
                     </TableCell>
                     <TableCell align="right" sx={{ fontFamily: 'JetBrains Mono', fontWeight: 800, color: 'primary.main' }}>
                        {s.decision.target ? `₹${Math.round(s.decision.target).toLocaleString()}` : '---'}
                     </TableCell>
                     <TableCell align="right" sx={{ fontFamily: 'JetBrains Mono', fontWeight: 800, color: 'error.main' }}>
                        {s.decision.stopLoss ? `₹${Math.round(s.decision.stopLoss).toLocaleString()}` : '---'}
                     </TableCell>
                     <TableCell align="center">
                        <Chip
                           label={s.decision.status.replace('_', ' ')}
                           size="small"
                           variant="outlined"
                           color={s.decision.status === 'ACTIVE' ? 'primary' : s.decision.status.includes('HIT') ? 'success' : 'default'}
                           sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900 }}
                        />
                        {s.decision.status === 'ACTIVE' && (
                           <Typography variant="caption" sx={{ display: 'block', mt: 0.5, fontWeight: 900, color: 'primary.main', fontSize: '0.5rem' }}>
                              {s.decision.profitPct !== undefined ? `${s.decision.profitPct >= 0 ? '+' : ''}${s.decision.profitPct.toFixed(2)}%` : 'TRACKING'}
                           </Typography>
                        )}
                     </TableCell>
                     <TableCell align="center">
                        <Button
                          size="small"
                          variant="text"
                          onClick={() => navigate('/analysis', { state: { symbol: s.symbol } })}
                          sx={{ fontWeight: 900, fontSize: '0.65rem', minWidth: 0, p: 0.5 }}
                        >
                           <ArrowRight size={14} />
                        </Button>
                     </TableCell>
                  </TableRow>
               )) : (
                  <TableRow>
                     <TableCell colSpan={8} sx={{ py: 6, textAlign: 'center' }}>
                        <Typography color="textSecondary" sx={{ fontWeight: 700, fontSize: '0.8rem' }}>
                           No actionable {tab.replace('_', ' ')} signals found in current session.
                        </Typography>
                     </TableCell>
                  </TableRow>
               )}
            </TableBody>
         </Table>
      </TableContainer>

      {filteredSignals.length > rowsPerPage && (
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'center', borderTop: '1px solid #1e293b' }}>
           <Pagination
             count={Math.ceil(filteredSignals.length / rowsPerPage)}
             page={page}
             onChange={(_, v) => setPage(v)}
             size="small"
             color="primary"
           />
        </Box>
      )}
    </Paper>
  );
}
