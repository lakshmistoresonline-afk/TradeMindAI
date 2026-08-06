import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, IconButton, TextField, InputAdornment, Button } from '@mui/material';
import { Search, RefreshCw } from 'lucide-react';
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

      <Box sx={{ width: '100%', overflowX: 'auto' }}>
        <TableContainer component={Paper}>
          <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell>Symbol</TableCell>
              <TableCell>Sector</TableCell>
              <TableCell align="right">AI Score</TableCell>
              <TableCell align="center">Grade</TableCell>
              <TableCell align="right">Last Price</TableCell>
              <TableCell align="right">Change %</TableCell>
              <TableCell align="center">Research</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredStocks.map((stock) => (
              <TableRow key={stock.symbol} hover>
                <TableCell sx={{ fontWeight: 'bold' }}>{stock.symbol}</TableCell>
                <TableCell>
                  <Chip label={stock.sector || 'N/A'} size="small" variant="outlined" sx={{ fontSize: '0.65rem' }} />
                </TableCell>
                <TableCell align="right">
                   <Typography color="primary" fontWeight="bold">{stock.ai_investment_score || '--'}</Typography>
                </TableCell>
                <TableCell align="center">
                   <Chip
                    label={stock.ai_investment_grade || 'B'}
                    size="small"
                    color="primary"
                    variant={stock.ai_investment_grade?.includes('A') ? 'filled' : 'outlined'}
                    sx={{ fontWeight: 'bold', fontSize: '0.7rem' }}
                   />
                </TableCell>
                <TableCell align="right">₹{stock.last_price?.toLocaleString()}</TableCell>
                <TableCell align="right" sx={{ color: (stock.change_pct || 0) >= 0 ? 'primary.main' : 'error.main' }}>
                   {stock.change_pct?.toFixed(2)}%
                </TableCell>
                <TableCell align="center">
                  <IconButton
                    size="small"
                    color="primary"
                    onClick={() => navigate('/analysis', { state: { symbol: stock.symbol } })}
                  >
                    <Search size={18} />
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
    </Box>
  );
}
