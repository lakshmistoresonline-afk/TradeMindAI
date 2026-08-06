import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Grid, Autocomplete, TextField, Stack, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';
import { Search, History, CheckCircle, XCircle, FileText, Database, Fingerprint } from 'lucide-react';
import { getStocks, triggerBacktest, getBacktestResults, getBacktestSignals } from '../api/client';
import ResearchHeader from '../components/Research/ResearchHeader';
import AIExecutiveSummary from '../components/Research/AIExecutiveSummary';
import TechnicalDeepDive from '../components/Research/TechnicalDeepDive';
import MarketStructure from '../components/Research/MarketStructure';
import FundamentalReport from '../components/Research/FundamentalReport';
import OptionsAnalytics from '../components/Research/OptionsAnalytics';
import QuantitativeAnalysis from '../components/Research/QuantitativeAnalysis';
import AIScoreCard from '../components/Research/AIScoreCard';
import StockHealthScorecard from '../components/Research/StockHealthScorecard';
import InvestmentThesis from '../components/Research/InvestmentThesis';
import AIResearchTimeline from '../components/Research/AIResearchTimeline';
import DecisionSimulator from '../components/Research/DecisionSimulator';
import WhyWhyNot from '../components/Research/WhyWhyNot';
import RiskDashboard from '../components/Research/RiskDashboard';
import ManagementMoat from '../components/Research/ManagementMoat';
import AINewsCenter from '../components/Research/AINewsCenter';
import EarningsIntelligence from '../components/Research/EarningsIntelligence';
import InstitutionalActivity from '../components/Research/InstitutionalActivity';
import FinancialWorkspace from '../components/Research/FinancialWorkspace';
import ResearchNotebook from '../components/Research/ResearchNotebook';
import KnowledgeGraph from '../components/Research/KnowledgeGraph';
import DigitalTwin from '../components/Research/DigitalTwin';
import RadarComparison from '../components/Research/RadarComparison';
import MarketReplay from '../components/Research/MarketReplay';
import ScenarioSimulator from '../components/Research/ScenarioSimulator';
import CorrelationEngine from '../components/Research/CorrelationEngine';
import MultiTimeframeAnalysis from '../components/Research/MultiTimeframeAnalysis';
import RecommendationHistory from '../components/Research/RecommendationHistory';
import SimilarityEngine from '../components/Research/SimilarityEngine';
import AILearningMentor from '../components/Research/AILearningMentor';
import HistoricalAIPerformance from '../components/Research/HistoricalAIPerformance';
import AICopilot from '../components/AICopilot';

import { useLocation } from 'react-router-dom';

export default function Analysis() {
  const location = useLocation();
  const [stocks, setStocks] = useState<any[]>([]);
  const [selectedStock, setSelectedStock] = useState<any | null>(null);
  const [backtestReport, setBacktestReport] = useState<any | null>(null);
  const [backtestSignals, setBacktestSignals] = useState<any[]>([]);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loadingBacktest, setLoadingBacktest] = useState(false);
  const [view, setView] = useState('research'); // 'research', 'backtest', 'twin'

  const generateReport = () => {
    if (!selectedStock) return;
    const content = `
# TRADE MIND AI: INSTITUTIONAL EQUITY RESEARCH
## ${selectedStock.name} (${selectedStock.symbol})

**Report Date:** ${new Date().toLocaleDateString()}
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
           const stock = data.find((s: any) => s.symbol === location.state.symbol);
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
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>Institutional Research</Typography>

        <Autocomplete
          sx={{ width: { xs: '100%', sm: 300 } }}
          options={stocks}
          getOptionLabel={(option) => `${option.symbol} - ${option.name}`}
          onChange={(_, newValue) => setSelectedStock(newValue)}
          renderInput={(params) => (
            <TextField {...params} label="Search Ticker..." size="small" />
          )}
        />
      </Box>

      {selectedStock ? (
        <Box>
          <ResearchHeader stock={selectedStock} />

          <Box sx={{ mb: 4, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
             <Button
               variant={view === 'research' ? 'contained' : 'outlined'}
               startIcon={<FileText size={18} />}
               onClick={() => setView('research')}
               size="small"
             >
               Report
             </Button>
             <Button
               variant={view === 'backtest' ? 'contained' : 'outlined'}
               startIcon={<History size={18} />}
               onClick={() => setView('backtest')}
               size="small"
             >
               Backtest
             </Button>
             <Button
               variant={view === 'twin' ? 'contained' : 'outlined'}
               startIcon={<Fingerprint size={18} />}
               onClick={() => setView('twin')}
               size="small"
             >
               Digital Twin
             </Button>
             <Box sx={{ ml: { xs: 0, sm: 'auto' }, width: { xs: '100%', sm: 'auto' }, mt: { xs: 1, sm: 0 } }}>
                <Button
                  variant="outlined"
                  color="primary"
                  fullWidth
                  startIcon={<FileText size={18} />}
                  onClick={generateReport}
                  size="small"
                >
                  Generate Research Report
                </Button>
             </Box>
          </Box>

          {view === 'research' ? (
            <Grid container spacing={3}>
              <Grid item xs={12} lg={9}>
                {/* Module 1 & 2: Score & Confidence */}
                <Grid container spacing={3} sx={{ mb: 4 }}>
                   <Grid item xs={12} sm={6}>
                      <AIScoreCard
                        score={selectedStock.ai_investment_score || 0}
                        grade={selectedStock.ai_investment_grade || 'B'}
                        confidence={selectedStock.confidence_metrics}
                      />
                   </Grid>
                   <Grid item xs={12} sm={6}>
                      <StockHealthScorecard metrics={selectedStock.health_metrics} />
                   </Grid>
                </Grid>

                <AIExecutiveSummary analysis={selectedStock.analysis} />
                <InvestmentThesis analysis={selectedStock.analysis} />
                <WhyWhyNot analysis={selectedStock.analysis} />

                <Grid container spacing={3}>
                   <Grid item xs={12}>
                      <RiskDashboard stock={selectedStock} />
                   </Grid>
                   <Grid item xs={12}>
                      <TechnicalDeepDive data={selectedStock.analysis?.technical_data} />
                      <Box sx={{ mt: 1, p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 2 }}>
                         <Typography variant="caption" color="primary" fontWeight="bold">AI CHART NARRATION:</Typography>
                         <Typography variant="body2" color="textSecondary" sx={{ mt: 0.5 }}>
                            Price is trending above all major EMAs (20, 50, 200) indicating a strong secular bull trend.
                            RSI at 62 suggests healthy momentum without being overextended.
                            Institutional accumulation is evident at the ₹2450 level.
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
                      <EarningsIntelligence symbol={selectedStock.symbol} />
                   </Grid>
                   <Grid item xs={12}>
                      <AIResearchTimeline symbol={selectedStock.symbol} />
                   </Grid>
                   <Grid item xs={12}>
                      <ManagementMoat analysis={selectedStock.analysis} />
                   </Grid>
                   <Grid item xs={12}>
                      <HistoricalAIPerformance />
                   </Grid>
                   <Grid item xs={12}>
                      <FundamentalReport stock={selectedStock} />
                   </Grid>
                   <Grid item xs={12}>
                      <RadarComparison stock={selectedStock} />
                   </Grid>
                   <Grid item xs={12}>
                      <FinancialWorkspace />
                   </Grid>
                   <Grid item xs={12}>
                      <InstitutionalActivity />
                   </Grid>
                   <Grid item xs={12}>
                      <AINewsCenter symbol={selectedStock.symbol} />
                   </Grid>
                   <Grid item xs={12}>
                      <OptionsAnalytics data={selectedStock.analysis?.options_data} />
                   </Grid>
                   <Grid item xs={12}>
                      <QuantitativeAnalysis metrics={selectedStock.analysis?.technical_data?.quant_metrics} />
                   </Grid>
                   <Grid item xs={12}>
                      <ResearchNotebook symbol={selectedStock.symbol} />
                   </Grid>
                   <Grid item xs={12}>
                      <KnowledgeGraph symbol={selectedStock.symbol} />
                   </Grid>
                   <Grid item xs={12}>
                      <MarketReplay />
                   </Grid>
                   <Grid item xs={12}>
                      <ScenarioSimulator />
                   </Grid>
                   <Grid item xs={12}>
                      <CorrelationEngine symbol={selectedStock.symbol} />
                   </Grid>
                   <Grid item xs={12}>
                      <MultiTimeframeAnalysis mtf_data={selectedStock.analysis?.technical_data?.mtf_alignment} />
                   </Grid>
                   <Grid item xs={12}>
                      <SimilarityEngine symbol={selectedStock.symbol} />
                   </Grid>
                   <Grid item xs={12}>
                      <AILearningMentor />
                   </Grid>
                   <Grid item xs={12}>
                      <RecommendationHistory history={timeline.filter(t => t.type === 'RATING')} />
                   </Grid>
                </Grid>
              </Grid>

              <Grid item xs={12} lg={3}>
                <Stack spacing={3}>
                  <Paper sx={{ p: 3 }}>
                    <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Database size={16} /> DATA LINEAGE
                    </Typography>
                    <Typography variant="caption" color="textSecondary" display="block" sx={{ mb: 1 }}>
                      Last Sync: {new Date(selectedStock.updated_at).toLocaleString()}
                    </Typography>
                    <Chip label="Incremental ETL Active" size="small" color="primary" variant="outlined" sx={{ fontSize: '0.65rem' }} />
                  </Paper>

                  <Paper sx={{ p: 3, bgcolor: 'rgba(41, 121, 255, 0.05)', border: '1px solid #2979FF' }}>
                     <Typography variant="subtitle2" color="#2979FF" gutterBottom>PRO ALERTS</Typography>
                     <Typography variant="body2" fontWeight="bold">SMC Breakout Detected</Typography>
                     <Typography variant="caption" color="textSecondary">Institutional activity detected in order block at ₹2480.</Typography>
                  </Paper>

                  <Paper sx={{ p: 3, bgcolor: 'rgba(255, 171, 0, 0.05)', border: '1px solid #FFAB00' }}>
                     <Typography variant="subtitle2" color="#FFAB00" gutterBottom>PORTFOLIO RELEVANCE</Typography>
                     <Typography variant="body2" fontWeight="bold">Not in Portfolio</Typography>
                     <Typography variant="caption" color="textSecondary">Adding this asset would increase your IT sector exposure by 12.5%.</Typography>
                     <Button fullWidth size="small" variant="outlined" sx={{ mt: 2, color: '#FFAB00', borderColor: '#FFAB00' }}>
                        Add to Watchlist
                     </Button>
                  </Paper>
                </Stack>
              </Grid>
            </Grid>
          ) : view === 'twin' ? (
            <DigitalTwin symbol={selectedStock.symbol} />
          ) : (
            <Box>
              <Paper sx={{ p: 4 }}>
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
        </Box>
      ) : (
        <Paper sx={{ p: 8, textAlign: 'center' }}>
          <Search size={48} className="text-slategray mb-4 opacity-20" />
          <Typography color="textSecondary">Search for a Nifty 100 stock to begin institutional research.</Typography>
        </Paper>
      )}
      <AICopilot stockContext={selectedStock} />
    </Box>
  );
}
