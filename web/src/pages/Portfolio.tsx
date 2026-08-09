import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Button, TextField, IconButton, List, ListItem, ListItemText, ListItemSecondaryAction, Chip, LinearProgress } from '@mui/material';
import { Plus, Trash2, Briefcase, Activity } from 'lucide-react';
import { getStocks } from '../api/client';
import PortfolioOptimization from '../components/Research/PortfolioOptimization';
import { useNavigate } from 'react-router-dom';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';

export default function Portfolio() {
  const navigate = useNavigate();
  const [myStocks, setMyStocks] = useState<string[]>(['RELIANCE', 'TCS', 'INFY']);
  const [newSymbol, setNewSymbol] = useState('');
  const [allStocks, setAllStocks] = useState<any[]>([]);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const data = await getStocks();
        setAllStocks(data.map((s: any) => ({ ...s, decision: normalizeAITradeDecision(s) })));
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
           <Typography variant="h4" sx={{ fontWeight: 900 }}>Portfolio</Typography>
           <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>INSTITUTIONAL RISK WATCH</Typography>
        </Box>
        <Chip label="AI Risk Guard Active" color="primary" variant="outlined" sx={{ fontWeight: 800 }} />
      </Box>

      <PortfolioOptimization />

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, mb: 3, border: '1px solid #1e293b' }}>
            <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 2, fontWeight: 800 }}>ADD INSTITUTIONAL ASSET</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                size="small"
                placeholder="Ticker e.g. HDFCBANK"
                value={newSymbol}
                onChange={(e) => setNewSymbol(e.target.value)}
              />
              <Button variant="contained" onClick={handleAdd} sx={{ minWidth: 48, borderRadius: 1 }}><Plus size={20} /></Button>
            </Box>
          </Paper>

          <Paper sx={{ border: '1px solid #1e293b', overflow: 'hidden' }}>
            <List subheader={<Typography variant="subtitle2" sx={{ p: 2, pb: 1, color: 'slategray', fontWeight: 800 }}>ACTIVE WATCHLIST</Typography>}>
              {myStocks.map((symbol) => (
                <ListItem key={symbol} divider sx={{ borderColor: 'rgba(255,255,255,0.05)' }}>
                  <ListItemText
                    primary={symbol}
                    primaryTypographyProps={{ fontWeight: 900, fontSize: '0.9rem' }}
                  />
                  <ListItemSecondaryAction>
                    <IconButton edge="end" size="small" onClick={() => handleRemove(symbol)} sx={{ color: 'error.main', opacity: 0.7 }}>
                      <Trash2 size={16} />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, minHeight: 400, border: '1px solid #1e293b' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
              <Briefcase size={20} className="text-emerald-500" />
              <Typography variant="h6" fontWeight={800}>Holdings Intelligence</Typography>
            </Box>

            {portfolioData.length > 0 ? (
              <Grid container spacing={2}>
                {portfolioData.map((stock) => (
                  <Grid item xs={12} key={stock.symbol}>
                    <Paper
                      variant="outlined"
                      onClick={() => navigate('/analysis', { state: { symbol: stock.symbol, fromPortfolio: true } })}
                      sx={{
                        p: 2.5, bgcolor: 'rgba(15, 23, 42, 0.5)',
                        border: '1px solid #1e293b', cursor: 'pointer',
                        '&:hover': { bgcolor: 'rgba(16, 185, 129, 0.05)', borderColor: 'primary.main' },
                        transition: '0.2s'
                      }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Box>
                          <Typography variant="h6" fontWeight={900}>{stock.symbol}</Typography>
                          <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>{stock.name}</Typography>
                          <Chip
                            label={stock.decision.rating}
                            size="small"
                            color={stock.decision.rating.includes('BUY') ? 'primary' : stock.decision.rating.includes('SELL') ? 'error' : 'default'}
                            sx={{ fontWeight: 800, height: 20, fontSize: '0.65rem' }}
                          />
                        </Box>
                        <Box sx={{ textAlign: 'right' }}>
                          <Typography variant="h6" sx={{ fontFamily: 'JetBrains Mono', fontWeight: 900 }}>₹{stock.last_price?.toLocaleString()}</Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 1, mt: 1 }}>
                             <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>CONVICTION</Typography>
                             <Typography variant="body2" color="primary" sx={{ fontWeight: 900 }}>{stock.decision.conviction}%</Typography>
                          </Box>
                          <Box sx={{ width: 100, mt: 0.5, ml: 'auto' }}>
                             <LinearProgress
                                variant="determinate"
                                value={stock.decision.conviction}
                                color={stock.decision.rating.includes('BUY') ? 'primary' : 'warning'}
                                sx={{ height: 3, borderRadius: 1 }}
                             />
                          </Box>
                        </Box>
                      </Box>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '300px', opacity: 0.3 }}>
                <Activity size={64} />
                <Typography variant="h6" sx={{ mt: 2, fontWeight: 800 }}>Empty Portfolio</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>Add institutional tickers to begin risk analysis.</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
