import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, IconButton, TextField, InputAdornment, Button, LinearProgress, Stack } from '@mui/material';
import { Search, RefreshCw, BarChart2, ArrowRight } from 'lucide-react';
import { getStocks } from '../api/client';
import QuickResearchDrawer from '../components/Research/QuickResearchDrawer';

import { useNavigate } from 'react-router-dom';

export default function Market() {
  const navigate = useNavigate();
  const [stocks, setStocks] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  // Drawer State
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedStock, setSelectedStock] = useState<any>(null);

  const fetchStocks = async () => {
    setLoading(true);
    try {
      const data = await getStocks();
      setStocks(data);
    } catch (error) {
      console.error('Error fetching stocks:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStocks();
  }, []);

  const filteredStocks = stocks.filter(s =>
    s.symbol.toLowerCase().includes(search.toLowerCase()) ||
    (s.name && s.name.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>Market Data</Typography>
          <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
             AS OF: {new Date().toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}
          </Typography>
          <Button
            size="small"
            variant="outlined"
            startIcon={<RefreshCw size={16} className={loading ? 'animate-spin' : ''} />}
            onClick={fetchStocks}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
        <TextField
          size="small"
          placeholder="Search stocks..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search size={18} />
              </InputAdornment>
            ),
          }}
          sx={{ width: 300 }}
        />
      </Box>

      <Box sx={{ width: '100%', overflowX: 'auto' }}>
        <TableContainer component={Paper} sx={{ border: '1px solid #1e293b' }}>
          <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ pl: 3 }}>SYMBOL</TableCell>
              <TableCell>SECTOR</TableCell>
              <TableCell align="right">AI CONVICTION</TableCell>
              <TableCell align="center">GRADE</TableCell>
              <TableCell align="right">LAST PRICE</TableCell>
              <TableCell align="right">24H CHANGE</TableCell>
              <TableCell align="center">ACTIONS</TableCell>
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
                <TableCell sx={{ fontWeight: 900, fontSize: '1rem', pl: 3 }}>{stock.symbol}</TableCell>
                <TableCell>
                  <Chip label={stock.sector || 'N/A'} size="small" variant="outlined" sx={{ fontSize: '0.6rem', fontWeight: 700, borderRadius: 1 }} />
                </TableCell>
                <TableCell align="right">
                   <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 1 }}>
                      <Typography variant="body2" sx={{ fontFamily: 'JetBrains Mono', fontWeight: 800 }}>{stock.ai_investment_score || '--'}%</Typography>
                      <Box sx={{ width: 40 }}>
                        <LinearProgress variant="determinate" value={stock.ai_investment_score || 0} sx={{ height: 4, borderRadius: 2 }} />
                      </Box>
                   </Box>
                </TableCell>
                <TableCell align="center">
                   <Chip
                    label={stock.ai_investment_grade || 'B'}
                    size="small"
                    color={stock.ai_investment_grade?.includes('A') ? 'primary' : 'default'}
                    sx={{ fontWeight: 900, fontSize: '0.75rem', width: 40 }}
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
