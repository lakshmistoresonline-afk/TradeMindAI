import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Grid, Autocomplete, TextField, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Tabs, Tab, alpha, Skeleton } from '@mui/material';
import { Search, Activity, Zap, TrendingUp, Info } from 'lucide-react';
import {
  getStocks,
  getBacktestSignals,
  getStockDetail
} from '../api/client';

import ResearchHeader from '../components/Research/ResearchHeader';
import AIInvestmentThesis from '../components/Research/decision/AIInvestmentThesis';
import HistoricalPatternMatch from '../components/Research/decision/HistoricalPatternMatch';
import SignalLifecycleTimeline from '../components/Research/shared/SignalLifecycleTimeline';
import ConfluenceMatrix from '../components/Research/shared/ConfluenceMatrix';

import TechnicalAnalysis from '../components/Research/market/TechnicalAnalysis';
import MarketStructure from '../components/Research/market/MarketStructure';
import MTFAlignmentMatrix from '../components/Research/market/MTFAlignmentMatrix';
import CorrelationAndHedging from '../components/Research/market/CorrelationAndHedging';

import FundamentalAnalysis from '../components/Research/fundamentals/FundamentalAnalysis';
import EarningsIntelligence from '../components/Research/fundamentals/EarningsIntelligence';
import PeerBenchmark from '../components/Research/fundamentals/PeerBenchmark';

import InstitutionalPositioning from '../components/Research/institutional/InstitutionalPositioning';
import OptionsIntelligence from '../components/Research/options/OptionsIntelligence';
import OptionChainTable from '../components/Research/options/OptionChainTable';

import QuantAnalytics from '../components/Research/quant/QuantAnalytics';
import StockQualityProfile from '../components/Research/fundamentals/StockQualityProfile';
import ResearchNotebook from '../components/Research/ResearchNotebook';

import { useLocation } from 'react-router-dom';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';
import { useNotification } from '../components/Layout';

export default function StockIntelligence() {
  const location = useLocation();
  const { setCopilotContext } = useNotification();
  const [stocks, setStocks] = useState<any[]>([]);
  const [selectedStock, setSelectedStock] = useState<any | null>(null);
  const [backtestSignals, setBacktestSignals] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);

  const decision = selectedStock ? normalizeAITradeDecision(selectedStock) : null;

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const data = await getStocks();
        setStocks(data);

        // Handle direct navigation via state (e.g. clicking a signal)
        if (location.state?.symbol) {
           handleSymbolSelection(location.state.symbol);
        }
      } catch (error) {
        console.error('Error fetching stocks:', error);
      }
    };
    fetchInitialData();
  }, [location.state]);

  const handleSymbolSelection = async (symbol: string) => {
    setLoading(true);
    try {
        const detail = await getStockDetail(symbol);
        if (detail && !detail.error) {
            setSelectedStock(detail);
            setCopilotContext(detail);
            fetchSignals(symbol);
        }
    } catch (error) {
        console.error('Error fetching stock detail:', error);
    } finally {
        setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedStock) {
      setCopilotContext(selectedStock);
      fetchSignals(selectedStock.symbol);
    } else {
      setCopilotContext(null);
    }
  }, [selectedStock, setCopilotContext]);

  const fetchSignals = async (symbol: string) => {
    try {
      const data = await getBacktestSignals(symbol);
      setBacktestSignals(data);
    } catch (error) {
      console.error('Error fetching signals:', error);
    }
  };

  return (
    <Box sx={{ pb: 10 }}>
      {/* Header Tier */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: { xs: 'stretch', sm: 'center' }, mb: 5, flexDirection: { xs: 'column', sm: 'row' }, gap: 3 }}>
        <Box sx={{ minWidth: 0 }}>
            <Typography variant="h3" sx={{ fontWeight: 900, letterSpacing: -1 }}>Signal Laboratory</Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 800, letterSpacing: 1.5, mt: 0.5, display: 'block' }}>
                DEEP FORENSIC INSTRUMENT ANALYSIS
            </Typography>
        </Box>

        <Autocomplete
          sx={{ width: { xs: '100%', sm: 420 } }}
          options={stocks}
          getOptionLabel={(option) => `${option.symbol} - ${option.name}`}
          onChange={(_, newValue) => newValue && handleSymbolSelection(newValue.symbol)}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Search Instrument..."
              placeholder="e.g. RELIANCE"
            />
          )}
        />
      </Box>

      {loading ? (
         <Box sx={{ py: 10 }}>
            <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2, mb: 4 }} />
            <Grid container spacing={4}>
                <Grid item xs={12} lg={8}><Skeleton variant="rectangular" height={500} sx={{ borderRadius: 2 }} /></Grid>
                <Grid item xs={12} lg={4}><Skeleton variant="rectangular" height={500} sx={{ borderRadius: 2 }} /></Grid>
            </Grid>
         </Box>
      ) : selectedStock && decision ? (
        <Box>
          <ResearchHeader stock={selectedStock} />

          <Grid container spacing={4}>
             <Grid item xs={12} lg={8.5}>
                <Paper sx={{ mb: 4, p: 0, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.05)', bgcolor: '#0C1118' }}>
                   <Box sx={{ p: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                      <Stack direction="row" spacing={2} alignItems="center">
                         <Typography variant="h5" sx={{ fontWeight: 900, color: 'white' }}>{selectedStock.symbol} EXECUTION SNAPSHOT</Typography>
                         <Chip
                            label={decision.status?.replace(/_/g, ' ')}
                            size="small"
                            variant="outlined"
                            color="primary"
                            sx={{ fontWeight: 900, height: 20, borderRadius: 0.5 }}
                         />
                      </Stack>
                      <Stack direction="row" spacing={2}>
                         <Box sx={{ textAlign: 'right' }}>
                            <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>CONFIDENCE</Typography>
                            <Typography variant="h6" sx={{ fontWeight: 900, color: 'primary.main', lineHeight: 1 }}>{decision.conviction}%</Typography>
                         </Box>
                      </Stack>
                   </Box>

                   <Box sx={{ p: 4 }}>
                      <Grid container spacing={5}>
                         <Grid item xs={6} md={3}>
                            <LevelItem
                                label={decision.assetClass === 'OPTIONS' ? "ENTRY PREMIUM" : "ENTRY PRICE"}
                                value={decision.entry ? `₹${decision.entry.toLocaleString()}` : '—'}
                                color="white"
                            />
                         </Grid>
                         <Grid item xs={6} md={3}>
                            <LevelItem label="STOP LOSS" value={decision.stopLoss ? `₹${decision.stopLoss.toLocaleString()}` : '—'} color="#ef4444" />
                         </Grid>
                         <Grid item xs={6} md={3}>
                            <LevelItem label="PRIMARY TARGET" value={decision.target ? `₹${decision.target.toLocaleString()}` : '—'} color="#10b981" />
                         </Grid>
                         <Grid item xs={6} md={3}>
                            <LevelItem label="RISK / REWARD" value={decision.riskReward || '—'} color="#00D1FF" />
                         </Grid>
                      </Grid>

                      <Box sx={{ mt: 6 }}>
                         <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 3, letterSpacing: 1 }}>SIGNAL AUDIT TRAIL</Typography>
                         <SignalLifecycleTimeline
                            events={decision.events || []}
                            currentStatus={decision.status}
                         />
                      </Box>
                   </Box>
                </Paper>

                <Box sx={{ mb: 4, borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                   <Tabs
                     value={activeTab}
                     onChange={(_, v) => setActiveTab(v)}
                     textColor="primary"
                     indicatorColor="primary"
                     variant="scrollable"
                     scrollButtons="auto"
                     sx={{ '& .MuiTab-root': { fontWeight: 900, fontSize: '0.75rem', textTransform: 'none' } }}
                   >
                      <Tab label="Thesis & Evidence" icon={<Activity size={16} />} iconPosition="start" />
                      <Tab label="Technical & Quant" icon={<TrendingUp size={16} />} iconPosition="start" />
                      <Tab label="Fundamentals" icon={<Info size={16} />} iconPosition="start" />
                      <Tab label="Institutional & Options" icon={<Zap size={16} />} iconPosition="start" />
                      <Tab label="Historical Accuracy" icon={<Search size={16} />} iconPosition="start" />
                   </Tabs>
                </Box>

                <Box>
                   {activeTab === 0 && (
                     <Grid container spacing={3}>
                        <Grid item xs={12} md={7}>
                           <AIInvestmentThesis stock={selectedStock} />
                        </Grid>
                        <Grid item xs={12} md={5}>
                           <ConfluenceMatrix stock={selectedStock} />
                        </Grid>
                     </Grid>
                   )}

                   {activeTab === 1 && (
                     <Box>
                        <TechnicalAnalysis data={selectedStock.analysis?.technical_data} />
                        <MTFAlignmentMatrix symbol={selectedStock.symbol} />
                        <MarketStructure smc={selectedStock.analysis?.technical_data?.smc} />
                        <QuantAnalytics metrics={selectedStock.analysis?.technical_data?.quant_metrics || {}} />
                     </Box>
                   )}

                   {activeTab === 2 && (
                     <Box>
                        <FundamentalAnalysis stock={selectedStock} />
                        <EarningsIntelligence symbol={selectedStock.symbol} />
                        <PeerBenchmark stock={selectedStock} />
                     </Box>
                   )}

                   {activeTab === 3 && (
                     <Box>
                        <InstitutionalPositioning stock={selectedStock} />
                        <OptionsIntelligence stock={selectedStock} />
                        <Box sx={{ mt: 4 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 3 }}>LIVE OPTION CHAIN</Typography>
                            <OptionChainTable symbol={selectedStock.symbol} />
                        </Box>
                        <CorrelationAndHedging symbol={selectedStock.symbol} />
                     </Box>
                   )}

                   {activeTab === 4 && (
                     <Box>
                        <HistoricalPatternMatch symbol={selectedStock.symbol} />
                        <Paper sx={{ p: 4, mt: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                          <Typography variant="h5" fontWeight={900}>Model Validation Log</Typography>
                          {backtestSignals.length > 0 ? (
                            <TableContainer sx={{ mt: 3 }}>
                              <Table size="small">
                                <TableHead>
                                  <TableRow>
                                    <TableCell>DATE</TableCell>
                                    <TableCell align="right">ENTRY</TableCell>
                                    <TableCell align="right">RESULT %</TableCell>
                                    <TableCell align="center">OUTCOME</TableCell>
                                  </TableRow>
                                </TableHead>
                                <TableBody>
                                  {backtestSignals.map((sig, i) => (
                                    <TableRow key={i} hover>
                                      <TableCell>{new Date(sig.date).toLocaleDateString()}</TableCell>
                                      <TableCell align="right">₹{sig.entry.toLocaleString()}</TableCell>
                                      <TableCell align="right" sx={{ fontWeight: 900, color: sig.profit_pct >= 0 ? '#10b981' : '#ef4444' }}>
                                        {sig.profit_pct.toFixed(2)}%
                                      </TableCell>
                                      <TableCell align="center">
                                        <Chip label={sig.outcome} size="small" sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900, borderRadius: 0.5 }} />
                                      </TableCell>
                                    </TableRow>
                                  ))}
                                </TableBody>
                              </Table>
                            </TableContainer>
                          ) : (
                            <Box sx={{ py: 6, textAlign: 'center' }}>
                              <Typography color="textSecondary" variant="body2" sx={{ fontWeight: 700 }}>No historical audit data found for this symbol.</Typography>
                            </Box>
                          )}
                        </Paper>
                     </Box>
                   )}
                </Box>
             </Grid>

             <Grid item xs={12} lg={3.5}>
                <Stack spacing={3}>
                   <Paper sx={{ p: 3, border: '1px solid rgba(255,255,255,0.05)', bgcolor: '#0C1118' }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 900, color: 'primary.main', mb: 2 }}>DATA LINEAGE</Typography>
                      <Box sx={{ mb: 2 }}>
                         <Typography variant="caption" color="textSecondary" display="block">SIGNAL ORIGIN</Typography>
                         <Typography variant="body2" fontWeight={800}>TradeMind Quant V2.2</Typography>
                      </Box>
                      <Box sx={{ mb: 2 }}>
                         <Typography variant="caption" color="textSecondary" display="block">LAST RECONCILIATION</Typography>
                         <Typography variant="body2" fontWeight={800}>{selectedStock.updated_at ? new Date(selectedStock.updated_at).toLocaleString() : '—'}</Typography>
                      </Box>
                      <Box>
                         <Typography variant="caption" color="textSecondary" display="block">DATA FRESHNESS</Typography>
                         <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
                            <Chip label="LIVE FEED" size="small" sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900, bgcolor: alpha('#10b981', 0.1), color: '#10b981' }} />
                            <Chip label="AUDITED" size="small" sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900, bgcolor: 'rgba(255,255,255,0.05)' }} />
                         </Stack>
                      </Box>
                   </Paper>

                   <StockQualityProfile metrics={selectedStock.health_metrics} />
                   <ResearchNotebook symbol={selectedStock.symbol} />
                </Stack>
             </Grid>
          </Grid>
        </Box>
      ) : (
        <Paper sx={{ p: 10, textAlign: 'center', bgcolor: alpha('#0C1118', 0.5), border: '1px dashed rgba(255,255,255,0.1)' }}>
          <Search size={64} className="text-slategray mb-4 opacity-20" />
          <Typography variant="h5" color="textSecondary" sx={{ mb: 1, fontWeight: 800 }}>Signal Laboratory Offline</Typography>
          <Typography color="textSecondary" sx={{ fontWeight: 500 }}>Select a verified instrument from the search box to begin forensic auditing.</Typography>
        </Paper>
      )}
    </Box>
  );
}

function LevelItem({ label, value, color }: any) {
  return (
    <Box>
       <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 900, letterSpacing: 1 }}>{label}</Typography>
       <Typography variant="h5" sx={{ fontWeight: 900, color, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
    </Box>
  );
}
