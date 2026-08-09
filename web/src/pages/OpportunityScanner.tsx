import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Tabs, Tab, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Button, Tooltip, Stack } from '@mui/material';
import { Trophy, TrendingUp, DollarSign, Zap, Star, Layout, ArrowRight, Activity, Info, RefreshCw } from 'lucide-react';
import { getStocks, getOpportunities } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';

export default function OpportunityScanner() {
  const navigate = useNavigate();
  const [tab, setTab] = useState(0);
  const [stocks, setStocks] = useState<any[]>([]);
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [stocksData, oppsData] = await Promise.all([
        getStocks(),
        getOpportunities()
      ]);
      setStocks(stocksData.map((s: any) => ({ ...s, decision: normalizeAITradeDecision(s) })));
      setOpportunities(oppsData);
    } catch (e) {
      console.error("Failed to fetch scanner data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getRankedData = () => {
    switch (tab) {
      case 0:
        // Sync with Market Command Center: Use canonical opportunities
        return opportunities.map(o => {
          const stock = stocks.find(s => s.symbol === o.symbol);
          return {
            ...stock,
            symbol: o.symbol,
            decision: stock?.decision || { conviction: o.conviction_score, rating: 'BUY' },
            type: o.type,
            reason: o.ai_thesis,
            isBootstrap: o.indicators?.includes('AI SCANNING...')
          };
        });
      case 1: return [...stocks].sort((a,b) => (b.change_pct || 0) - (a.change_pct || 0));
      case 2: return [...stocks].sort((a,b) => (a.pe_ratio || 999) - (b.pe_ratio || 999));
      case 3: return [...stocks].filter(s => s.decision.rating.includes('BUY')).sort((a,b) => b.decision.conviction - a.decision.conviction);
      case 4: return [...stocks].filter(s => s.change_pct > 0 && s.change_pct < 2).sort((a,b) => b.change_pct - a.change_pct);
      default: return stocks;
    }
  };

  const data = getRankedData().slice(0, 15);

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
         <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Trophy size={32} className="text-amber-500" />
            <Box>
               <Typography variant="h4" sx={{ fontWeight: 900 }}>Opportunity Scanner</Typography>
               <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>MULTI-AGENT ALPHA ENGINE</Typography>
            </Box>
         </Box>
         <Stack direction="row" spacing={2} alignItems="center">
            <Button
              size="small"
              startIcon={<RefreshCw size={14} className={loading ? 'animate-spin' : ''} />}
              onClick={fetchData}
              sx={{ fontWeight: 800 }}
            >
               Sync Hub
            </Button>
            <Chip icon={<Activity size={14} />} label="ENGINE: READY" color="primary" variant="outlined" sx={{ fontWeight: 900 }} />
         </Stack>
      </Box>

      <Paper sx={{ p: 0, overflow: 'hidden', border: '1px solid #1e293b' }}>
        <Tabs
          value={tab}
          onChange={(_, v) => setTab(v)}
          sx={{ px: 2, pt: 1, borderBottom: '1px solid #334155' }}
          variant="scrollable"
          scrollButtons="auto"
        >
           <Tab label="Highest Conviction" icon={<Star size={16} />} iconPosition="start" sx={{ fontWeight: 800 }} />
           <Tab label="Momentum Leaders" icon={<TrendingUp size={16} />} iconPosition="start" sx={{ fontWeight: 800 }} />
           <Tab label="Value Leaders" icon={<DollarSign size={16} />} iconPosition="start" sx={{ fontWeight: 800 }} />
           <Tab label="Quality Leaders" icon={<Zap size={16} />} iconPosition="start" sx={{ fontWeight: 800 }} />
           <Tab label="Emerging Setups" icon={<Layout size={16} />} iconPosition="start" sx={{ fontWeight: 800 }} />
        </Tabs>

        <TableContainer>
           <Table size="small">
              <TableHead>
                 <TableRow>
                    <TableCell align="center">RANK</TableCell>
                    <TableCell>SYMBOL</TableCell>
                    <TableCell align="right">AI CONVICTION</TableCell>
                    <TableCell align="center">STATUS</TableCell>
                    <TableCell align="right">CHANGE %</TableCell>
                    <TableCell align="center">AI RATING</TableCell>
                    <TableCell align="center">PRIMARY CATALYST</TableCell>
                    <TableCell align="center">ACTION</TableCell>
                 </TableRow>
              </TableHead>
              <TableBody>
                 {data.map((s, i) => {
                   const isBootstrap = s.isBootstrap || s.indicators?.includes('BOOTSTRAP');
                   return (
                   <TableRow
                     key={s.symbol}
                     hover
                     onClick={() => navigate('/analysis', { state: { symbol: s.symbol, fromScanner: true } })}
                     sx={{ cursor: 'pointer' }}
                   >
                      <TableCell align="center">
                         <Typography variant="body2" sx={{ fontWeight: 800, color: i < 3 ? 'primary.main' : 'text.secondary' }}>
                            #{i+1}
                         </Typography>
                      </TableCell>
                      <TableCell>
                         <Typography variant="body2" sx={{ fontWeight: 900 }}>{s.symbol}</Typography>
                         <Typography variant="caption" color="textSecondary" sx={{ display: 'block', fontSize: '0.6rem' }}>{s.sector || 'Scanning...'}</Typography>
                      </TableCell>
                      <TableCell align="right">
                         <Typography color="primary" fontWeight={900}>{s.decision.conviction}%</Typography>
                      </TableCell>
                      <TableCell align="center">
                         <Tooltip title={isBootstrap ? "Preliminary detection based on raw momentum. Deep AI analysis pending." : "Full institutional analysis completed."}>
                            <Chip
                               label={isBootstrap ? "PRELIMINARY" : "AI VALIDATED"}
                               size="small"
                               variant="filled"
                               sx={{
                                 height: 18, fontSize: '0.55rem', fontWeight: 900,
                                 bgcolor: isBootstrap ? 'rgba(251, 191, 36, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                                 color: isBootstrap ? '#fbbf24' : '#10b981'
                               }}
                            />
                         </Tooltip>
                      </TableCell>
                      <TableCell align="right" sx={{ color: s.change_pct >= 0 ? 'primary.main' : 'error.main', fontWeight: 800 }}>
                         {s.change_pct?.toFixed(2)}%
                      </TableCell>
                      <TableCell align="center">
                         <Chip
                            label={s.decision.rating}
                            color={s.decision.rating.includes('BUY') ? 'primary' : s.decision.rating.includes('SELL') ? 'error' : 'default'}
                            size="small"
                            variant="outlined"
                            sx={{ fontWeight: 900, minWidth: 80, height: 20, fontSize: '0.65rem' }}
                         />
                      </TableCell>
                      <TableCell align="center">
                         <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.65rem', fontWeight: 600 }}>
                            {s.decision.primaryCatalyst || s.type || 'Volume Spike'}
                         </Typography>
                      </TableCell>
                      <TableCell align="center">
                         <Button size="small" endIcon={<ArrowRight size={14} />} sx={{ fontWeight: 800, fontSize: '0.7rem' }}>Deep Research</Button>
                      </TableCell>
                   </TableRow>
                 )})}
              </TableBody>
           </Table>
        </TableContainer>
      </Paper>

      <Box sx={{ mt: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
         <Info size={14} className="text-slategray" />
         <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 500 }}>
            Opportunities are prioritized by institutional alignment, order block proximity, and multi-factor momentum alignment.
         </Typography>
      </Box>
    </Box>
  );
}
