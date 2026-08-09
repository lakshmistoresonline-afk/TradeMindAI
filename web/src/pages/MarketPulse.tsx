import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, IconButton, TextField, InputAdornment, Button, LinearProgress, Stack, MenuItem, Select, FormControl, InputLabel } from '@mui/material';
import { Search, RefreshCw, BarChart2, ArrowRight } from 'lucide-react';
import { getStocks } from '../api/client';
import QuickResearchDrawer from '../components/Research/QuickResearchDrawer';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';

import { useNavigate } from 'react-router-dom';

export default function MarketPulse() {
  const navigate = useNavigate();
  const [stocks, setStocks] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  // Filters
  const [sectorFilter, setSectorFilter] = useState('ALL');
  const [ratingFilter, setRatingFilter] = useState('ALL');

  // Drawer State
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedStock, setSelectedStock] = useState<any>(null);

  const fetchStocks = async () => {
    setLoading(true);
    try {
      const data = await getStocks();
      setStocks(data.map((s: any) => ({ ...s, decision: normalizeAITradeDecision(s) })));
    } catch (error) {
      console.error('Error fetching stocks:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStocks();
  }, []);

  const sectors = ['ALL', ...new Set(stocks.map(s => s.sector).filter(Boolean))];
  const ratings = ['ALL', 'STRONG BUY', 'BUY', 'HOLD', 'SELL', 'STRONG SELL'];

  const filteredStocks = stocks.filter(s => {
    const matchesSearch = s.symbol.toLowerCase().includes(search.toLowerCase()) || (s.name && s.name.toLowerCase().includes(search.toLowerCase()));
    const matchesSector = sectorFilter === 'ALL' || s.sector === sectorFilter;
    const matchesRating = ratingFilter === 'ALL' || s.decision.rating === ratingFilter;
    return matchesSearch && matchesSector && matchesRating;
  });

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4, flexWrap: 'wrap', gap: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 900 }}>Market Pulse</Typography>
          <Typography variant="caption" color="textSecondary" sx={{ mt: 1, fontWeight: 700 }}>
             TERMINAL SYNC: {new Date().toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}
          </Typography>
        </Box>

        <Stack direction="row" spacing={2} alignItems="center" sx={{ flexGrow: 1, justifyContent: 'flex-end' }}>
          <TextField
            size="small"
            placeholder="Search universe..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search size={18} />
                </InputAdornment>
              ),
            }}
            sx={{ width: 250 }}
          />

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Sector</InputLabel>
            <Select value={sectorFilter} label="Sector" onChange={(e) => setSectorFilter(e.target.value)}>
              {sectors.map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Rating</InputLabel>
            <Select value={ratingFilter} label="Rating" onChange={(e) => setRatingFilter(e.target.value)}>
              {ratings.map(r => <MenuItem key={r} value={r}>{r}</MenuItem>)}
            </Select>
          </FormControl>

          <Button
            variant="outlined"
            startIcon={<RefreshCw size={16} className={loading ? 'animate-spin' : ''} />}
            onClick={fetchStocks}
            disabled={loading}
            sx={{ height: 40 }}
          >
            Refresh
          </Button>
        </Stack>
      </Box>

      <Box sx={{ width: '100%', overflowX: 'auto' }}>
        <TableContainer component={Paper} sx={{ border: '1px solid #1e293b' }}>
          <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ pl: 3 }}>SYMBOL</TableCell>
              <TableCell>SECTOR</TableCell>
              <TableCell align="right">CONVICTION</TableCell>
              <TableCell align="center">AI RATING</TableCell>
              <TableCell align="right">LAST PRICE</TableCell>
              <TableCell align="right">24H CHANGE</TableCell>
              <TableCell align="center">ACTION</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredStocks.map((stock) => (
              <TableRow
                key={stock.symbol}
                hover
                onClick={() => {
                   setSelectedStock(stock);
                   setDrawerOpen(true);
                }}
                sx={{ cursor: 'pointer' }}
              >
                <TableCell sx={{ fontWeight: 900, fontSize: '0.9rem', pl: 3 }}>{stock.symbol}</TableCell>
                <TableCell>
                  <Typography variant="caption" sx={{ fontWeight: 700, color: 'text.secondary' }}>{stock.sector || 'N/A'}</Typography>
                </TableCell>
                <TableCell align="right">
                   <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 1 }}>
                      <Typography variant="body2" sx={{ fontFamily: 'JetBrains Mono', fontWeight: 800 }}>{stock.decision.conviction}%</Typography>
                      <Box sx={{ width: 40 }}>
                        <LinearProgress
                          variant="determinate"
                          value={stock.decision.conviction}
                          color={stock.decision.rating.includes('BUY') ? 'primary' : stock.decision.rating.includes('SELL') ? 'error' : 'warning'}
                          sx={{ height: 4, borderRadius: 2 }}
                        />
                      </Box>
                   </Box>
                </TableCell>
                <TableCell align="center">
                   <Chip
                    label={stock.decision.rating}
                    size="small"
                    variant="outlined"
                    color={stock.decision.rating.includes('BUY') ? 'primary' : stock.decision.rating.includes('SELL') ? 'error' : 'default'}
                    sx={{ fontWeight: 900, fontSize: '0.65rem', minWidth: 80 }}
                   />
                </TableCell>
                <TableCell align="right" sx={{ fontFamily: 'JetBrains Mono', fontWeight: 700 }}>₹{stock.last_price?.toLocaleString()}</TableCell>
                <TableCell align="right">
                   <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5, color: (stock.change_pct || 0) >= 0 ? 'primary.main' : 'error.main' }}>
                      <Typography variant="body2" sx={{ fontFamily: 'JetBrains Mono', fontWeight: 800 }}>
                        {(stock.change_pct || 0) >= 0 ? '+' : ''}{stock.change_pct?.toFixed(2)}%
                      </Typography>
                   </Box>
                </TableCell>
                <TableCell align="center">
                  <Stack direction="row" spacing={1} justifyContent="center">
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate('/analysis', { state: { symbol: stock.symbol } });
                      }}
                    >
                      <BarChart2 size={18} />
                    </IconButton>
                    <IconButton size="small">
                       <ArrowRight size={18} />
                    </IconButton>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      </Box>

      <QuickResearchDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        stock={selectedStock}
      />
    </Box>
  );
}
