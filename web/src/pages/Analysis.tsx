import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, Autocomplete, TextField, CircularProgress, Stack, Button, Divider, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { Brain, Cpu, Zap, Search, History, CheckCircle, XCircle } from 'lucide-react';
import { getStocks, triggerBacktest, getBacktestResults, getBacktestSignals } from '../api/client';
import AnalysisReport from '../components/AnalysisReport';

export default function Analysis() {
  const [stocks, setStocks] = useState<any[]>([]);
  const [selectedStock, setSelectedStock] = useState<any | null>(null);
  const [backtestReport, setBacktestReport] = useState<any | null>(null);
  const [backtestSignals, setBacktestSignals] = useState<any[]>([]);
  const [loadingBacktest, setLoadingBacktest] = useState(false);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const data = await getStocks();
        setStocks(data);
      } catch (error) {
        console.error('Error fetching stocks:', error);
      }
    };
    fetchStocks();
  }, []);

  useEffect(() => {
    if (selectedStock) {
      fetchBacktest(selectedStock.symbol);
      fetchSignals(selectedStock.symbol);
    } else {
      setBacktestReport(null);
      setBacktestSignals([]);
    }
  }, [selectedStock]);

  const fetchBacktest = async (symbol: string) => {
    try {
      const data = await getBacktestResults(symbol);
      if (data && !data.error) {
        setBacktestReport(data);
      } else {
        setBacktestReport(null);
      }
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>AI Intelligence</Typography>

        <Autocomplete
          sx={{ width: 300 }}
          options={stocks}
          getOptionLabel={(option) => option.symbol}
          onChange={(_, newValue) => setSelectedStock(newValue)}
          renderInput={(params) => (
            <TextField {...params} label="Search for reports..." size="small" />
          )}
        />
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 4, minHeight: 600 }}>
            {selectedStock ? (
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4 }}>
                  <Box>
                    <Typography variant="h5" fontWeight="bold">{selectedStock.symbol} Performance Analysis</Typography>
                    <Typography variant="body2" color="textSecondary">Multi-agent institutional report & 10Y Accuracy</Typography>
                  </Box>
                  <Button
                    variant="outlined"
                    startIcon={<History size={18} />}
                    onClick={handleRunBacktest}
                    disabled={loadingBacktest}
                  >
                    Run 10Y Backtest
                  </Button>
                </Box>

                {backtestReport && (
                  <Box>
                    <Box sx={{ mb: 6, p: 3, backgroundColor: 'rgba(16, 185, 129, 0.05)', borderRadius: 2, border: '1px solid #10b981' }}>
                      <Grid container spacing={2}>
                        <Grid item xs={4}>
                          <Typography variant="caption" color="textSecondary">10Y SUCCESS RATE</Typography>
                          <Typography variant="h4" color="primary" fontWeight="bold">{backtestReport.success_rate?.toFixed(1)}%</Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="caption" color="textSecondary">TOTAL SIGNALS</Typography>
                          <Typography variant="h4" fontWeight="bold">{backtestReport.total_signals}</Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="caption" color="textSecondary">AVG. PROFIT/TRADE</Typography>
                          <Typography variant="h4" color="primary" fontWeight="bold">+{backtestReport.avg_profit?.toFixed(2)}%</Typography>
                        </Grid>
                      </Grid>
                      <Divider sx={{ my: 2, opacity: 0.1 }} />
                      <Typography variant="caption" color="textSecondary">Last Accuracy Audit: {new Date(backtestReport.last_run).toLocaleDateString()}</Typography>
                    </Box>

                    {backtestSignals.length > 0 && (
                      <Box sx={{ mb: 6 }}>
                        <Typography variant="h6" gutterBottom>Historical Signals (Last 100)</Typography>
                        <TableContainer component={Paper} sx={{ backgroundColor: 'transparent', border: 'none' }}>
                          <Table size="small">
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
                    )}
                  </Box>
                )}

                {selectedStock.analysis ? (
                  <AnalysisReport data={{ ...selectedStock.analysis, symbol: selectedStock.symbol }} />
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', py: 8 }}>
                    <CircularProgress sx={{ mb: 2 }} />
                    <Typography color="textSecondary">AI is processing {selectedStock.symbol}...</Typography>
                  </Box>
                )}
              </Box>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', py: 8 }}>
                <Search size={48} className="text-slategray mb-4 opacity-20" />
                <Typography color="textSecondary" align="center">
                  Search for a stock in the bar above to view <br />
                  detailed multi-agent institutional reports.
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Stack spacing={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Intelligence Feed</Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Real-time multi-agent consensus for NSE stocks.
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <AnalysisStep icon={<Brain size={18} />} title="Technical Agent" status="SMC Enabled" />
                  <AnalysisStep icon={<Cpu size={18} />} title="Fundamental Agent" status="Active" />
                  <AnalysisStep icon={<Zap size={18} />} title="Consensus Agent" status="Active" />
                </Box>
              </CardContent>
            </Card>

            <Paper sx={{ p: 3, backgroundColor: 'rgba(16, 185, 129, 0.05)' }}>
              <Typography variant="subtitle2" gutterBottom>Overall Market Bias</Typography>
              <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>BULLISH</Typography>
              <Typography variant="caption" color="textSecondary">Scanning {stocks.length} tracked symbols</Typography>
            </Paper>
          </Stack>
        </Grid>
      </Grid>
    </Box>
  );
}

function AnalysisStep({ icon, title, status }: any) {
  return (
    <Box sx={{ p: 2, border: '1px solid #334155', borderRadius: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
      <Box sx={{ p: 1, backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#10b981', borderRadius: '50%' }}>
        {icon}
      </Box>
      <Box>
        <Typography fontWeight="bold" variant="body2">{title}</Typography>
        <Typography variant="caption" color="textSecondary">{status}</Typography>
      </Box>
    </Box>
  );
}
