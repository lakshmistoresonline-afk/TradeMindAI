import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Paper, Grid, Stack, TextField, MenuItem, Slider, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, alpha } from '@mui/material';
import { Search, Filter, ArrowRight, TrendingUp, Zap, Target } from 'lucide-react';
import { getStocks, getLiveSignalsAudit } from '../api/client';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';
import { useNavigate } from 'react-router-dom';

export default function EquityScanner() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stocks, setStocks] = useState<any[]>([]);

  // Filters
  const [signalFilter, setSignalFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ACTIVE');
  const [minProb, setMinProb] = useState(50);
  const [minRR, setMinRR] = useState(1.0);
  const [sectorFilter, setSectorFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [stocksData, signalsData] = await Promise.all([getStocks(), getLiveSignalsAudit()]);
      const stockMap = new Map((stocksData || []).map((s: any) => [s.symbol, s]));

      const combined = (signalsData || [])
        .filter((s: any) => s.asset_class === 'EQUITY' || !s.asset_class)
        .map((s: any) => {
            const stockInfo = stockMap.get(s.symbol) || {};
            return {
                ...stockInfo,
                ...s,
                decision: normalizeAITradeDecision({...stockInfo, ...s})
            };
        });
      setStocks(combined);
    } catch (e) {
      console.error("Scanner data sync failed:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const sectors = useMemo(() => {
    const s = new Set(stocks.map(x => x.sector).filter(Boolean));
    return ['ALL', ...Array.from(s)];
  }, [stocks]);

  const filteredData = useMemo(() => {
    return stocks.filter(s => {
      const matchesSignal = signalFilter === 'ALL' || s.decision.rating.includes(signalFilter);
      const matchesStatus = statusFilter === 'ALL' || s.status === statusFilter;
      const matchesProb = (s.calibrated_probability * 100) >= minProb;
      const matchesRR = (s.risk_reward_ratio || 1.0) >= minRR;
      const matchesSector = sectorFilter === 'ALL' || s.sector === sectorFilter;
      const matchesSearch = s.symbol.toLowerCase().includes(searchQuery.toLowerCase());

      return matchesSignal && matchesStatus && matchesProb && matchesRR && matchesSector && matchesSearch;
    }).sort((a, b) => (b.calibrated_probability || 0) - (a.calibrated_probability || 0));
  }, [stocks, signalFilter, statusFilter, minProb, minRR, sectorFilter, searchQuery]);

  return (
    <Box sx={{ pb: 8 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>NIFTY-200 EQUITY SCANNER</Typography>
        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
           INSTITUTIONAL RESEARCH TERMINAL • STRATEGY V2.2
        </Typography>
      </Box>

      {/* Filter Panel */}
      <Paper sx={{ p: 3, mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
        <Grid container spacing={3} alignItems="center">
           <Grid item xs={12} md={2}>
              <TextField
                select
                fullWidth
                label="SIGNAL"
                value={signalFilter}
                onChange={(e) => setSignalFilter(e.target.value)}
                size="small"
              >
                 <MenuItem value="ALL">ALL</MenuItem>
                 <MenuItem value="BUY">BUY</MenuItem>
                 <MenuItem value="SELL">SELL</MenuItem>
              </TextField>
           </Grid>
           <Grid item xs={12} md={2}>
              <TextField
                select
                fullWidth
                label="STATUS"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                size="small"
              >
                 <MenuItem value="ALL">ALL</MenuItem>
                 <MenuItem value="ACTIVE">ACTIVE</MenuItem>
                 <MenuItem value="CLOSED">CLOSED</MenuItem>
              </TextField>
           </Grid>
           <Grid item xs={12} md={3}>
              <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900 }}>MIN PROBABILITY: {minProb}%</Typography>
              <Slider value={minProb} onChange={(_, v) => setMinProb(v as number)} size="small" />
           </Grid>
           <Grid item xs={12} md={2}>
              <TextField
                select
                fullWidth
                label="SECTOR"
                value={sectorFilter}
                onChange={(e) => setSectorFilter(e.target.value)}
                size="small"
              >
                 {sectors.map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
              </TextField>
           </Grid>
           <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="SEARCH TICKER"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                size="small"
                InputProps={{ startAdornment: <Search size={16} style={{ marginRight: 8, color: 'slategray' }} /> }}
              />
           </Grid>
        </Grid>
      </Paper>

      {/* Results Table */}
      <TableContainer component={Paper} sx={{ bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>SYMBOL</TableCell>
              <TableCell align="center">SIGNAL</TableCell>
              <TableCell align="right">PROBABILITY</TableCell>
              <TableCell align="center">EXPECTED VALUE</TableCell>
              <TableCell align="center">R:R</TableCell>
              <TableCell align="center">STATUS</TableCell>
              <TableCell align="right">ACTION</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredData.map((s) => (
              <TableRow key={s.id} hover>
                <TableCell>
                   <Typography sx={{ fontWeight: 900, fontSize: '0.85rem' }}>{s.symbol}</Typography>
                   <Typography variant="caption" sx={{ color: 'slategray' }}>{s.sector}</Typography>
                </TableCell>
                <TableCell align="center">
                   <Chip
                    label={s.direction}
                    size="small"
                    sx={{
                        height: 20,
                        fontSize: '0.65rem',
                        fontWeight: 900,
                        bgcolor: s.direction === 'LONG' ? alpha('#10b981', 0.1) : alpha('#ef4444', 0.1),
                        color: s.direction === 'LONG' ? '#10b981' : '#ef4444'
                    }}
                   />
                </TableCell>
                <TableCell align="right">
                   <Typography sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', color: 'primary.main' }}>
                      {(s.calibrated_probability * 100).toFixed(1)}%
                   </Typography>
                </TableCell>
                <TableCell align="center">
                   <Typography sx={{ fontWeight: 800, color: (s.expected_value || 0) > 0 ? '#10b981' : '#ef4444' }}>
                      {s.expected_value ? `₹${s.expected_value.toFixed(2)}` : '—'}
                   </Typography>
                </TableCell>
                <TableCell align="center">
                   <Typography sx={{ fontWeight: 800 }}>1:{s.risk_reward_ratio?.toFixed(1) || '1.0'}</Typography>
                </TableCell>
                <TableCell align="center">
                   <Typography variant="caption" sx={{ fontWeight: 900, color: s.status === 'ACTIVE' ? 'primary.main' : 'slategray' }}>
                      {s.status}
                   </Typography>
                </TableCell>
                <TableCell align="right">
                   <Button
                    size="small"
                    endIcon={<ArrowRight size={14} />}
                    onClick={() => navigate(`/signals/${s.id}`)}
                    sx={{ color: 'primary.main', fontWeight: 800 }}
                   >
                     ANALYZE
                   </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
