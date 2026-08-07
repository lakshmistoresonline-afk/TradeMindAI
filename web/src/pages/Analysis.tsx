import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Grid, Autocomplete, TextField, Stack, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Tabs, Tab } from '@mui/material';
import { Search, History, CheckCircle, XCircle, FileText, Database, Fingerprint, Activity, Layout } from 'lucide-react';
import {
  getStocks, triggerBacktest, getBacktestResults,
  getBacktestSignals, getStockTimeline
} from '../api/client';
import ResearchHeader from '../components/Research/ResearchHeader';
import AIExecutiveSummary from '../components/Research/AIExecutiveSummary';
import AIScoreCard from '../components/Research/AIScoreCard';
import StockHealthScorecard from '../components/Research/StockHealthScorecard';
import InvestmentThesis from '../components/Research/InvestmentThesis';
import AIResearchTimeline from '../components/Research/AIResearchTimeline';
import DecisionSimulator from '../components/Research/DecisionSimulator';
import WhyWhyNot from '../components/Research/WhyWhyNot';
import TechnicalDeepDive from '../components/Research/TechnicalDeepDive';
import MarketStructure from '../components/Research/MarketStructure';
import FundamentalReport from '../components/Research/FundamentalReport';
import OptionsAnalytics from '../components/Research/OptionsAnalytics';
import ManagementMoat from '../components/Research/ManagementMoat';
import EarningsIntelligence from '../components/Research/EarningsIntelligence';
import InstitutionalActivity from '../components/Research/InstitutionalActivity';
import FinancialWorkspace from '../components/Research/FinancialWorkspace';
import ResearchNotebook from '../components/Research/ResearchNotebook';
import KnowledgeGraph from '../components/Research/KnowledgeGraph';
import DigitalTwin from '../components/Research/DigitalTwin';
import RadarComparison from '../components/Research/RadarComparison';
import CorrelationEngine from '../components/Research/CorrelationEngine';
import MultiTimeframeAnalysis from '../components/Research/MultiTimeframeAnalysis';
import RecommendationHistory from '../components/Research/RecommendationHistory';
import SimilarityEngine from '../components/Research/SimilarityEngine';
import AILearningMentor from '../components/Research/AILearningMentor';
import HistoricalAIPerformance from '../components/Research/HistoricalAIPerformance';
import AICopilot from '../components/AICopilot';
import DecisionAnchorHeader from '../components/Research/DecisionAnchorHeader';

import { useLocation } from 'react-router-dom';

export default function Analysis() {
  const location = useLocation();
  const [stocks, setStocks] = useState<any[]>([]);
  const [selectedStock, setSelectedStock] = useState<any | null>(null);
  const [backtestReport, setBacktestReport] = useState<any | null>(null);
  const [backtestSignals, setBacktestSignals] = useState<any[]>([]);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loadingBacktest, setLoadingBacktest] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  const generateReport = () => {
    // (Existing generateReport logic stays the same)
    if (!selectedStock) return;
    const content = `
# TRADE MIND AI: INSTITUTIONAL EQUITY RESEARCH
## ${selectedStock.name} (${selectedStock.symbol})

**Report Generated:** ${new Date().toLocaleString(undefined, { dateStyle: 'full', timeStyle: 'short' })}
**AI Investment Score:** ${selectedStock.ai_investment_score} / 100
**Grade:** ${selectedStock.ai_investment_grade}

### EXECUTIVE SUMMARY
${selectedStock.analysis?.consensus}

### AI THESIS
- **Bull Case:** Strong institutional accumulation and breakout structure.
- **Bear Case:** Valuation at premium levels vs historical median.
- **Invalidation:** Thesis fails if weekly close below support.

### KEY METRICS
- **Sector:** ${selectedStock.sector}
- **Industry:** ${selectedStock.industry}
- **Market Cap:** ₹${(selectedStock.market_cap / 1e7).toFixed(2)} Cr
- **P/E Ratio:** ${selectedStock.pe_ratio?.toFixed(2)}
- **P/B Ratio:** ${selectedStock.pb_ratio?.toFixed(2)}
- **ROE:** ${(selectedStock.roe * 100).toFixed(2)}%
- **Beta:** ${selectedStock.beta?.toFixed(2)}

### TECHNICAL POSTURE
- **Primary Trend:** ${selectedStock.analysis?.technical_data?.mtf_alignment?.overall_bias}
- **RSI (14):** ${selectedStock.analysis?.technical_data?.indicators?.momentum_rsi?.toFixed(2)}
- **Pivot Point:** ₹${selectedStock.analysis?.technical_data?.indicators?.Pivot?.toFixed(2)}

### QUANTITATIVE RISK
- **Sharpe Ratio:** ${selectedStock.analysis?.technical_data?.quant_metrics?.sharpe_ratio?.toFixed(2)}
- **Max Drawdown:** ${(selectedStock.analysis?.technical_data?.quant_metrics?.max_drawdown * 100).toFixed(1)}%

---
*Disclaimer: AI-generated research is for informational purposes only. Past performance does not guarantee future outcomes.*
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

        // Handle deep-link from Market page
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
      getStockTimeline(selectedStock.symbol).then(setTimeline);
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
        <Typography variant="h4" sx={{ fontWeight: 900 }}>Stock Forensic</Typography>

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

          <DecisionAnchorHeader stock={selectedStock} />

          <Box sx={{ mb: 4, borderBottom: '1px solid #1e293b' }}>
             <Tabs
               value={activeTab}
               onChange={(_, v) => setActiveTab(v)}
               textColor="primary"
               indicatorColor="primary"
               variant="scrollable"
               scrollButtons="auto"
             >
                <Tab icon={<Layout size={18} />} iconPosition="start" label="OVERVIEW" sx={{ fontWeight: 700 }} />
                <Tab icon={<Fingerprint size={18} />} iconPosition="start" label="FORENSICS" sx={{ fontWeight: 700 }} />
                <Tab icon={<Activity size={18} />} iconPosition="start" label="HEALTH" sx={{ fontWeight: 700 }} />
                <Tab icon={<History size={18} />} iconPosition="start" label="HISTORY" sx={{ fontWeight: 700 }} />
             </Tabs>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} lg={9}>
               {activeTab === 0 && (
                 <Box>
                    <AIExecutiveSummary stock={selectedStock} />
                    <InvestmentThesis analysis={selectedStock.analysis} />
                    <WhyWhyNot analysis={selectedStock.analysis} />

                    <Grid container spacing={3}>
                       <Grid item xs={12}>
                          <TechnicalDeepDive data={selectedStock.analysis?.technical_data} />
                          <Box sx={{ mt: 1, p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 2 }}>
                             <Typography variant="caption" color="primary" fontWeight="bold">AI CHART NARRATION:</Typography>
                             <Typography variant="body2" color="textSecondary" sx={{ mt: 0.5 }}>
                                {selectedStock.structured_consensus?.thesis || selectedStock.analysis?.consensus}
                             </Typography>
                          </Box>
                       </Grid>
                       <Grid item xs={12}>
                          <DecisionSimulator stock={selectedStock} />
                       </Grid>
                       <Grid item xs={12}>
                          <MarketStructure smc={selectedStock.analysis?.technical_data?.smc} />
                       </Grid>
                       <Grid item xs={12}>
                          <OptionsAnalytics data={selectedStock.analysis?.options_data} />
                       </Grid>
                    </Grid>
                 </Box>
               )}

               {activeTab === 1 && (
                 <Box>
                    <DigitalTwin symbol={selectedStock.symbol} />
                    <KnowledgeGraph symbol={selectedStock.symbol} />
                    <SimilarityEngine symbol={selectedStock.symbol} />
                    <CorrelationEngine symbol={selectedStock.symbol} />
                    <MultiTimeframeAnalysis mtf_data={selectedStock.analysis?.technical_data?.mtf_alignment} />
                 </Box>
               )}

               {activeTab === 2 && (
                 <Box>
                    <FundamentalReport stock={selectedStock} />
                    <FinancialWorkspace />
                    <ManagementMoat analysis={selectedStock.analysis} />
                    <InstitutionalActivity stock={selectedStock} />
                    <EarningsIntelligence symbol={selectedStock.symbol} />
                    <RadarComparison stock={selectedStock} />
                 </Box>
               )}

               {activeTab === 3 && (
                 <Box>
                    <HistoricalAIPerformance />
                    <RecommendationHistory history={timeline.filter(t => t.type === 'RATING')} />
                    <AIResearchTimeline symbol={selectedStock.symbol} />

                    <Paper sx={{ p: 4, mt: 4 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4 }}>
                         <Typography variant="h5" fontWeight="bold">10-Year Strategy Validation</Typography>
                         <Button
                            variant="outlined"
                            startIcon={<History size={18} />}
                            onClick={handleRunBacktest}
                            disabled={loadingBacktest}
                          >
                            Recalculate Accuracy
                          </Button>
                      </Box>

                      {backtestReport ? (
                        <Box>
                          <Box sx={{ mb: 6, p: 3, backgroundColor: 'rgba(16, 185, 129, 0.05)', borderRadius: 2, border: '1px solid #10b981' }}>
                            <Grid container spacing={2}>
                              <Grid item xs={4}>
                                <Typography variant="caption" color="textSecondary">SUCCESS RATE</Typography>
                                <Typography variant="h4" color="primary" fontWeight="bold">{backtestReport.success_rate?.toFixed(1)}%</Typography>
                              </Grid>
                              <Grid item xs={4}>
                                <Typography variant="caption" color="textSecondary">TOTAL SIGNALS</Typography>
                                <Typography variant="h4" fontWeight="bold">{backtestReport.total_signals}</Typography>
                              </Grid>
                              <Grid item xs={4}>
                                <Typography variant="caption" color="textSecondary">AVG. PROFIT</Typography>
                                <Typography variant="h4" color="primary" fontWeight="bold">+{backtestReport.avg_profit?.toFixed(2)}%</Typography>
                              </Grid>
                            </Grid>
                          </Box>

                          <TableContainer>
                            <Table>
                              <TableHead>
                                <TableRow>
                                  <TableCell>Date</TableCell>
                                  <TableCell>Entry</TableCell>
                                  <TableCell>Exit (30d)</TableCell>
                                  <TableCell align="right">Return</TableCell>
                                  <TableCell align="center">Result</TableCell>
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {backtestSignals.map((sig, idx) => (
                                  <TableRow key={idx}>
                                    <TableCell>{sig.date}</TableCell>
                                    <TableCell>₹{sig.entry.toFixed(2)}</TableCell>
                                    <TableCell>₹{sig.exit_30d.toFixed(2)}</TableCell>
                                    <TableCell align="right" sx={{ color: sig.success ? '#10b981' : '#f43f5e' }}>
                                      {sig.profit_pct.toFixed(2)}%
                                    </TableCell>
                                    <TableCell align="center">
                                      {sig.success ? <CheckCircle size={16} color="#10b981" /> : <XCircle size={16} color="#f43f5e" />}
                                    </TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </TableContainer>
                        </Box>
                      ) : (
                        <Typography color="textSecondary">No backtest data available. Click 'Recalculate Accuracy' to generate.</Typography>
                      )}
                    </Paper>
                 </Box>
               )}
            </Grid>

            <Grid item xs={12} lg={3}>
              <Stack spacing={3}>
                <AIScoreCard
                  score={selectedStock.ai_investment_score || 0}
                  grade={selectedStock.ai_investment_grade || 'B'}
                  confidence={selectedStock.confidence_metrics}
                />

                <StockHealthScorecard metrics={selectedStock.health_metrics} />

                <Paper sx={{ p: 3, border: '1px solid #1e293b' }}>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Database size={16} /> DATA LINEAGE
                  </Typography>
                  <Typography variant="caption" color="textSecondary" display="block" sx={{ mb: 1 }}>
                    Last Sync: {selectedStock.updated_at ? new Date(selectedStock.updated_at).toLocaleString() : '---'}
                  </Typography>
                  <Chip label="Hybrid SQL/DuckDB Active" size="small" color="primary" variant="outlined" sx={{ fontSize: '0.65rem', fontWeight: 800 }} />
                </Paper>

                <Paper sx={{ p: 3, border: '1px solid #1e293b' }}>
                   <Typography variant="subtitle2" color="textSecondary" gutterBottom>REPORTS</Typography>
                   <Button
                      variant="contained"
                      color="primary"
                      fullWidth
                      startIcon={<FileText size={18} />}
                      onClick={generateReport}
                      size="small"
                      sx={{ fontWeight: 800 }}
                    >
                      Institutional PDF
                    </Button>
                </Paper>

                <AILearningMentor />
                <ResearchNotebook symbol={selectedStock.symbol} />
              </Stack>
            </Grid>
          </Grid>
        </Box>
      ) : (
        <Paper sx={{ p: 8, textAlign: 'center', bgcolor: 'rgba(15, 23, 42, 0.3)', border: '1px dashed #334155' }}>
          <Search size={48} className="text-slategray mb-4 opacity-20" />
          <Typography variant="h5" color="textSecondary" sx={{ mb: 1 }}>Deep Stock Forensics</Typography>
          <Typography color="textSecondary">Search for a Nifty 100 stock to begin institutional research.</Typography>
        </Paper>
      )}
      <AICopilot stockContext={selectedStock} />
    </Box>
  );
}
