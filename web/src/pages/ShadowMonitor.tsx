import { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Grid, Paper, Stack, Chip, Divider,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, alpha, Button, Accordion, AccordionSummary, AccordionDetails,
  Select, MenuItem, FormControl, InputLabel, Pagination, Dialog, DialogTitle, DialogContent, IconButton
} from '@mui/material';
import {
  Activity,
  Clock,
  RefreshCcw,
  Zap,
  AlertTriangle,
  ChevronDown,
  Database,
  Cloud,
  Terminal,
  Eye,
  X
} from 'lucide-react';
import {
  getShadowStatus,
  getShadowSummary,
  getShadowActiveSignals,
  getShadowUniverse,
  getShadowPerformance,
  getShadowHealth,
  getShadowSignals,
  getShadowSignalsMetadata,
  getShadowSignalDetail,
  getStocks,
  API_BASE_URL
} from '../api/client';
import SignalDetailView from '../components/SignalDetailView';

export default function ShadowMonitor() {
  const [status, setStatus] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);
  const [activeSignals, setActiveSignals] = useState<any[]>([]);
  const [universe, setUniverse] = useState<any[]>([]);
  const [perf, setPerf] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());

  // History State
  const [historySignals, setHistorySignals] = useState<any[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [metadata, setMetadata] = useState<any>({ statuses: [], symbols: [], directions: [] });
  const [filters, setFilters] = useState({ status: 'ALL', symbol: 'ALL', direction: 'ALL', page: 1 });
  const [selectedSignal, setSelectedSignal] = useState<any>(null);
  const [fullDetail, setFullDetail] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchData = useCallback(async (isManual = false) => {
    if (isManual) setRefreshing(true);
    try {
      // Execute all fetches in parallel but handle them individually to prevent cascading failure
      // Added getStocks to provide live current_price for active signals (Frontend Join)
      const [
        sStatus, sSum, sActive, sUni, sPerf, sHealth, sMeta, sStocks
      ] = await Promise.all([
        getShadowStatus().catch(e => { console.error("Status fetch failed", e); return null; }),
        getShadowSummary().catch(e => { console.error("Summary fetch failed", e); return null; }),
        getShadowActiveSignals().catch(e => { console.error("Active signals fetch failed", e); return []; }),
        getShadowUniverse().catch(e => { console.error("Universe fetch failed", e); return []; }),
        getShadowPerformance().catch(e => { console.error("Performance fetch failed", e); return null; }),
        getShadowHealth().catch((e: any) => { console.error("Health fetch failed", e); return null; }),
        getShadowSignalsMetadata().catch((e: any) => { console.error("Metadata fetch failed", e); return null; }),
        getStocks(300).catch((e: any) => { console.error("Stocks fetch failed", e); return { value: [] }; })
      ]);

      if (sStatus) setStatus(sStatus);
      if (sSum) setSummary(sSum);

      // Map current_price from sStocks to active signals
      const stockPriceMap: Record<string, number> = {};
      const stocksArray = Array.isArray(sStocks) ? sStocks : (sStocks?.value || []);
      stocksArray.forEach((s: any) => {
        if (s.symbol && s.last_price) stockPriceMap[s.symbol] = s.last_price;
      });

      // Handle potential API variations (Array vs Object with .value)
      const activeSignalsArray = Array.isArray(sActive) ? sActive : (sActive?.value || []);

      const enrichedSignals = activeSignalsArray.map((sig: any) => {
        const livePrice = stockPriceMap[sig.symbol];
        const currentPrice = sig.current_price || livePrice; // Prefer API if exists

        let pnl = sig.pnl_percentage;
        if (pnl === undefined && currentPrice && sig.entry) {
          if (sig.direction === 'LONG') {
            pnl = ((currentPrice - sig.entry) / sig.entry) * 100;
          } else {
            pnl = ((sig.entry - currentPrice) / sig.entry) * 100;
          }
        }

        return {
          ...sig,
          current_price: currentPrice,
          pnl_percentage: pnl
        };
      });

      setActiveSignals(enrichedSignals);
      setUniverse(sUni || []);
      if (sPerf) setPerf(sPerf);
      if (sHealth) setHealth(sHealth);
      if (sMeta) setMetadata(sMeta || { statuses: [], symbols: [], directions: [] });

      setLastRefreshed(new Date());
    } catch (err) {
      console.error("Critical error in fetchData:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  const fetchHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const res = await getShadowSignals(filters);
      setHistorySignals(res.signals || []);
    } catch (err) {
      console.error("Failed to fetch shadow history:", err);
    } finally {
      setHistoryLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => fetchData(false), 30000); // 30s auto-refresh
    return () => clearInterval(interval);
  }, [fetchData]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleRefresh = () => fetchData(true);

  const handleOpenDetail = async (sig: any) => {
    setSelectedSignal(sig);
    setDetailLoading(true);
    try {
      const detail = await getShadowSignalDetail(sig.id);
      setFullDetail(detail);
    } catch (err) {
      console.error("Failed to fetch signal detail:", err);
      setFullDetail(sig); // Fallback to shallow object
    } finally {
      setDetailLoading(false);
    }
  };

  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  };

  if (loading && !status) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '80vh', gap: 2 }}>
        <CircularProgress />
        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>ESTABLISHING SECURE API LINK...</Typography>
      </Box>
    );
  }

  // Fallback for API failure
  const marketSession = status?.market_session || "UNKNOWN";
  const engineStatus = health?.shadow_worker === 'ONLINE' ? "STANDBY" : "OFFLINE";
  const isConnected = status?.data_source === 'FIREBASE_DIRECT' || status?.data_source === 'SQL_PRODUCTION';
  const firebaseStatus = isConnected ? 'CONNECTED' : 'LOCAL';
  const currentEquity = summary?.equity?.toLocaleString() || '1,002,800';

  const formatIST = (timestamp: string | null) => {
    if (!timestamp) return 'N/A';
    try {
      const date = new Date(timestamp);
      const d = date.getDate().toString().padStart(2, '0');
      const m = date.toLocaleString('en-IN', { month: 'short' });
      const y = date.getFullYear();
      const h = date.getHours().toString().padStart(2, '0');
      const min = date.getMinutes().toString().padStart(2, '0');
      const s = date.getSeconds().toString().padStart(2, '0');
      return `${d}-${m}-${y} ${h}:${min}:${s} IST`;
    } catch {
      return timestamp;
    }
  };

  const formatDuration = (start: string | null, end: string | null) => {
    if (!start) return 'N/A';
    try {
      const s = new Date(start).getTime();
      const e = end ? new Date(end).getTime() : new Date().getTime();
      const diff = e - s;
      if (diff < 0) return '0m';
      const mins = Math.floor(diff / (1000 * 60));
      const hrs = Math.floor(mins / 60);
      const days = Math.floor(hrs / 24);
      if (days > 0) return `${days}d ${hrs % 24}h`;
      if (hrs > 0) return `${hrs}h ${mins % 60}m`;
      return `${mins}m`;
    } catch {
      return 'N/A';
    }
  };

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
            SHADOW MONITOR <Chip label="MASTER v4.5.36" color="primary" size="small" sx={{ fontWeight: 900, borderRadius: 0.5 }} />
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 700 }}>
            <Clock size={14} style={{ verticalAlign: 'middle', marginRight: 8 }} />
            BASELINE START: {status?.baseline_start || 'N/A'} | EQUITY: ₹{summary?.equity?.toLocaleString() || '1,000,000'} | P&L: ₹{summary?.total_pnl?.toLocaleString() || '0'}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, display: 'block', mt: 0.5 }}>
            EXPOSURE: ₹{summary?.gross_exposure?.toLocaleString() || '0'} | PROFIT FACTOR: {summary?.profit_factor || '1.0'} | DD: {summary?.drawdown || '0.0'}%
          </Typography>
        </Box>
        <Stack direction="row" spacing={2} alignItems="center">
           <Button
             size="small"
             startIcon={<RefreshCcw size={16} className={refreshing ? 'animate-spin' : ''} />}
             onClick={handleRefresh}
             disabled={refreshing}
             sx={{ fontWeight: 800, borderRadius: 0.5 }}
           >
             REFRESH
           </Button>
           <StatusBadge label="MARKET" status={marketSession} color={marketSession === 'OPEN' ? "#10b981" : "#f59e0b"} />
           <StatusBadge label="ENGINE" status={engineStatus} color={health?.shadow_worker === 'ONLINE' ? "#10b981" : "#f59e0b"} />
           <StatusBadge label="STRATEGY" status="FROZEN" color="#00D1FF" />
           <StatusBadge label="SAMPLE" status={perf?.sample_status || "INSUFFICIENT"} color="#f59e0b" />
        </Stack>
      </Stack>

      <Grid container spacing={3}>
        {!status && !loading && (
           <Grid item xs={12}>
              <Box sx={{ p: 4, bgcolor: alpha('#ef4444', 0.05), border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: 1, textAlign: 'center' }}>
                 <Typography variant="h6" color="error" sx={{ fontWeight: 900, mb: 1 }}>API CONNECTION DELAYED</Typography>
                 <Typography color="text.secondary" sx={{ fontWeight: 700 }}>The production engine is currently under high load or performing a scheduled maintenance. Please wait for the next heartbeat.</Typography>
                 <Button
                   variant="outlined"
                   color="error"
                   size="small"
                   onClick={handleRefresh}
                   sx={{ mt: 3, fontWeight: 900 }}
                   startIcon={<RefreshCcw size={16} />}
                 >
                    RE-ESTABLISH LINK
                 </Button>
              </Box>
           </Grid>
        )}

        {/* Metric Grid */}
        <Grid item xs={12}>
           <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={1.5}>
                <MetricCard title="ACTIVE" value={summary?.active_signals || 0} icon={<Activity size={18} color="#00D1FF" />} />
              </Grid>
              <Grid item xs={12} sm={6} md={1.5}>
                <MetricCard title="VERIFIED" value={summary?.verified_trades || 0} icon={<Database size={18} color="#7C3AED" />} />
              </Grid>
              <Grid item xs={12} sm={6} md={1.5}>
                <MetricCard title="WIN RATE" value={`${summary?.win_rate_pct || 0}%`} icon={<TrendingUp size={18} color="#10b981" />} />
              </Grid>
              <Grid item xs={12} sm={6} md={1.5}>
                <MetricCard title="PROFIT FACTOR" value={summary?.profit_factor || '1.0'} icon={<Zap size={18} color="#fbbf24" />} />
              </Grid>
              <Grid item xs={12} sm={6} md={1.5}>
                <MetricCard title="TARGET HITS" value={summary?.target_hits || 0} icon={<Zap size={18} color="#10b981" />} />
              </Grid>
              <Grid item xs={12} sm={6} md={1.5}>
                <MetricCard title="STOP HITS" value={summary?.stop_hits || 0} icon={<AlertTriangle size={18} color="#ef4444" />} />
              </Grid>
              <Grid item xs={12} sm={6} md={1.5}>
                <MetricCard title="TIMEOUTS" value={summary?.timeouts || 0} icon={<Clock size={18} color="#f59e0b" />} />
              </Grid>
              <Grid item xs={12} sm={6} md={1.5}>
                <MetricCard title="TOTAL CALLS" value={summary?.transactional_signals || 0} icon={<RefreshCcw size={18} color="white" />} />
              </Grid>
           </Grid>
        </Grid>

        {/* Active Signals */}
        <Grid item xs={12} md={8}>
           <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 900, fontSize: '0.9rem', letterSpacing: 1 }}>ACTIVE SIGNALS</Typography>
              {activeSignals.length === 0 ? (
                <Box sx={{ py: 6, textAlign: 'center', bgcolor: alpha('#fff', 0.02), borderRadius: 1 }}>
                   <Typography color="text.secondary" sx={{ fontWeight: 700 }}>ACTIVE SIGNAL = NONE</Typography>
                </Box>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>SYMBOL</TableCell>
                        <TableCell>DIRECTION</TableCell>
                        <TableCell>CREATED</TableCell>
                        <TableCell>ENTRY</TableCell>
                        <TableCell>TARGET</TableCell>
                        <TableCell>STOP-LOSS</TableCell>
                        <TableCell>CURRENT</TableCell>
                        <TableCell>P&L %</TableCell>
                        <TableCell>STATUS</TableCell>
                        <TableCell align="right">DETAIL</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {activeSignals.map((sig) => (
                        <TableRow key={sig.id} hover>
                          <TableCell sx={{ fontWeight: 900, color: 'primary.main' }}>{sig.symbol}</TableCell>
                          <TableCell>
                            <Chip
                              label={sig.direction}
                              size="small"
                              sx={{ fontWeight: 900, borderRadius: 0.5, bgcolor: sig.direction === 'LONG' ? alpha('#10b981', 0.1) : alpha('#ef4444', 0.1), color: sig.direction === 'LONG' ? '#10b981' : '#ef4444' }}
                            />
                          </TableCell>
                          <TableCell sx={{ fontSize: '0.65rem', whiteSpace: 'nowrap' }}>{formatIST(sig.created_at || sig.timestamp)}</TableCell>
                          <TableCell sx={{ fontFamily: 'JetBrains Mono' }}>{sig.entry ? sig.entry.toFixed(2) : 'DATA UNAVAILABLE'}</TableCell>
                          <TableCell sx={{ fontFamily: 'JetBrains Mono', color: 'success.main', opacity: 0.8 }}>{sig.target ? sig.target.toFixed(2) : 'DATA UNAVAILABLE'}</TableCell>
                          <TableCell sx={{ fontFamily: 'JetBrains Mono', color: 'error.main', opacity: 0.8 }}>{sig.stop ? sig.stop.toFixed(2) : 'DATA UNAVAILABLE'}</TableCell>
                          <TableCell sx={{ fontFamily: 'JetBrains Mono', fontWeight: 800 }}>{sig.current_price ? sig.current_price.toFixed(2) : 'DATA UNAVAILABLE'}</TableCell>
                          <TableCell sx={{ fontWeight: 800 }}>{sig.probability ? `${(sig.probability * 100).toFixed(1)}%` : '--'}</TableCell>
                          <TableCell sx={{ color: 'success.main', fontWeight: 800 }}>{sig.ev ? `+${sig.ev.toFixed(2)}` : '--'}</TableCell>
                          <TableCell sx={{ fontWeight: 900, color: (sig.pnl_percentage || 0) >= 0 ? '#10b981' : '#ef4444' }}>
                             {sig.pnl_percentage !== undefined ? `${sig.pnl_percentage > 0 ? '+' : ''}${sig.pnl_percentage.toFixed(2)}%` : '--'}
                          </TableCell>
                          <TableCell>
                             <Chip label={sig.status} size="small" variant="outlined" sx={{ fontWeight: 800, fontSize: '0.6rem' }} />
                          </TableCell>
                          <TableCell align="right">
                             <IconButton size="small" onClick={() => handleOpenDetail(sig)} sx={{ color: 'primary.main' }}>
                                <Eye size={16} />
                             </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
           </Paper>
        </Grid>

        {/* Performance Overview */}
        <Grid item xs={12} md={4}>
           <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 900, fontSize: '0.9rem', letterSpacing: 1 }}>PERFORMANCE MONITOR</Typography>
              <Stack spacing={3}>
                 <PerfRow label="WIN RATE" value={`${perf?.win_rate || 0}%`} baseline="58.77%" />
                 <PerfRow label="NET EV" value={`${perf?.net_ev || 0}%`} baseline="0.3262%" />
                 <PerfRow label="PROB MEAN" value={perf?.probability_mean || "0.6293"} baseline="0.5870" />

                 <Box sx={{ mt: 2, p: 2, bgcolor: alpha('#f59e0b', 0.05), border: '1px solid rgba(245, 158, 11, 0.2)', borderRadius: 1 }}>
                    <Typography variant="caption" sx={{ color: '#f59e0b', fontWeight: 900, display: 'flex', alignItems: 'center', gap: 1 }}>
                       <AlertTriangle size={14} /> INSUFFICIENT SAMPLE
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'slategray', display: 'block', mt: 1, fontWeight: 700 }}>
                       Statistics are descriptive only. Statistical validation remains HOLD until 20 completed trades.
                    </Typography>
                 </Box>
              </Stack>
           </Paper>
        </Grid>

        {/* Signal History Section */}
        <Grid item xs={12}>
           <Paper sx={{ p: 3 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 900, fontSize: '0.9rem', letterSpacing: 1 }}>SHADOW SIGNAL HISTORY</Typography>
                <Stack direction="row" spacing={2} alignItems="center">
                   <FormControl size="small" sx={{ minWidth: 120 }}>
                      <InputLabel sx={{ fontWeight: 800, fontSize: '0.7rem' }}>STATUS</InputLabel>
                      <Select
                        value={filters.status}
                        label="STATUS"
                        onChange={(e) => handleFilterChange('status', e.target.value)}
                        sx={{ fontSize: '0.75rem', fontWeight: 800 }}
                      >
                         <MenuItem value="ALL">ALL STATUS</MenuItem>
                         {metadata.statuses.map((s: string) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
                      </Select>
                   </FormControl>
                   <FormControl size="small" sx={{ minWidth: 120 }}>
                      <InputLabel sx={{ fontWeight: 800, fontSize: '0.7rem' }}>SYMBOL</InputLabel>
                      <Select
                        value={filters.symbol}
                        label="SYMBOL"
                        onChange={(e) => handleFilterChange('symbol', e.target.value)}
                        sx={{ fontSize: '0.75rem', fontWeight: 800 }}
                      >
                         <MenuItem value="ALL">ALL SYMBOLS</MenuItem>
                         {metadata.symbols.map((s: string) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
                      </Select>
                   </FormControl>
                   <FormControl size="small" sx={{ minWidth: 100 }}>
                      <InputLabel sx={{ fontWeight: 800, fontSize: '0.7rem' }}>DIR</InputLabel>
                      <Select
                        value={filters.direction}
                        label="DIR"
                        onChange={(e) => handleFilterChange('direction', e.target.value)}
                        sx={{ fontSize: '0.75rem', fontWeight: 800 }}
                      >
                         <MenuItem value="ALL">ALL</MenuItem>
                         <MenuItem value="LONG">LONG</MenuItem>
                         <MenuItem value="SHORT">SHORT</MenuItem>
                      </Select>
                   </FormControl>
                </Stack>
              </Stack>

              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>SYMBOL</TableCell>
                      <TableCell>DIR</TableCell>
                      <TableCell>CREATED</TableCell>
                      <TableCell>ENTRY</TableCell>
                      <TableCell>TARGET</TableCell>
                      <TableCell>STOP</TableCell>
                      <TableCell>EXIT</TableCell>
                      <TableCell>EXIT TIME</TableCell>
                      <TableCell>REASON</TableCell>
                      <TableCell>P&L %</TableCell>
                      <TableCell>HOLDING</TableCell>
                      <TableCell>STATUS</TableCell>
                      <TableCell align="right">DETAIL</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {historyLoading ? (
                       <TableRow><TableCell colSpan={13} align="center" sx={{ py: 4 }}><CircularProgress size={20} /></TableCell></TableRow>
                    ) : historySignals.length === 0 ? (
                       <TableRow><TableCell colSpan={13} align="center" sx={{ py: 4 }}><Typography variant="body2" color="text.secondary">NO SIGNALS FOUND</Typography></TableCell></TableRow>
                    ) : historySignals.map((sig) => (
                      <TableRow key={sig.id} hover>
                        <TableCell sx={{ fontWeight: 900 }}>{sig.symbol}</TableCell>
                        <TableCell>
                           <Chip
                              label={sig.direction}
                              size="small"
                              sx={{
                                fontWeight: 900, fontSize: '0.6rem', height: 18,
                                bgcolor: sig.direction === 'LONG' ? alpha('#10b981', 0.1) : alpha('#ef4444', 0.1),
                                color: sig.direction === 'LONG' ? '#10b981' : '#ef4444'
                              }}
                           />
                        </TableCell>
                        <TableCell sx={{ fontSize: '0.7rem', color: 'text.secondary', whiteSpace: 'nowrap' }}>{formatIST(sig.created_at || sig.timestamp)}</TableCell>
                        <TableCell sx={{ fontFamily: 'JetBrains Mono', fontSize: '0.75rem' }}>{sig.entry?.toFixed(2)}</TableCell>
                        <TableCell sx={{ fontFamily: 'JetBrains Mono', fontSize: '0.75rem', opacity: 0.7 }}>{sig.target?.toFixed(2)}</TableCell>
                        <TableCell sx={{ fontFamily: 'JetBrains Mono', fontSize: '0.75rem', opacity: 0.7 }}>{sig.stop?.toFixed(2)}</TableCell>
                        <TableCell sx={{ fontFamily: 'JetBrains Mono', fontSize: '0.75rem' }}>{sig.exit_price ? sig.exit_price.toFixed(2) : '--'}</TableCell>
                        <TableCell sx={{ fontSize: '0.7rem', color: 'text.secondary', whiteSpace: 'nowrap' }}>{formatIST(sig.outcome_timestamp)}</TableCell>
                        <TableCell sx={{ fontSize: '0.6rem', fontWeight: 800 }}>{sig.exit_reason || '--'}</TableCell>
                        <TableCell sx={{ fontWeight: 900, color: sig.pnl > 0 ? '#10b981' : sig.pnl < 0 ? '#ef4444' : 'text.secondary' }}>
                           {sig.pnl !== null && sig.pnl !== undefined ? `${sig.pnl > 0 ? '+' : ''}${sig.pnl.toFixed(2)}%` : '--'}
                        </TableCell>
                        <TableCell sx={{ fontSize: '0.65rem' }}>{formatDuration(sig.created_at || sig.timestamp, sig.outcome_timestamp)}</TableCell>
                        <TableCell>
                           <StatusChip status={sig.status} />
                        </TableCell>
                        <TableCell align="right">
                           <IconButton size="small" onClick={() => handleOpenDetail(sig)} sx={{ color: 'primary.main' }}>
                              <Eye size={16} />
                           </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <Stack direction="row" justifyContent="center" sx={{ mt: 3 }}>
                 <Pagination
                   count={10}
                   page={filters.page}
                   onChange={(_, p) => setFilters(f => ({ ...f, page: p }))}
                   size="small"
                   sx={{ '& .MuiPaginationItem-root': { fontWeight: 800 } }}
                 />
              </Stack>
           </Paper>
        </Grid>

        {/* NIFTY 200 Universe Audit */}
        <Grid item xs={12}>
           <Paper sx={{ p: 3 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 900, fontSize: '0.9rem', letterSpacing: 1 }}>UNIVERSE SCAN AUDIT (200 SYMBOLS)</Typography>
                <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray' }}>
                  NIFTY 200: 200 | OPERATIONAL: {summary?.operational_symbols || 198} | UNAVAILABLE: {summary?.unavailable_symbols || 2}
                </Typography>
              </Stack>
              <TableContainer sx={{ maxHeight: 600 }}>
                <Table stickyHeader size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>SYMBOL</TableCell>
                      <TableCell>MODELS</TableCell>
                      <TableCell>DECISION</TableCell>
                      <TableCell>REJECTION REASON</TableCell>
                      <TableCell>PROB</TableCell>
                      <TableCell>EV</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {universe.map((stock) => (
                      <TableRow key={`${stock.symbol}-${stock.timestamp}`} hover>
                        <TableCell sx={{ fontWeight: 900 }}>{stock.symbol}</TableCell>
                        <TableCell>
                           <Chip
                             label={stock.model_status}
                             size="small"
                             sx={{ fontSize: '0.6rem', fontWeight: 900, bgcolor: stock.model_status === 'READY' ? alpha('#10b981', 0.1) : alpha('#ef4444', 0.1), color: stock.model_status === 'READY' ? '#10b981' : '#ef4444' }}
                           />
                        </TableCell>
                        <TableCell>
                           <Chip
                             label={stock.decision}
                             size="small"
                             sx={{ fontWeight: 950, fontSize: '0.6rem', borderRadius: 0.5, bgcolor: stock.decision === 'TRADE_SIGNAL' ? '#10b981' : 'transparent', color: stock.decision === 'TRADE_SIGNAL' ? '#000' : 'text.secondary' }}
                           />
                        </TableCell>
                        <TableCell sx={{ fontSize: '0.75rem', fontWeight: 700, color: 'slategray' }}>
                          {stock.rejection_reason || '-'}
                        </TableCell>
                        <TableCell sx={{ fontWeight: 800 }}>{stock.probability ? `${(stock.probability*100).toFixed(1)}%` : '-'}</TableCell>
                        <TableCell sx={{ fontWeight: 800, color: stock.ev > 0 ? 'success.main' : 'error.main' }}>
                          {stock.ev ? `+${stock.ev.toFixed(2)}` : '-'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
           </Paper>
        </Grid>

        {/* Diagnostics Section */}
        <Grid item xs={12} sx={{ mt: 4 }}>
          <Accordion sx={{ bgcolor: alpha('#000', 0.2), border: '1px solid rgba(255,255,255,0.05)' }}>
            <AccordionSummary expandIcon={<ChevronDown color="gray" />}>
              <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray', display: 'flex', alignItems: 'center', gap: 1 }}>
                <Terminal size={14} /> SYSTEM DIAGNOSTICS
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={4}>
                <Grid item xs={12} md={4}>
                  <DiagItem icon={<Database size={14} />} label="API ENDPOINT" value={API_BASE_URL} />
                </Grid>
                <Grid item xs={12} md={4}>
                  <DiagItem icon={<Cloud size={14} />} label="FIREBASE PROJECT" value="com-webcraft-trademindai-c8f75" />
                </Grid>
                <Grid item xs={12} md={4}>
                  <DiagItem icon={<Clock size={14} />} label="CLIENT FETCH TS" value={lastRefreshed.toISOString()} />
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>
      </Grid>

      {/* Detail Dialog */}
      <Dialog
        open={!!selectedSignal}
        onClose={() => { setSelectedSignal(null); setFullDetail(null); }}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { bgcolor: '#0a0a0a', border: '1px solid rgba(255,255,255,0.1)' } }}
      >
         {selectedSignal && (
           <>
             <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <Typography variant="h6" sx={{ fontWeight: 900, display: 'flex', alignItems: 'center', gap: 2 }}>
                   SIGNAL ANALYTICS: {selectedSignal.symbol}
                </Typography>
                <IconButton onClick={() => { setSelectedSignal(null); setFullDetail(null); }} size="small">
                   <X size={18} />
                </IconButton>
             </DialogTitle>
             <DialogContent sx={{ p: 4 }}>
                <SignalDetailView signal={fullDetail || selectedSignal} loading={detailLoading} />
             </DialogContent>
           </>
         )}
      </Dialog>
    </Box>
  );
}

function StatusChip({ status }: { status: string }) {
  const colors: any = {
    'ACTIVE': { bg: alpha('#00D1FF', 0.1), text: '#00D1FF' },
    'TARGET_HIT': { bg: alpha('#10b981', 0.1), text: '#10b981' },
    'STOP_LOSS': { bg: alpha('#ef4444', 0.1), text: '#ef4444' },
    'TIMEOUT': { bg: alpha('#f59e0b', 0.1), text: '#f59e0b' },
    'EXPIRED': { bg: alpha('#6b7280', 0.1), text: '#6b7280' },
    'REJECTED': { bg: alpha('#ef4444', 0.1), text: '#ef4444' },
    'CANCELLED': { bg: alpha('#6b7280', 0.1), text: '#6b7280' }
  };

  const style = colors[status] || { bg: alpha('#fff', 0.05), text: '#fff' };

  return (
    <Chip
      label={status}
      size="small"
      sx={{
        fontWeight: 900, fontSize: '0.55rem', height: 18,
        bgcolor: style.bg, color: style.text, borderRadius: 0.5
      }}
    />
  );
}

function DetailItem({ label, value, color, bold }: any) {
  return (
    <Box sx={{ mb: 2 }}>
       <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, display: 'block', mb: 0.5, letterSpacing: 1 }}>{label}</Typography>
       <Typography variant="body2" sx={{ fontWeight: bold ? 900 : 700, color: color || 'text.primary', fontFamily: 'JetBrains Mono' }}>{value || 'N/A'}</Typography>
    </Box>
  );
}

function StatusBadge({ label, status, color }: any) {
  return (
    <Box sx={{ px: 2, py: 0.8, borderRadius: 1, border: `1px solid ${alpha(color, 0.2)}`, bgcolor: alpha(color, 0.05) }}>
       <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 950, fontSize: '0.65rem', mr: 1.5 }}>{label}:</Typography>
       <Typography variant="caption" sx={{ color: color, fontWeight: 950, fontSize: '0.65rem' }}>{status}</Typography>
    </Box>
  );
}

function PerfRow({ label, value, baseline }: any) {
  return (
    <Box>
       <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
          <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray' }}>{label}</Typography>
          <Typography variant="caption" sx={{ fontWeight: 900, color: 'primary.main' }}>LIVE: {value}</Typography>
       </Stack>
       <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="body2" sx={{ fontWeight: 800 }}>BASELINE: {baseline}</Typography>
          <Chip label="FROZEN" size="small" sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900, bgcolor: alpha('#fff', 0.05) }} />
       </Stack>
       <Divider sx={{ mt: 1.5, opacity: 0.05 }} />
    </Box>
  );
}

function MetricCard({ title, value, icon }: any) {
  return (
    <Paper sx={{ p: 2.5, border: '1px solid rgba(255,255,255,0.05)' }}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray', letterSpacing: 1.5 }}>{title}</Typography>
          <Typography variant="h4" sx={{ fontWeight: 950, mt: 1, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
        </Box>
        <Box sx={{ p: 1, bgcolor: alpha('#fff', 0.03), borderRadius: 1 }}>{icon}</Box>
      </Stack>
    </Paper>
  );
}

function DiagItem({ icon, label, value }: any) {
  return (
    <Box>
      <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
        {icon} {label}
      </Typography>
      <Typography variant="body2" sx={{ fontFamily: 'JetBrains Mono', fontSize: '0.7rem', color: 'primary.main', wordBreak: 'break-all' }}>
        {value}
      </Typography>
    </Box>
  );
}

function TimelineItem({ label, time, active }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: active ? 1 : 0.3 }}>
       <Typography variant="caption" sx={{ fontWeight: 900, fontSize: '0.6rem' }}>{label}</Typography>
       <Typography variant="caption" sx={{ fontFamily: 'JetBrains Mono', fontSize: '0.6rem' }}>{time || '--'}</Typography>
    </Box>
  );
}
