import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Grid, Autocomplete, TextField, Stack, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Tabs, Tab, Divider } from '@mui/material';
import { Search, History, FileText, Database, Activity, Brain, LineChart, BarChart4, ShieldAlert, Briefcase } from 'lucide-react';
import {
  getStocks, triggerBacktest, getBacktestResults,
  getBacktestSignals, getStockTimeline
} from '../api/client';

import ResearchHeader from '../components/Research/ResearchHeader';
import DecisionPanel from '../components/Research/decision/DecisionPanel';
import AIInvestmentThesis from '../components/Research/decision/AIInvestmentThesis';
import HistoricalPatternMatch from '../components/Research/decision/HistoricalPatternMatch';
import DecisionHistory from '../components/Research/decision/DecisionHistory';

import TechnicalAnalysis from '../components/Research/market/TechnicalAnalysis';
import MarketStructure from '../components/Research/market/MarketStructure';
import CorrelationAndHedging from '../components/Research/market/CorrelationAndHedging';

import FundamentalAnalysis from '../components/Research/fundamentals/FundamentalAnalysis';
import EarningsIntelligence from '../components/Research/fundamentals/EarningsIntelligence';
import PeerBenchmark from '../components/Research/fundamentals/PeerBenchmark';
import BusinessQualityAndMoat from '../components/Research/fundamentals/BusinessQualityAndMoat';
import StockQualityProfile from '../components/Research/fundamentals/StockQualityProfile';

import InstitutionalPositioning from '../components/Research/institutional/InstitutionalPositioning';
import OptionsIntelligence from '../components/Research/options/OptionsIntelligence';

import QuantAnalytics from '../components/Research/quant/QuantAnalytics';
import ScenarioStressLab from '../components/Research/quant/ScenarioStressLab';
import AIPerformance from '../components/Research/quant/AIPerformance';
import AIResearchTimeline from '../components/Research/AIResearchTimeline';
import ResearchNotebook from '../components/Research/ResearchNotebook';

import RiskAssessment from '../components/Research/risk/RiskAssessment';
import AICopilot from '../components/AICopilot';

import { useLocation } from 'react-router-dom';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';

export default function StockIntelligence() {
  const location = useLocation();
  const [stocks, setStocks] = useState<any[]>([]);
  const [selectedStock, setSelectedStock] = useState<any | null>(null);
  const [backtestReport, setBacktestReport] = useState<any | null>(null);
  const [backtestSignals, setBacktestSignals] = useState<any[]>([]);
  const [loadingBacktest, setLoadingBacktest] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    if (selectedStock) {
      // Logic for any global page state needed when stock changes
    }
  }, [selectedStock]);

  const fromPortfolio = location.state?.fromPortfolio || false;

  const generateReport = () => {
    if (!selectedStock) return;
    const decision = normalizeAITradeDecision(selectedStock);
    const content = `
# TRADE MIND AI: INSTITUTIONAL EQUITY RESEARCH
## ${selectedStock.name} (${selectedStock.symbol})

**Report Generated:** ${new Date().toLocaleString(undefined, { dateStyle: 'full', timeStyle: 'short' })}
**AI Conviction:** ${decision.conviction}%
**Grade:** ${selectedStock.ai_investment_grade || 'N/A'}
**Rating:** ${decision.rating}

### EXECUTIVE SUMMARY
${decision.thesis || 'Analysis pending for latest session dynamics.'}

### AI THESIS & DRIVERS
${decision.drivers?.map(d => `- ${d}`).join('\n') || '- Technical structure alignment\n- Institutional flow bias'}

### KEY CATALYST
${decision.primaryCatalyst || 'Breakout above major structural resistance.'}

### INVALIDATION
${decision.invalidation || 'Weekly close below major support zone.'}
`;
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedStock.symbol}_Institutional_Research.md`;
    a.click();
  };

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const data = await getStocks();
        setStocks(data);
        if (location.state?.symbol) {
           const stock = data.find((s: any) => s.symbol.toUpperCase() === location.state.symbol.toUpperCase());
           if (stock) setSelectedStock(stock);
        }
      } catch (error) {
        console.error('Error fetching stocks:', error);
      }
    };
    fetchStocks();
  }, [location.state]);

  useEffect(() => {
    if (selectedStock) {
      fetchBacktest(selectedStock.symbol);
      fetchSignals(selectedStock.symbol);
      getStockTimeline(selectedStock.symbol);
    }
  }, [selectedStock]);

  const fetchBacktest = async (symbol: string) => {
    try {
      const data = await getBacktestResults(symbol);
      setBacktestReport(data && !data.error ? data : null);
    } catch (error) {
      console.error('Error fetching backtest:', error);
    }
  };

  const fetchSignals = async (symbol: string) => {
    try {
      const data = await getBacktestSignals(symbol);
      setBacktestSignals(data);
    } catch (error) {
      console.error('Error fetching signals:', error);
    }
  };

  const handleRunBacktest = async () => {
    if (!selectedStock) return;
    setLoadingBacktest(true);
    try {
      await triggerBacktest(selectedStock.symbol);
      alert("Backtest triggered! Please check back in a few minutes.");
    } catch (error) {
      console.error('Error triggering backtest:', error);
    } finally {
      setLoadingBacktest(false);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: { xs: 'flex-start', sm: 'center' }, mb: 4, flexDirection: { xs: 'column', sm: 'row' }, gap: 2 }}>
        <Typography variant="h4" sx={{ fontWeight: 900 }}>Stock Intelligence</Typography>

        <Autocomplete
          sx={{ width: { xs: '100%', sm: 350 } }}
          options={stocks}
          getOptionLabel={(option) => `${option.symbol} - ${option.name}`}
          onChange={(_, newValue) => setSelectedStock(newValue)}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Search NSE Ticker..."
              size="small"
              placeholder="e.g. RELIANCE"
            />
          )}
        />
      </Box>

      {selectedStock ? (
        <Box>
          <ResearchHeader stock={selectedStock} />

          {fromPortfolio && (
            <Paper sx={{ p: 2, mb: 4, bgcolor: 'rgba(16, 185, 129, 0.05)', border: '1px solid #10b981', display: 'flex', alignItems: 'center', gap: 3, flexWrap: 'wrap' }}>
               <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Briefcase size={20} className="text-emerald-500" />
                  <Typography variant="subtitle2" fontWeight={800}>PORTFOLIO CONTEXT (MODEL)</Typography>
               </Box>
               <Divider orientation="vertical" flexItem sx={{ opacity: 0.1 }} />
               <Box>
                  <Typography variant="caption" color="textSecondary" display="block">WEIGHT (MODEL)</Typography>
                  <Typography variant="body2" fontWeight={900}>4.2%</Typography>
               </Box>
               <Box>
                  <Typography variant="caption" color="textSecondary" display="block">UNREALIZED P&L (MODEL)</Typography>
                  <Typography variant="body2" fontWeight={900} color="primary">+₹24,500 (+12.4%)</Typography>
               </Box>
               <Box>
                  <Typography variant="caption" color="textSecondary" display="block">RISK CONTRIBUTION (MODEL)</Typography>
                  <Typography variant="body2" fontWeight={900} color="warning.main">MODERATE</Typography>
               </Box>
               <Chip label="IN HOLDINGS" size="small" color="primary" sx={{ ml: 'auto', fontWeight: 900, height: 20, fontSize: '0.6rem' }} />
            </Paper>
          )}

          <DecisionPanel stock={selectedStock} />

          <Box sx={{ mb: 4, borderBottom: '1px solid #1e293b' }}>
             <Tabs
               value={activeTab}
               onChange={(_, v) => setActiveTab(v)}
               textColor="primary"
               indicatorColor="primary"
               variant="scrollable"
               scrollButtons="auto"
             >
                <Tab icon={<Brain size={18} />} iconPosition="start" label="DECISION" sx={{ fontWeight: 700 }} />
                <Tab icon={<LineChart size={18} />} iconPosition="start" label="MARKET" sx={{ fontWeight: 700 }} />
                <Tab icon={<BarChart4 size={18} />} iconPosition="start" label="FUNDAMENTALS" sx={{ fontWeight: 700 }} />
                <Tab icon={<Activity size={18} />} iconPosition="start" label="ANALYTICS" sx={{ fontWeight: 700 }} />
                <Tab icon={<ShieldAlert size={18} />} iconPosition="start" label="RISK" sx={{ fontWeight: 700 }} />
                <Tab icon={<History size={18} />} iconPosition="start" label="HISTORY" sx={{ fontWeight: 700 }} />
             </Tabs>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} lg={9}>
               {activeTab === 0 && (
                 <Box>
                    <AIInvestmentThesis stock={selectedStock} />
                    <HistoricalPatternMatch symbol={selectedStock.symbol} />
                 </Box>
               )}

               {activeTab === 1 && (
                 <Box>
                    <TechnicalAnalysis data={selectedStock.analysis?.technical_data} />
                    <MarketStructure smc={selectedStock.analysis?.technical_data?.smc} />
                    <InstitutionalPositioning stock={selectedStock} />
                    <OptionsIntelligence stock={selectedStock} />
                    <CorrelationAndHedging symbol={selectedStock.symbol} />
                 </Box>
               )}

               {activeTab === 2 && (
                 <Box>
                    <FundamentalAnalysis stock={selectedStock} />
                    <EarningsIntelligence symbol={selectedStock.symbol} />
                    <PeerBenchmark stock={selectedStock} />
                    <BusinessQualityAndMoat analysis={selectedStock.analysis} />
                 </Box>
               )}

               {activeTab === 3 && (
                 <Box>
                    <QuantAnalytics metrics={selectedStock.analysis?.technical_data?.quant_metrics || {}} />
                    <ScenarioStressLab stock={selectedStock} />
                    <AIPerformance />
                 </Box>
               )}

               {activeTab === 4 && (
                 <Box>
                    <RiskAssessment stock={selectedStock} />
                 </Box>
               )}

               {activeTab === 5 && (
                 <Box>
                    <DecisionHistory history={selectedStock.analysis?.recommendation_history || []} />
                    <AIPerformance />
                    <AIResearchTimeline symbol={selectedStock.symbol} />

                    <Paper sx={{ p: 4, mt: 4, border: '1px solid #1e293b' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                         <Box>
                            <Typography variant="h5" fontWeight={900}>Model Validation</Typography>
                            <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>HISTORICAL ACCURACY AUDIT</Typography>
                         </Box>
                         <Button
                            variant="outlined"
                            startIcon={<History size={18} />}
                            onClick={handleRunBacktest}
                            disabled={loadingBacktest}
                            sx={{ fontWeight: 800 }}
                          >
                            {loadingBacktest ? 'Auditing...' : 'Recalculate Accuracy'}
                          </Button>
                      </Box>

                      {backtestReport ? (
                        <Box>
                          <TableContainer>
                            <Table size="small">
                              <TableHead sx={{ bgcolor: 'rgba(255,255,255,0.01)' }}>
                                <TableRow>
                                  <TableCell sx={{ pl: 3 }}>DATE</TableCell>
                                  <TableCell align="right">ENTRY</TableCell>
                                  <TableCell align="right">TARGET</TableCell>
                                  <TableCell align="right">STOP LOSS</TableCell>
                                  <TableCell align="right">RETURN</TableCell>
                                  <TableCell align="center">OUTCOME</TableCell>
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {backtestSignals.map((sig, idx) => (
                                  <TableRow key={idx} hover>
                                    <TableCell sx={{ pl: 3, fontWeight: 700, color: 'text.secondary' }}>{new Date(sig.date).toLocaleDateString()}</TableCell>
                                    <TableCell align="right" sx={{ fontFamily: 'JetBrains Mono', fontWeight: 700 }}>₹{sig.entry.toLocaleString()}</TableCell>
                                    <TableCell align="right" sx={{ fontFamily: 'JetBrains Mono', fontWeight: 800, color: 'primary.main' }}>₹{sig.target?.toLocaleString() || '---'}</TableCell>
                                    <TableCell align="right" sx={{ fontFamily: 'JetBrains Mono', fontWeight: 800, color: 'error.main' }}>₹{sig.stop_loss?.toLocaleString() || '---'}</TableCell>
                                    <TableCell align="right" sx={{ color: sig.profit_pct >= 0 ? 'primary.main' : 'error.main', fontWeight: 900 }}>
                                      {sig.profit_pct >= 0 ? '+' : ''}{sig.profit_pct.toFixed(2)}%
                                    </TableCell>
                                    <TableCell align="center">
                                      <StatusChip status={sig.outcome} />
                                    </TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </TableContainer>
                        </Box>
                      ) : (
                        <Box sx={{ p: 4, textAlign: 'center', bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 2 }}>
                           <Typography color="textSecondary" sx={{ fontWeight: 600 }}>No audit data available.</Typography>
                           <Typography variant="caption" color="textSecondary">Click 'Recalculate Accuracy' to trigger a deep historical validation.</Typography>
                        </Box>
                      )}
                    </Paper>
                 </Box>
               )}
            </Grid>

            <Grid item xs={12} lg={3}>
              <Stack spacing={3}>
                <StockQualityProfile metrics={selectedStock.health_metrics} />

                <Paper sx={{ p: 3, border: '1px solid #1e293b' }}>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 900 }}>
                    <Database size={16} /> DATA LINEAGE
                  </Typography>
                  <Typography variant="caption" color="textSecondary" display="block" sx={{ mb: 1, fontWeight: 700 }}>
                    Last Sync: {selectedStock.updated_at ? new Date(selectedStock.updated_at).toLocaleString() : '---'}
                  </Typography>
                  <Chip label="Institutional SQL Active" size="small" color="primary" variant="outlined" sx={{ fontSize: '0.6rem', fontWeight: 900, height: 20 }} />
                </Paper>

                <Paper sx={{ p: 3, border: '1px solid #1e293b' }}>
                   <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ fontWeight: 900 }}>REPORTS</Typography>
                   <Button
                      variant="contained"
                      color="primary"
                      fullWidth
                      startIcon={<FileText size={18} />}
                      onClick={generateReport}
                      size="small"
                      sx={{ fontWeight: 900 }}
                    >
                      Export Intelligence PDF
                    </Button>
                </Paper>

                <ResearchNotebook symbol={selectedStock.symbol} />
              </Stack>
            </Grid>
          </Grid>
        </Box>
      ) : (
        <Paper sx={{ p: 8, textAlign: 'center', bgcolor: 'rgba(15, 23, 42, 0.3)', border: '1px dashed #334155' }}>
          <Search size={48} className="text-slategray mb-4 opacity-20" />
          <Typography variant="h5" color="textSecondary" sx={{ mb: 1, fontWeight: 800 }}>Deep Stock Intelligence</Typography>
          <Typography color="textSecondary" sx={{ fontWeight: 500 }}>Search for a Nifty 100 stock to begin institutional research.</Typography>
        </Paper>
      )}
      <AICopilot stockContext={selectedStock} />
    </Box>
  );
}

function StatusChip({ status }: { status: string }) {
   const isHit = status === 'TARGET_HIT';
   const isStop = status === 'STOP_LOSS';
   const isActive = status === 'ACTIVE';

   return (
      <Chip
         label={status === 'TARGET_HIT' ? 'HIT' : status === 'STOP_LOSS' ? 'STOP' : status}
         size="small"
         variant={isActive ? "outlined" : "filled"}
         color={isHit ? "primary" : isStop ? "error" : isActive ? "info" : "default"}
         sx={{ fontWeight: 900, height: 18, fontSize: '0.55rem' }}
      />
   );
}
