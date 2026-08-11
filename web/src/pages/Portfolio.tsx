import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Button, TextField, IconButton, List, ListItem, ListItemText, ListItemSecondaryAction, Chip, LinearProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { Plus, Trash2, Briefcase, Activity, TrendingUp } from 'lucide-react';
import { getStocks } from '../api/client';
import PortfolioOptimization from '../components/Research/PortfolioOptimization';
import { useNavigate } from 'react-router-dom';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';

export default function Portfolio() {
  const navigate = useNavigate();
  // Mock holdings data for audit reconciliation
  const [holdings, setHoldings] = useState<any>({
    'RELIANCE': { qty: 10, avgPrice: 2420.50 },
    'TCS': { qty: 5, avgPrice: 3850.00 },
    'INFY': { qty: 20, avgPrice: 1540.25 }
  });

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
    if (newSymbol && !holdings[newSymbol.toUpperCase()]) {
      setHoldings({ ...holdings, [newSymbol.toUpperCase()]: { qty: 1, avgPrice: 0 } });
      setNewSymbol('');
    }
  };

  const handleRemove = (symbol: string) => {
    const newHoldings = { ...holdings };
    delete newHoldings[symbol];
    setHoldings(newHoldings);
  };

  const portfolioData = allStocks
    .filter(s => holdings[s.symbol])
    .map(s => {
       const h = holdings[s.symbol];
       const marketValue = s.last_price * h.qty;
       const investedValue = h.avgPrice * h.qty;
       const pnl = marketValue - investedValue;
       const pnlPct = investedValue > 0 ? (pnl / investedValue) * 100 : 0;
       return { ...s, ...h, marketValue, investedValue, pnl, pnlPct };
    });

  const totalMarketValue = portfolioData.reduce((acc, s) => acc + s.marketValue, 0);
  const totalPnL = portfolioData.reduce((acc, s) => acc + s.pnl, 0);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
           <Typography variant="h4" sx={{ fontWeight: 900 }}>Portfolio Hub</Typography>
           <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>INSTITUTIONAL RISK WATCH • v2.2 VALIDATED</Typography>
        </Box>
        <Chip label="AI Risk Guard Active" color="primary" variant="outlined" sx={{ fontWeight: 800 }} />
      </Box>

      <PortfolioOptimization />

      <Grid container spacing={3} sx={{ mb: 4 }}>
         <Grid item xs={12} md={3}>
            <SummaryCard label="TOTAL ASSET VALUE" value={`₹${totalMarketValue.toLocaleString()}`} icon={<Briefcase size={20} />} color="#3b82f6" />
         </Grid>
         <Grid item xs={12} md={3}>
            <SummaryCard label="UNREALIZED P&L" value={`₹${totalPnL.toLocaleString()}`} icon={<Activity size={20} />} color={totalPnL >= 0 ? "#10b981" : "#f43f5e"} />
         </Grid>
         <Grid item xs={12} md={3}>
            <SummaryCard label="BETA EXPOSURE" value="1.14" icon={<TrendingUp size={20} />} color="#fbbf24" />
         </Grid>
         <Grid item xs={12} md={3}>
            <SummaryCard label="DIVERSIFICATION" value="HIGH" icon={<Plus size={20} />} color="#10b981" />
         </Grid>
      </Grid>

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
              {Object.keys(holdings).map((symbol) => (
                <ListItem key={symbol} divider sx={{ borderColor: 'rgba(255,255,255,0.05)' }}>
                  <ListItemText
                    primary={symbol}
                    primaryTypographyProps={{ fontWeight: 900, fontSize: '0.9rem' }}
                    secondary={`${holdings[symbol].qty} Shares`}
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
          <Paper sx={{ p: 0, minHeight: 400, border: '1px solid #1e293b', overflow: 'hidden' }}>
            <Box sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 1, borderBottom: '1px solid #334155' }}>
              <Briefcase size={20} className="text-emerald-500" />
              <Typography variant="h6" fontWeight={800}>Holdings Intelligence</Typography>
            </Box>

            <TableContainer>
               <Table size="small">
                  <TableHead sx={{ bgcolor: 'rgba(255,255,255,0.01)' }}>
                     <TableRow>
                        <TableCell sx={{ pl: 3 }}>ASSET</TableCell>
                        <TableCell align="right">WEIGHT</TableCell>
                        <TableCell align="right">AVG PRICE</TableCell>
                        <TableCell align="right">MARKET PRICE</TableCell>
                        <TableCell align="right">P&L</TableCell>
                        <TableCell align="center">AI RATING</TableCell>
                     </TableRow>
                  </TableHead>
                  <TableBody>
                     {portfolioData.map((s) => (
                        <TableRow
                           key={s.symbol}
                           hover
                           onClick={() => navigate('/analysis', { state: { symbol: s.symbol, fromPortfolio: true } })}
                           sx={{ cursor: 'pointer' }}
                        >
                           <TableCell sx={{ pl: 3 }}>
                              <Typography variant="body2" fontWeight={900}>{s.symbol}</Typography>
                              <Typography variant="caption" color="textSecondary">{s.qty} Shares</Typography>
                           </TableCell>
                           <TableCell align="right">
                              <Typography variant="body2" fontWeight={800}>{((s.marketValue / (totalMarketValue || 1)) * 100).toFixed(1)}%</Typography>
                              <LinearProgress variant="determinate" value={(s.marketValue / (totalMarketValue || 1)) * 100} sx={{ height: 2, mt: 0.5 }} />
                           </TableCell>
                           <TableCell align="right" sx={{ fontFamily: 'JetBrains Mono' }}>
                              {s.avgPrice ? `₹${s.avgPrice.toLocaleString()}` : '---'}
                           </TableCell>
                           <TableCell align="right" sx={{ fontFamily: 'JetBrains Mono', fontWeight: 800 }}>
                              {s.last_price ? `₹${s.last_price.toLocaleString()}` : '---'}
                           </TableCell>
                           <TableCell align="right">
                              <Typography variant="body2" fontWeight={900} color={s.pnl >= 0 ? 'primary.main' : 'error.main'}>
                                 {s.pnl >= 0 ? '+' : ''}₹{Math.round(s.pnl).toLocaleString()}
                              </Typography>
                              <Typography variant="caption" color={s.pnl >= 0 ? 'primary.main' : 'error.main'} sx={{ fontWeight: 700 }}>
                                 {s.pnl >= 0 ? '+' : ''}{s.pnlPct.toFixed(2)}%
                              </Typography>
                           </TableCell>
                           <TableCell align="center">
                              <Chip
                                 label={s.decision.rating}
                                 size="small"
                                 color={s.decision.rating.includes('BUY') ? 'primary' : s.decision.rating.includes('SELL') ? 'error' : 'default'}
                                 sx={{ fontWeight: 900, height: 18, fontSize: '0.6rem' }}
                              />
                           </TableCell>
                        </TableRow>
                     ))}
                  </TableBody>
               </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function SummaryCard({ label, value, icon, color }: any) {
   return (
      <Paper sx={{ p: 2.5, border: '1px solid #1e293b', bgcolor: 'rgba(15, 23, 42, 0.3)', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
         <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5, alignItems: 'center' }}>
            <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800, letterSpacing: 0.5 }}>{label}</Typography>
            <Box sx={{ color, opacity: 0.8 }}>{icon}</Box>
         </Box>
         <Typography variant="h5" fontWeight={900} sx={{ fontFamily: 'JetBrains Mono' }}>{value}</Typography>
      </Paper>
   );
}
