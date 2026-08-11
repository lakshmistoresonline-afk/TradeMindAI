import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Tabs, Tab, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Button, Stack } from '@mui/material';
import { Trophy, TrendingUp, DollarSign, Zap, Star, ArrowRight, Info, RefreshCw } from 'lucide-react';
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
    if (!Array.isArray(opportunities)) return [];

    switch (tab) {
      case 0:
        return opportunities.map(o => {
          const stock = Array.isArray(stocks) ? stocks.find(s => s.symbol === o.symbol) : null;
          return {
            ...stock,
            symbol: o.symbol,
            decision: stock?.decision || { conviction: o.conviction_score || 0, rating: 'BUY' },
            type: o.type || 'REVERSAL',
            reason: o.ai_thesis || ''
          };
        });
      case 1: return Array.isArray(stocks) ? [...stocks].sort((a,b) => (b.change_pct || 0) - (a.change_pct || 0)) : [];
      case 2: return Array.isArray(stocks) ? [...stocks].sort((a,b) => (a.pe_ratio || 999) - (b.pe_ratio || 999)) : [];
      case 3: return Array.isArray(stocks) ? [...stocks].filter(s => s.decision?.rating?.includes('BUY')).sort((a,b) => (b.decision?.conviction || 0) - (a.decision?.conviction || 0)) : [];
      default: return Array.isArray(stocks) ? stocks : [];
    }
  };

  const data = getRankedData().slice(0, 15);

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
         <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Trophy size={32} className="text-amber-500" />
            <Box>
               <Typography variant="h4" sx={{ fontWeight: 900 }}>Opportunity Discovery</Typography>
               <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>ALPHA SCANNER • REAL-TIME ALPHA GENERATION</Typography>
            </Box>
         </Box>
         <Stack direction="row" spacing={2} alignItems="center">
            <Button
              variant="outlined"
              size="small"
              startIcon={<RefreshCw size={14} className={loading ? 'animate-spin' : ''} />}
              onClick={fetchData}
              sx={{ fontWeight: 800 }}
            >
               RESYNC HUB
            </Button>
            <Chip icon={<Zap size={14} />} label="LIVE ALPHA ACTIVE" color="primary" variant="filled" sx={{ fontWeight: 900 }} />
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
           <Tab label="High Conviction" icon={<Star size={16} />} iconPosition="start" sx={{ fontWeight: 800 }} />
           <Tab label="Institutional Accumulation" icon={<TrendingUp size={16} />} iconPosition="start" sx={{ fontWeight: 800 }} />
           <Tab label="Value Alpha" icon={<DollarSign size={16} />} iconPosition="start" sx={{ fontWeight: 800 }} />
           <Tab label="SMC Breakouts" icon={<Zap size={16} />} iconPosition="start" sx={{ fontWeight: 800 }} />
        </Tabs>

        <TableContainer>
           <Table size="small">
              <TableHead>
                 <TableRow>
                    <TableCell align="center">RANK</TableCell>
                    <TableCell>SYMBOL</TableCell>
                    <TableCell align="right">CONVICTION</TableCell>
                    <TableCell align="center">R/R RATIO</TableCell>
                    <TableCell align="right">CHANGE %</TableCell>
                    <TableCell align="center">PRIMARY CATALYST</TableCell>
                    <TableCell align="center">ACTION</TableCell>
                 </TableRow>
              </TableHead>
              <TableBody>
                 {data.length > 0 ? data.map((s, i) => (
                   <TableRow
                     key={s.symbol || i}
                     hover
                     onClick={() => s.symbol && navigate('/analysis', { state: { symbol: s.symbol, fromScanner: true } })}
                     sx={{ cursor: 'pointer' }}
                   >
                      <TableCell align="center">
                         <Typography variant="body2" sx={{ fontWeight: 800, color: i < 3 ? 'primary.main' : 'text.secondary' }}>
                            #{i+1}
                         </Typography>
                      </TableCell>
                      <TableCell>
                         <Typography variant="body2" sx={{ fontWeight: 900 }}>{s.symbol || '---'}</Typography>
                         <Typography variant="caption" color="textSecondary" sx={{ display: 'block', fontSize: '0.65rem', fontWeight: 700 }}>{s.sector || 'Scanning...'}</Typography>
                      </TableCell>
                      <TableCell align="right">
                         <Stack direction="row" spacing={1} alignItems="center" justifyContent="flex-end">
                            <Typography color="primary" fontWeight={900}>{s.decision?.conviction || 0}%</Typography>
                            <Box sx={{ width: 40, height: 4, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 2 }}>
                               <Box sx={{ width: `${s.decision?.conviction || 0}%`, height: '100%', bgcolor: 'primary.main', borderRadius: 2 }} />
                            </Box>
                         </Stack>
                      </TableCell>
                      <TableCell align="center">
                         <Typography variant="body2" sx={{ fontWeight: 800, fontFamily: 'JetBrains Mono' }}>{s.decision?.riskReward || '1:2.0'}</Typography>
                      </TableCell>
                      <TableCell align="right" sx={{ color: (s.change_pct || 0) >= 0 ? 'primary.main' : 'error.main', fontWeight: 800 }}>
                         {(s.change_pct || 0) >= 0 ? '+' : ''}{s.change_pct?.toFixed(2) || '0.00'}%
                      </TableCell>
                      <TableCell align="center">
                         <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.65rem', fontWeight: 800, textTransform: 'uppercase' }}>
                            {s.decision?.primaryCatalyst || s.type || 'Volume Spike'}
                         </Typography>
                      </TableCell>
                      <TableCell align="center">
                         <Button
                           size="small"
                           endIcon={<ArrowRight size={14} />}
                           sx={{ fontWeight: 900, fontSize: '0.65rem', color: 'primary.main' }}
                         >
                           FORENSIC LAB
                         </Button>
                      </TableCell>
                   </TableRow>
                 )) : (
                   <TableRow>
                      <TableCell colSpan={8} sx={{ py: 10, textAlign: 'center' }}>
                         <Typography color="textSecondary" sx={{ fontWeight: 700 }}>
                            {loading ? "Synchronizing institutional setups..." : "No active opportunities detected for current filters."}
                         </Typography>
                         {!loading && <Button variant="text" size="small" onClick={fetchData} sx={{ mt: 1 }}>Retry Sync</Button>}
                      </TableCell>
                   </TableRow>
                 )}
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
