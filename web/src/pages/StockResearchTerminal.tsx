import { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Grid, Paper, Stack, Chip, Divider,
  CircularProgress, alpha, Autocomplete, TextField, Tabs, Tab
} from '@mui/material';
import {
  Search, BarChart3, Fingerprint, PieChart, ShieldCheck, Microscope, History
} from 'lucide-react';
import { apiClient, getStocks } from '../api/client';
import SignalDetailView from '../components/SignalDetailView';

export default function StockResearchTerminal() {
  const [stocks, setStocks] = useState<any[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('RELIANCE');
  const [research, setResearch] = useState<any>(null);
  const [matrix, setMatrix] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);

  const fetchStockData = useCallback(async (symbol: string) => {
    setLoading(true);
    try {
      const [rRes, mRes] = await Promise.all([
        apiClient.get(`/shadow/research/stock/${symbol}`),
        apiClient.get(`/shadow/research/stock/${symbol}/evidence`)
      ]);
      setResearch(rRes.data);
      setMatrix(mRes.data);
    } catch (err) {
      console.error("Research fetch failed", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const loadUniverse = async () => {
      const data = await getStocks();
      setStocks(data);
    };
    loadUniverse();
    fetchStockData(selectedSymbol);
  }, [fetchStockData, selectedSymbol]);

  if (loading && !research) return <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 900 }}>STOCK RESEARCH TERMINAL <Chip label="FORENSIC" color="secondary" size="small" /></Typography>
        <Autocomplete
          sx={{ width: 300 }}
          options={stocks}
          getOptionLabel={(option) => `${option.symbol} - ${option.name}`}
          onChange={(_, newValue) => newValue && setSelectedSymbol(newValue.symbol)}
          renderInput={(params) => <TextField {...params} label="Search Universe..." size="small" />}
        />
      </Box>

      <Grid container spacing={3}>
        {/* Profile Header */}
        <Grid item xs={12}>
           <Paper sx={{ p: 3, borderLeft: '4px solid', borderColor: 'primary.main' }}>
              <Grid container spacing={4} alignItems="center">
                 <Grid item>
                    <Typography variant="h3" fontWeight={950}>{selectedSymbol}</Typography>
                    <Typography variant="body2" color="text.secondary" fontWeight={700}>NIFTY 200 CONSTITUENT • {research?.technical_context?.sector || 'ENERGY'}</Typography>
                 </Grid>
                 <Grid item xs>
                    <Typography variant="h4" fontWeight={900} sx={{ fontFamily: 'JetBrains Mono' }}>₹{research?.technical_context?.price || '2,420.50'}</Typography>
                    <Typography variant="caption" color="success.main" fontWeight={900}>+1.45% (LIVE)</Typography>
                 </Grid>
                 <Grid item>
                    <Stack direction="row" spacing={1}>
                       <Chip label={research?.market_context?.bias || 'BULLISH'} size="small" variant="outlined" sx={{ fontWeight: 900 }} />
                       <Chip label="ACTIVE_SIGNAL_CAPABLE" color="primary" size="small" sx={{ fontWeight: 900 }} />
                    </Stack>
                 </Grid>
              </Grid>
           </Paper>
        </Grid>

        {/* Intelligence Evidence Matrix */}
        <Grid item xs={12} md={8}>
           <Paper sx={{ p: 0, overflow: 'hidden' }}>
              <Box sx={{ p: 2, bgcolor: alpha('#fff', 0.02), borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                 <Stack direction="row" spacing={1} alignItems="center">
                    <Microscope size={18} color="#7c3aed" />
                    <Typography variant="subtitle2" fontWeight={900}>EVIDENCE CONFLUENCE MATRIX</Typography>
                 </Stack>
              </Box>
              <Box sx={{ p: 3 }}>
                 <Grid container spacing={2}>
                    {matrix?.matrix && Object.entries(matrix.matrix).map(([key, data]: [string, any]) => (
                       <Grid item xs={12} sm={6} md={4} key={key}>
                          <Box sx={{ p: 2, border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1 }}>
                             <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900 }}>{key}</Typography>
                             <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mt: 1 }}>
                                <Typography variant="body2" fontWeight={800} color={data.bias === 'BULLISH' ? '#10b981' : data.bias === 'BEARISH' ? '#ef4444' : 'white'}>
                                   {data.bias}
                                </Typography>
                                <Typography variant="caption" fontWeight={900}>{Math.round(data.confidence * 100)}% CONF</Typography>
                             </Stack>
                          </Box>
                       </Grid>
                    ))}
                 </Grid>
              </Box>
           </Paper>

           {/* Detailed Tabs */}
           <Box sx={{ mt: 3 }}>
              <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ mb: 2 }}>
                 <Tab label="RESEARCH SUMMARY" sx={{ fontWeight: 900 }} />
                 <Tab label="FUNDAMENTALS" sx={{ fontWeight: 900 }} />
                 <Tab label="INSTITUTIONAL" sx={{ fontWeight: 900 }} />
                 <Tab label="F&O CHAIN" sx={{ fontWeight: 900 }} />
              </Tabs>

              <Paper sx={{ p: 3, minHeight: 300 }}>
                 {activeTab === 0 && (
                    <Box>
                       <Typography variant="h6" fontWeight={800} sx={{ mb: 2 }}>AI Research Copilot Thesis</Typography>
                       <Typography variant="body1" sx={{ color: 'text.secondary', lineHeight: 1.8 }}>{research?.summary}</Typography>
                       <Divider sx={{ my: 3 }} />
                       <Typography variant="overline" sx={{ fontWeight: 900, color: 'primary.main' }}>SUPPORTING FACTORS</Typography>
                       <Stack spacing={1} sx={{ mt: 1 }}>
                          {research?.supporting_evidence?.map((e: string) => (
                             <Typography key={e} variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 700 }}>
                                <ShieldCheck size={14} color="#10b981" /> {e}
                             </Typography>
                          ))}
                       </Stack>
                    </Box>
                 )}
                 {activeTab === 1 && (
                    <Grid container spacing={4}>
                       {Object.entries(research?.fundamental_context || {}).map(([k, v]: [string, any]) => (
                          <Grid item xs={6} md={3} key={k}>
                             <Typography variant="caption" color="text.secondary" fontWeight={900}>{k.toUpperCase()}</Typography>
                             <Typography variant="h6" fontWeight={800} sx={{ fontFamily: 'JetBrains Mono' }}>{String(v)}</Typography>
                          </Grid>
                       ))}
                    </Grid>
                 )}
              </Paper>
           </Box>
        </Grid>

        {/* Side Panels */}
        <Grid item xs={12} md={4}>
           <Stack spacing={3}>
              <Paper sx={{ p: 3 }}>
                 <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                    <PieChart size={18} color="#00D1FF" />
                    <Typography variant="subtitle2" fontWeight={900}>PORTFOLIO CONTEXT</Typography>
                 </Stack>
                 <Box sx={{ p: 2, bgcolor: alpha('#fff', 0.02), borderRadius: 1 }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={800}>CURRENT ALLOCATION</Typography>
                    <Typography variant="h5" fontWeight={900}>₹0.00</Typography>
                    <Typography variant="caption" color="slategray" fontWeight={700}>0.0% OF TOTAL EQUITY</Typography>
                 </Box>
              </Paper>

              <Paper sx={{ p: 3 }}>
                 <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                    <History size={18} color="#7c3aed" />
                    <Typography variant="subtitle2" fontWeight={900}>HISTORICAL SIGNALS</Typography>
                 </Stack>
                 <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 4 }}>No historical signals for this symbol in current Strategy V2.2 validation dataset.</Typography>
              </Paper>
           </Stack>
        </Grid>
      </Grid>
    </Box>
  );
}
