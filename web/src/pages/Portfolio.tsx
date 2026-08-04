import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Grid, Button, TextField, IconButton, List, ListItem, ListItemText, ListItemSecondaryAction, Divider } from '@mui/material';
import { Plus, Trash2, TrendingUp, TrendingDown, Briefcase } from 'lucide-react';
import { getStocks } from '../api/client';

export default function Portfolio() {
  const [myStocks, setMyStocks] = useState<string[]>(['RELIANCE', 'TCS', 'INFY']);
  const [newSymbol, setNewSymbol] = useState('');
  const [allStocks, setAllStocks] = useState<any[]>([]);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const data = await getStocks();
        setAllStocks(data);
      } catch (error) {
        console.error('Error fetching stocks:', error);
      }
    };
    fetchStocks();
  }, []);

  const handleAdd = () => {
    if (newSymbol && !myStocks.includes(newSymbol.toUpperCase())) {
      setMyStocks([...myStocks, newSymbol.toUpperCase()]);
      setNewSymbol('');
    }
  };

  const handleRemove = (symbol: string) => {
    setMyStocks(myStocks.filter(s => s !== symbol));
  };

  const portfolioData = allStocks.filter(s => myStocks.includes(s.symbol));

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>My Portfolio</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>Add Asset</Typography>
            <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
              <TextField
                fullWidth
                size="small"
                placeholder="Symbol (e.g. RELIANCE)"
                value={newSymbol}
                onChange={(e) => setNewSymbol(e.target.value)}
              />
              <Button variant="contained" onClick={handleAdd} sx={{ minWidth: 0 }}><Plus size={20} /></Button>
            </Box>
          </Paper>

          <Paper>
            <List subheader={<Typography variant="subtitle2" sx={{ p: 2, pb: 1, color: 'slategray' }}>WATCHLIST</Typography>}>
              {myStocks.map((symbol) => (
                <ListItem key={symbol}>
                  <ListItemText primary={symbol} />
                  <ListItemSecondaryAction>
                    <IconButton edge="end" size="small" onClick={() => handleRemove(symbol)}>
                      <Trash2 size={16} />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, minHeight: 400 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
              <Briefcase size={20} className="text-emerald-500" />
              <Typography variant="h6">Holdings Analysis</Typography>
            </Box>

            {portfolioData.length > 0 ? (
              <Grid container spacing={2}>
                {portfolioData.map((stock) => (
                  <Grid item xs={12} key={stock.symbol}>
                    <Paper variant="outlined" sx={{ p: 2, backgroundColor: 'rgba(15, 23, 42, 0.3)' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box>
                          <Typography fontWeight="bold">{stock.symbol}</Typography>
                          <Typography variant="caption" color="textSecondary">{stock.name}</Typography>
                        </Box>
                        <Box sx={{ textAlign: 'right' }}>
                          <Typography fontWeight="bold">₹{stock.last_price?.toLocaleString()}</Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', color: '#10b981' }}>
                            <TrendingUp size={14} className="mr-1" />
                            <Typography variant="caption">AI: {stock.analysis?.consensus || 'HOLD'}</Typography>
                          </Box>
                        </Box>
                      </Box>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '300px' }}>
                <Typography color="textSecondary">Add stocks to your watchlist to see AI analysis.</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
