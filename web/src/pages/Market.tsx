import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, IconButton, TextField, InputAdornment, Button } from '@mui/material';
import { Search, Info, TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';
import { getStocks } from '../api/client';

import { useNavigate } from 'react-router-dom';

export default function Market() {
  const navigate = useNavigate();
  const [stocks, setStocks] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

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

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Sector</TableCell>
              <TableCell align="right">Last Price</TableCell>
              <TableCell align="right">Market Cap</TableCell>
              <TableCell align="center">Action</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredStocks.map((stock) => (
              <TableRow key={stock.symbol} hover>
                <TableCell sx={{ fontWeight: 'bold' }}>{stock.symbol}</TableCell>
                <TableCell>{stock.name || 'N/A'}</TableCell>
                <TableCell>
                  <Chip label={stock.sector || 'N/A'} size="small" variant="outlined" />
                </TableCell>
                <TableCell align="right">
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                    {stock.last_price > 2500 ? <TrendingUp size={16} className="text-emerald-500 mr-1" /> : <TrendingDown size={16} className="text-rose-500 mr-1" />}
                    ₹{stock.last_price?.toLocaleString()}
                  </Box>
                </TableCell>
                <TableCell align="right">₹{(stock.market_cap / 1e11).toFixed(2)}T</TableCell>
                <TableCell align="center">
                  <IconButton
                    size="small"
                    color="primary"
                    onClick={() => navigate('/analysis', { state: { symbol: stock.symbol } })}
                  >
                    <Info size={18} />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
            {filteredStocks.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 8 }}>
                  <Typography color="textSecondary">No stocks found in the database.</Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
