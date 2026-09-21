import { useState, useEffect, useMemo } from 'react';
import { Box, Typography, Grid, Stack, Tab, Tabs, Button, Divider, InputBase, alpha, IconButton, Paper, Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TablePagination, Chip as MuiChip, Select, MenuItem, FormControl, InputLabel, Dialog, DialogTitle, DialogContent, DialogActions } from '@mui/material';
import { ShieldAlert, RefreshCw, Search, Activity, Info, Clock, CheckCircle, XCircle, AlertCircle, LayoutGrid, List as ListIcon, Columns } from 'lucide-react';
import { getEquitySignals, getEquityHistory } from '../api/client';
import { mapCanonicalSignal } from '../hooks/useAITradeDecision';
import { useTurboSync } from '../hooks/useTurboSync';
import LiveSignalCard from '../components/Research/shared/LiveSignalCard';
import { useNavigate } from 'react-router-dom';

export default function EquitySignals() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<'ACTIVE' | 'HISTORY'>('ACTIVE');
  const [activeTab, setActiveTab] = useState(0); // Default to ALL ACTIVE (index 0)
  const [signals, setSignals] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('NEWEST');

  // UI State
  const [viewLayout, setViewLayout] = useState<'GRID' | 'TABLE'>('GRID');
  const [selectedForCompare, setSelectedForCompare] = useState<string[]>([]);
  const [isCompareOpen, setIsCompareOpen] = useState(false);

  // History Pagination & Filters
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [totalHistory, setTotalHistory] = useState(0);
  const [historySummary, setHistorySummary] = useState<any>(null);

  const [hFilterHorizon, setHFilterHorizon] = useState('ALL');
  const [hFilterQuality, setHFilterQuality] = useState('ALL');
  const [hFilterStatus, setHFilterStatus] = useState('ALL');
  const [hFilterDirection, setHFilterDirection] = useState('ALL');

  const { connectionStatus, firestoreSignals } = useTurboSync();

  // Canonical Signal Universes (V2.3)
  const universes = useMemo(() => [
    { label: 'ALL ACTIVE', value: 'ALL', color: '#00D1FF' },
    { label: 'SWING', value: 'SWING', color: '#10b981' },
    { label: 'SHORT HORIZON', value: 'SHORT', color: '#708090' },
    { label: 'LONG HORIZON', value: 'LONG', color: '#00D1FF' }
  ], []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      if (mode === 'ACTIVE') {
        const signalsData = await getEquitySignals({ limit: 100 });
        console.log(`[Forensic] Received Active Signals: ${signalsData?.length || 0}`);
        if (!signalsData || !Array.isArray(signalsData)) {
            throw new Error("Invalid response format from signal service.");
        }
        const normalized = signalsData.map((s: any) => mapCanonicalSignal(s));

        setSignals(prev => {
            const mergedMap = new Map();
            prev.forEach((s: any) => mergedMap.set(s.id, s));
            normalized.forEach((s: any) => mergedMap.set(s.id, s));
            return Array.from(mergedMap.values()).sort((a: any, b: any) => {
                const timeA = new Date(a.decision?.generatedAt || 0).getTime();
                const timeB = new Date(b.decision?.generatedAt || 0).getTime();
                return timeB - timeA;
            });
        });
      } else {
        const params: any = {
            page: mode === 'HISTORY' ? page + 1 : 1,
            limit: mode === 'HISTORY' ? rowsPerPage : 100,
            symbol: searchQuery || undefined,
            horizon: hFilterHorizon !== 'ALL' ? hFilterHorizon : undefined,
            quality: hFilterQuality !== 'ALL' ? hFilterQuality : undefined,
            status: hFilterStatus !== 'ALL' ? hFilterStatus : undefined,
            direction: hFilterDirection !== 'ALL' ? hFilterDirection : undefined
        };
        const historyData = await getEquityHistory(params);
        if (!historyData || !historyData.records) {
            throw new Error("Invalid response format from history service.");
        }
        const records = (historyData.records || []).map((r: any) => mapCanonicalSignal(r));
        setHistory(records);
        setTotalHistory(historyData.total || 0);
        setHistorySummary(historyData.summary || null);
      }
    } catch (e: any) {
      console.error("Failed to sync equity data:", e);
      setError(e.message || "Failed to synchronize with authoritative signal ledger.");
    } finally {
      setLoading(false);
      console.log(`[Forensic] Sync Complete. Mode: ${mode}, Signals: ${signals.length}, Tab: ${activeTab}`);
    }
  };

  useEffect(() => {
    fetchData();
  }, [mode, page, rowsPerPage, hFilterHorizon, hFilterQuality, hFilterStatus, hFilterDirection]);

  // Hybrid Data Integration (V2.3)
  // Authoritatively merges REST API and Firestore Shadow Mirror
  useEffect(() => {
    if (firestoreSignals.length === 0) return;

    const fsSignals = firestoreSignals.map(s => ({ ...mapCanonicalSignal(s), _isFirestore: true }));
    console.log(`[Forensic] Merging ${fsSignals.length} Firestore signals into state...`);

    setSignals(prev => {
        const mergedMap = new Map();

        // Add existing signals to map
        prev.forEach(s => mergedMap.set(s.id, s));

        // Overwrite/Add with Firestore signals
        fsSignals.forEach(s => mergedMap.set(s.id, s));

        const merged = Array.from(mergedMap.values()).sort((a, b) =>
            new Date(b.decision?.generatedAt || 0).getTime() - new Date(a.decision?.generatedAt || 0).getTime()
        );
        console.log(`[Forensic] State now has ${merged.length} total signals.`);
        return merged;
    });
  }, [firestoreSignals]);

  const counts = useMemo(() => {
    return {
      all: signals.length,
      swing: signals.filter(s => s.decision.timeframe === 'SWING').length,
      short: signals.filter(s => s.decision.timeframe === 'SHORT').length,
      long: signals.filter(s => s.decision.timeframe === 'LONG').length
    };
  }, [signals]);

  const filteredActiveSignals = useMemo(() => {
    const universe = universes[activeTab].value;

    return signals.filter(s => {
        // V2.3 Hybrid: Ensure we only show truly ACTIVE signals in this mode
        const isActive = ['ACTIVE', 'WAITING_FOR_ENTRY', 'ENTRY_TRIGGERED'].includes(s.decision.status);
        if (!isActive) return false;

        const matchesSearch = s.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
                             (s.company_name?.toLowerCase().includes(searchQuery.toLowerCase()));

        if (!matchesSearch) return false;

        if (universe === 'ALL') return true;
        if (universe === 'SWING') return s.decision.timeframe === 'SWING';
        if (universe === 'SHORT') return s.decision.timeframe === 'SHORT';
        if (universe === 'LONG') return s.decision.timeframe === 'LONG';

        return false;
    });
  }, [signals, activeTab, searchQuery, universes]);

  const toggleCompare = (id: string) => {
    setSelectedForCompare(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : (prev.length < 4 ? [...prev, id] : prev)
    );
  };

  const comparedSignals = useMemo(() => {
    const source = mode === 'ACTIVE' ? signals : history;
    return source.filter(s => selectedForCompare.includes(s.id));
  }, [signals, history, mode, activeTab, searchQuery, universes]);

  const finalDisplaySignals = useMemo(() => {
    let source = mode === 'ACTIVE' ? [...filteredActiveSignals] : [...history];
    if (sortBy === 'PROBABILITY') source.sort((a, b) => (b.decision?.conviction || 0) - (a.decision?.conviction || 0));
    if (sortBy === 'EV') source.sort((a, b) => (b.decision?.expectedValue || 0) - (a.decision?.expectedValue || 0));
    if (sortBy === 'NEWEST') source.sort((a, b) => new Date(b.decision?.generatedAt || 0).getTime() - new Date(a.decision?.generatedAt || 0).getTime());
    return source;
  }, [filteredActiveSignals, history, mode, sortBy]);

  const latestUpdate = signals.length > 0 ? new Date(signals[0].decision?.generatedAt).toLocaleTimeString() : '—';

  return (
    <Box sx={{ pb: 10, bgcolor: '#020617', minHeight: '100vh', mx: -4, px: 4, pt: 2 }}>
      {/* 1. Terminal Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', mb: 5, flexWrap: 'wrap', gap: 3 }}>
         <Box>
            <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1, color: '#fff' }}>SIGNAL TERMINAL</Typography>
            <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
               <Typography variant="caption" sx={{ fontWeight: 900, color: '#10b981', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Activity size={14} /> LIVE SHADOW SCAN
               </Typography>
               <Divider orientation="vertical" flexItem sx={{ height: 12, my: 'auto', bgcolor: 'rgba(255,255,255,0.1)' }} />
               <Typography variant="caption" sx={{ fontWeight: 800, color: connectionStatus === 'ONLINE' ? '#10b981' : '#ef4444' }}>
                  NODE: {connectionStatus} (SHADOW MODE)
               </Typography>
            </Stack>
         </Box>

         <Stack direction="row" spacing={2} alignItems="center">
            <Box sx={{
               display: 'flex',
               alignItems: 'center',
               bgcolor: '#0f172a',
               border: '1px solid rgba(255,255,255,0.08)',
               borderRadius: 1,
               px: 2,
               width: { xs: '100%', sm: 320 },
               height: 48,
               transition: '0.2s',
               '&:focus-within': { borderColor: '#10b981', bgcolor: '#111827', boxShadow: '0 0 0 2px rgba(16, 185, 129, 0.1)' }
            }}>
               <Search size={18} color="#708090" />
               <InputBase
                  placeholder="SEARCH SYMBOL OR ID..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => { if (e.key === 'Enter') fetchData(); }}
                  sx={{ ml: 1.5, flex: 1, fontSize: '0.8rem', fontWeight: 800, color: 'white' }}
               />
            </Box>
            <IconButton onClick={fetchData} sx={{ border: '1px solid rgba(255,255,255,0.08)', borderRadius: 1, p: 1.5, bgcolor: '#0f172a' }}>
               <RefreshCw size={20} className={loading ? 'animate-spin' : ''} color="#708090" />
            </IconButton>
         </Stack>
      </Box>

      {/* 2. Mode Switch & Controls */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
         <Stack direction="row" spacing={1}>
            <ModeButton active={mode === 'ACTIVE'} onClick={() => { setMode('ACTIVE'); setPage(0); setSearchQuery(''); }}>ACTIVE SIGNALS</ModeButton>
            <ModeButton active={mode === 'HISTORY'} onClick={() => { setMode('HISTORY'); setPage(0); setSearchQuery(''); }}>SIGNAL HISTORY</ModeButton>
         </Stack>

         <Stack direction="row" spacing={1}>
            <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel sx={{ color: '#708090', fontSize: '0.6rem', fontWeight: 900 }}>DISPLAY RANKING</InputLabel>
                <Select
                    value={sortBy}
                    label="DISPLAY RANKING"
                    onChange={(e) => setSortBy(e.target.value)}
                    sx={{ height: 40, bgcolor: '#0f172a', color: 'white', fontWeight: 800, fontSize: '0.7rem', '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.08)' } }}
                >
                    <MenuItem value="NEWEST" sx={{ fontSize: '0.7rem', fontWeight: 700 }}>NEWEST</MenuItem>
                    <MenuItem value="PROBABILITY" sx={{ fontSize: '0.7rem', fontWeight: 700 }}>PROBABILITY</MenuItem>
                    <MenuItem value="EV" sx={{ fontSize: '0.7rem', fontWeight: 700 }}>EXPECTED VALUE</MenuItem>
                </Select>
            </FormControl>
            <Divider orientation="vertical" flexItem sx={{ mx: 1, opacity: 0.1 }} />
            {mode === 'ACTIVE' && (
                <>
                    <IconButton onClick={() => setViewLayout('GRID')} sx={{ color: viewLayout === 'GRID' ? '#00D1FF' : '#708090' }}>
                        <LayoutGrid size={20} />
                    </IconButton>
                    <IconButton onClick={() => setViewLayout('TABLE')} sx={{ color: viewLayout === 'TABLE' ? '#00D1FF' : '#708090' }}>
                        <ListIcon size={20} />
                    </IconButton>
                </>
            )}
            <Divider orientation="vertical" flexItem sx={{ mx: 1, opacity: 0.1 }} />
            <Button
                variant="outlined"
                size="small"
                startIcon={<Columns size={16} />}
                disabled={selectedForCompare.length < 2}
                onClick={() => setIsCompareOpen(true)}
                sx={{ fontWeight: 900, fontSize: '0.65rem', borderColor: '#00D1FF', color: '#00D1FF' }}
            >
                COMPARE {selectedForCompare.length > 0 ? `(${selectedForCompare.length})` : ''}
            </Button>
         </Stack>
      </Box>

      {mode === 'ACTIVE' ? (
        <>
            {/* 3. Active Signal Summary */}
            <Grid container spacing={2} sx={{ mb: 4 }}>
                <Grid item xs={6} md={3}>
                    <SummaryStat label="TOTAL OPEN" value={counts.all} color="#00D1FF" />
                </Grid>
                <Grid item xs={6} md={3}>
                    <SummaryStat label="SWING" value={counts.swing} color="#10b981" />
                </Grid>
                <Grid item xs={6} md={3}>
                    <SummaryStat label="LONG" value={counts.long} color="#00D1FF" />
                </Grid>
                <Grid item xs={6} md={3}>
                    <SummaryStat label="SHORT" value={counts.short} color="#708090" />
                </Grid>
            </Grid>

            {/* 4. Active Universe Selectors */}
            <Paper sx={{ mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 1, p: 0.5, width: 'fit-content' }}>
                <Tabs
                    value={activeTab}
                    onChange={(_, v) => setActiveTab(v)}
                    sx={{
                        minHeight: 44,
                        '& .MuiTabs-indicator': { height: 3, bgcolor: universes[activeTab].color },
                        '& .MuiTab-root': {
                            color: '#708090',
                            fontWeight: 950,
                            fontSize: '0.7rem',
                            minWidth: 160,
                            textTransform: 'none',
                            '&.Mui-selected': { color: 'white' }
                        }
                    }}
                >
                    {universes.map((u) => (
                        <Tab key={u.value} label={u.label} />
                    ))}
                </Tabs>
            </Paper>

            {/* 5. Signal Data Presentation */}
            {loading ? (
                <Grid container spacing={3}>
                    {[1,2,3,4,5,6].map(i => (
                        <Grid item xs={12} md={6} lg={4} key={i}>
                            <Skeleton variant="rectangular" height={450} sx={{ borderRadius: 1, bgcolor: 'rgba(255,255,255,0.02)' }} />
                        </Grid>
                    ))}
                </Grid>
            ) : error ? (
                <Paper sx={{ py: 15, textAlign: 'center', bgcolor: alpha('#ef4444', 0.05), border: '1px dashed #ef4444', borderRadius: 1 }}>
                    <ShieldAlert size={56} color="#ef4444" style={{ margin: '0 auto 24px', opacity: 0.5 }} />
                    <Typography variant="h6" sx={{ fontWeight: 950, color: 'white', mb: 1 }}>CONNECTION FAILED</Typography>
                    <Typography variant="body2" sx={{ color: '#708090', mb: 4, maxWidth: 400, mx: 'auto' }}>{error}</Typography>
                    <Button variant="outlined" onClick={fetchData} startIcon={<RefreshCw size={16} />}>RETRY SYNCHRONIZATION</Button>
                </Paper>
            ) : (
                <Box>
                    {finalDisplaySignals.length > 0 ? (
                        viewLayout === 'GRID' && mode === 'ACTIVE' ? (
                            <Grid container spacing={3}>
                                {finalDisplaySignals.map((s) => (
                                    <Grid item xs={12} md={6} lg={4} key={s.id}>
                                        <Box sx={{ position: 'relative', height: '100%' }}>
                                            <LiveSignalCard stock={s} decision={s.decision} variant="SIMPLE" />
                                            <MuiChip
                                                label={selectedForCompare.includes(s.id) ? "SELECTED" : "COMPARE"}
                                                onClick={() => toggleCompare(s.id)}
                                                size="small"
                                                sx={{
                                                    position: 'absolute', top: 10, right: 80,
                                                    zIndex: 10, height: 20, fontSize: '0.5rem',
                                                    fontWeight: 950, cursor: 'pointer',
                                                    bgcolor: selectedForCompare.includes(s.id) ? '#00D1FF' : 'rgba(0,0,0,0.4)',
                                                    color: selectedForCompare.includes(s.id) ? '#000' : 'white',
                                                    '&:hover': { bgcolor: '#00D1FF', color: '#000' }
                                                }}
                                            />
                                        </Box>
                                    </Grid>
                                ))}
                            </Grid>
                        ) : (
                            <TableContainer component={Paper} sx={{ bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1 }}>
                                <Table sx={{ minWidth: 1200 }}>
                                    <TableHead sx={{ bgcolor: 'rgba(255,255,255,0.01)' }}>
                                        <TableRow>
                                            <TableCell padding="checkbox" />
                                            <TableCell>SYMBOL</TableCell>
                                            <TableCell>DIRECTION</TableCell>
                                            <TableCell>HORIZON</TableCell>
                                            <TableCell>ENTRY</TableCell>
                                            <TableCell>CURRENT/EXIT</TableCell>
                                            <TableCell>TARGET</TableCell>
                                            <TableCell>STOP</TableCell>
                                            <TableCell>PROBABILITY</TableCell>
                                            <TableCell>EV</TableCell>
                                            <TableCell align="right">ACTION</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {finalDisplaySignals.map((s) => (
                                            <TableRow key={s.id} hover onClick={() => navigate(`/signals/${s.id}`)} sx={{ cursor: 'pointer' }}>
                                                <TableCell padding="checkbox">
                                                    <MuiChip
                                                        size="small"
                                                        onClick={(e) => { e.stopPropagation(); toggleCompare(s.id); }}
                                                        sx={{
                                                            height: 18, width: 18, minWidth: 0, p: 0,
                                                            bgcolor: selectedForCompare.includes(s.id) ? '#00D1FF' : 'transparent',
                                                            border: '1px solid rgba(255,255,255,0.1)'
                                                        }}
                                                    />
                                                </TableCell>
                                                <TableCell sx={{ fontWeight: 950 }}>{s.symbol}</TableCell>
                                                <TableCell>
                                                    <Typography sx={{ fontWeight: 900, color: s.decision.rating.includes('BUY') ? '#10b981' : '#ef4444', fontSize: '0.75rem' }}>
                                                        {s.decision.rating}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell sx={{ fontWeight: 700, fontSize: '0.7rem' }}>{s.decision.timeframe}</TableCell>
                                                <TableCell sx={{ fontFamily: 'JetBrains Mono' }}>₹{s.decision.entry?.toLocaleString()}</TableCell>
                                                <TableCell sx={{ fontFamily: 'JetBrains Mono' }}>₹{(s.decision.normalizedCurrentPrice || s.decision.exitPrice)?.toLocaleString()}</TableCell>
                                                <TableCell sx={{ fontFamily: 'JetBrains Mono', color: '#10b981' }}>₹{s.decision.target?.toLocaleString()}</TableCell>
                                                <TableCell sx={{ fontFamily: 'JetBrains Mono', color: '#ef4444' }}>₹{s.decision.stopLoss?.toLocaleString()}</TableCell>
                                                <TableCell sx={{ fontWeight: 800 }}>{s.decision.conviction}%</TableCell>
                                                <TableCell sx={{ fontFamily: 'JetBrains Mono' }}>₹{s.decision.expectedValue?.toFixed(1)}</TableCell>
                                                <TableCell align="right">
                                                    <Button size="small" sx={{ fontWeight: 900, fontSize: '0.65rem' }}>TERMINAL</Button>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        )
                    ) : (
                        <Paper sx={{ py: 20, textAlign: 'center', bgcolor: alpha('#0f172a', 0.5), border: '1px dashed rgba(255,255,255,0.05)', borderRadius: 1 }}>
                            <ShieldAlert size={56} color="#708090" style={{ margin: '0 auto 24px', opacity: 0.2 }} />
                            <Typography variant="h6" sx={{ fontWeight: 900, color: '#708090', letterSpacing: 1 }}>
                                {universes[activeTab].label} — NO QUALIFIED SIGNALS
                            </Typography>
                        </Paper>
                    )}
                </Box>
            )}
        </>
      ) : (
        /* 6. Signal History View */
        <Box>
            <Grid container spacing={2} sx={{ mb: 4 }}>
                <Grid item xs={12} md={2.4}><SummaryStat label="TOTAL HISTORY" value={historySummary?.total || 0} color="#00D1FF" /></Grid>
                <Grid item xs={6} md={2.4}><SummaryStat label="TARGET HITS" value={historySummary?.target_hits || 0} color="#10b981" /></Grid>
                <Grid item xs={6} md={2.4}><SummaryStat label="STOP LOSSES" value={historySummary?.stop_losses || 0} color="#ef4444" /></Grid>
                <Grid item xs={6} md={2.4}><SummaryStat label="EXPIRED" value={historySummary?.expired || 0} color="orange" /></Grid>
                <Grid item xs={6} md={2.4}><SummaryStat label="OTHER" value={historySummary?.other || 0} color="#708090" /></Grid>
            </Grid>

            <Paper sx={{ p: 2, mb: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1 }}>
               <Grid container spacing={3} alignItems="center">
                  <Grid item xs={12} md={2.4}><HistorySelect label="DIRECTION" value={hFilterDirection} onChange={setHFilterDirection} options={['ALL', 'LONG', 'SHORT']} /></Grid>
                  <Grid item xs={12} md={2.4}><HistorySelect label="HORIZON" value={hFilterHorizon} onChange={setHFilterHorizon} options={['ALL', 'SWING', 'SHORT', 'LONG']} /></Grid>
                  <Grid item xs={12} md={2.4}><HistorySelect label="QUALITY" value={hFilterQuality} onChange={setHFilterQuality} options={['ALL', 'PRIMARY', 'SELECTIVE', 'EXPERIMENTAL']} /></Grid>
                  <Grid item xs={12} md={2.4}><HistorySelect label="OUTCOME" value={hFilterStatus} onChange={setHFilterStatus} options={['ALL', 'TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'CANCELLED']} /></Grid>
                  <Grid item xs={12} md={2.4}>
                     <Button
                        fullWidth
                        variant="outlined"
                        onClick={() => { setHFilterDirection('ALL'); setHFilterHorizon('ALL'); setHFilterQuality('ALL'); setHFilterStatus('ALL'); setSearchQuery(''); }}
                        startIcon={<RefreshCw size={14} />}
                        sx={{ height: 40, fontWeight: 900, borderColor: 'rgba(255,255,255,0.1)', color: '#708090' }}
                     >
                        RESET FILTERS
                     </Button>
                  </Grid>
               </Grid>
            </Paper>

            <TableContainer component={Paper} sx={{ bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1 }}>
               <Table sx={{ minWidth: 1400 }}>
                  <TableHead sx={{ bgcolor: 'rgba(255,255,255,0.01)' }}>
                     <TableRow>
                        <TableCell padding="checkbox" />
                        <TableCell>DATE</TableCell>
                        <TableCell>SYMBOL</TableCell>
                        <TableCell>SIGNAL ID</TableCell>
                        <TableCell>DIRECTION</TableCell>
                        <TableCell>HORIZON</TableCell>
                        <TableCell>QUALITY</TableCell>
                        <TableCell>ENTRY</TableCell>
                        <TableCell>EXIT</TableCell>
                        <TableCell>OUTCOME</TableCell>
                        <TableCell>RETURN %</TableCell>
                        <TableCell>PROB</TableCell>
                        <TableCell align="right">ACTION</TableCell>
                     </TableRow>
                  </TableHead>
                  <TableBody>
                     {loading ? (
                        [1,2,3,4,5].map(i => (
                           <TableRow key={i}><TableCell colSpan={12}><Skeleton height={40} /></TableCell></TableRow>
                        ))
                     ) : history.length > 0 ? (
                        history.map((s) => (
                           <TableRow key={s.id} hover sx={{ '&:hover': { bgcolor: 'rgba(255,255,255,0.02)' } }}>
                              <TableCell padding="checkbox">
                                  <MuiChip
                                      size="small"
                                      onClick={(e) => { e.stopPropagation(); toggleCompare(s.id); }}
                                      sx={{
                                          height: 18, width: 18, minWidth: 0, p: 0,
                                          bgcolor: selectedForCompare.includes(s.id) ? '#00D1FF' : 'transparent',
                                          border: '1px solid rgba(255,255,255,0.1)'
                                      }}
                                  />
                              </TableCell>
                              <TableCell sx={{ fontWeight: 700, color: '#708090', fontSize: '0.7rem' }}>{new Date(s.decision?.generatedAt).toLocaleDateString()}</TableCell>
                              <TableCell><Typography sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', fontSize: '0.85rem' }}>{s.symbol}</Typography></TableCell>
                              <TableCell sx={{ fontSize: '0.6rem', color: '#708090', fontFamily: 'JetBrains Mono' }}>{s.id}</TableCell>
                              <TableCell>
                                 <MuiChip
                                    label={s.decision.rating}
                                    size="small"
                                    sx={{
                                        fontWeight: 950, fontSize: '0.55rem', height: 20,
                                        bgcolor: alpha(s.decision.rating.includes('BUY') ? '#10b981' : '#ef4444', 0.1),
                                        color: s.decision.rating.includes('BUY') ? '#10b981' : '#ef4444'
                                    }}
                                 />
                              </TableCell>
                              <TableCell sx={{ fontWeight: 800, fontSize: '0.65rem' }}>{s.decision.timeframe}</TableCell>
                              <TableCell>
                                 <MuiChip
                                    label={s.decision.qualityClass}
                                    size="small"
                                    variant="outlined"
                                    sx={{
                                        height: 18, fontSize: '0.5rem', fontWeight: 900,
                                        borderColor: s.decision.qualityClass === 'PRIMARY' ? '#10b981' : s.decision.qualityClass === 'SELECTIVE' ? '#00D1FF' : '#708090',
                                        color: s.decision.qualityClass === 'PRIMARY' ? '#10b981' : s.decision.qualityClass === 'SELECTIVE' ? '#00D1FF' : '#708090'
                                    }}
                                 />
                              </TableCell>
                              <TableCell sx={{ fontFamily: 'JetBrains Mono', fontSize: '0.8rem' }}>₹{s.decision.entry?.toLocaleString()}</TableCell>
                              <TableCell sx={{ fontFamily: 'JetBrains Mono', fontSize: '0.8rem' }}>{s.decision.exitPrice ? `₹${s.decision.exitPrice.toLocaleString()}` : '—'}</TableCell>
                              <TableCell><OutcomeBadge outcome={s.decision.status} /></TableCell>
                              <TableCell sx={{ fontWeight: 900, color: (s.decision.realizedReturn || 0) >= 0 ? '#10b981' : '#ef4444', fontSize: '0.8rem' }}>
                                 {s.decision.realizedReturn !== undefined ? `${s.decision.realizedReturn > 0 ? '+' : ''}${s.decision.realizedReturn.toFixed(2)}%` : '—'}
                              </TableCell>
                              <TableCell sx={{ fontWeight: 800, color: '#00D1FF', fontSize: '0.8rem' }}>{s.decision?.conviction}%</TableCell>
                              <TableCell align="right">
                                 <Stack direction="row" spacing={1} justifyContent="flex-end">
                                     <Button
                                        size="small"
                                        onClick={() => navigate(`/signals/${s.id}`, { state: { scrollReplay: true } })}
                                        sx={{ fontWeight: 900, fontSize: '0.65rem', color: '#10b981' }}
                                     >
                                         REPLAY
                                     </Button>
                                     <Button
                                        size="small"
                                        onClick={() => navigate(`/signals/${s.id}`)}
                                        sx={{ fontWeight: 900, fontSize: '0.65rem' }}
                                     >
                                         DETAILS
                                     </Button>
                                 </Stack>
                              </TableCell>
                           </TableRow>
                        ))
                     ) : (
                        <TableRow>
                           <TableCell colSpan={12} sx={{ py: 10, textAlign: 'center' }}>
                              <Typography variant="body2" sx={{ color: '#708090', fontWeight: 700 }}>NO HISTORICAL RECORDS MATCHING CURRENT FILTERS</Typography>
                           </TableCell>
                        </TableRow>
                     )}
                  </TableBody>
               </Table>
               <TablePagination
                  component="div"
                  count={totalHistory}
                  page={page}
                  onPageChange={(_, p) => setPage(p)}
                  rowsPerPage={rowsPerPage}
                  onRowsPerPageChange={(e) => setRowsPerPage(parseInt(e.target.value, 10))}
                  rowsPerPageOptions={[25, 50, 100]}
                  sx={{ borderTop: '1px solid rgba(255,255,255,0.05)', color: '#708090' }}
               />
            </TableContainer>
        </Box>
      )}

      {/* 7. Comparison Dialog */}
      <Dialog open={isCompareOpen} onClose={() => setIsCompareOpen(false)} maxWidth="lg" fullWidth PaperProps={{ sx: { bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' } }}>
         <DialogTitle sx={{ color: 'white', fontWeight: 950 }}>SIGNAL COMPARISON</DialogTitle>
         <DialogContent>
            <TableContainer sx={{ mt: 2 }}>
               <Table>
                  <TableHead>
                     <TableRow>
                        <TableCell>METRIC</TableCell>
                        {comparedSignals.map(s => <TableCell key={s.id} sx={{ fontWeight: 950, color: '#00D1FF' }}>{s.symbol}</TableCell>)}
                     </TableRow>
                  </TableHead>
                  <TableBody>
                     <CompareRow label="PROBABILITY" values={comparedSignals.map(s => `${s.decision.conviction}%`)} />
                     <CompareRow label="EXPECTED VALUE" values={comparedSignals.map(s => `₹${s.decision.expectedValue?.toFixed(2)}`)} />
                     <CompareRow label="RISK / REWARD" values={comparedSignals.map(s => s.decision.riskReward)} />
                     <CompareRow label="HORIZON" values={comparedSignals.map(s => s.decision.timeframe)} />
                     <CompareRow label="QUALITY" values={comparedSignals.map(s => s.decision.qualityClass)} />
                     <CompareRow label="ENTRY" values={comparedSignals.map(s => `₹${s.decision.entry?.toLocaleString()}`)} />
                     <CompareRow label="TARGET" values={comparedSignals.map(s => `₹${s.decision.target?.toLocaleString()}`)} />
                     <CompareRow label="STOP" values={comparedSignals.map(s => `₹${s.decision.stopLoss?.toLocaleString()}`)} />
                     {mode === 'HISTORY' && (
                         <>
                            <CompareRow label="OUTCOME" values={comparedSignals.map(s => s.decision.status)} />
                            <CompareRow label="RETURN %" values={comparedSignals.map(s => `${s.decision.realizedReturn?.toFixed(2)}%`)} />
                            <CompareRow label="HOLDING" values={comparedSignals.map(s => `${s.decision.holdingPeriodDays} days`)} />
                         </>
                     )}
                  </TableBody>
               </Table>
            </TableContainer>
         </DialogContent>
         <DialogActions sx={{ p: 3 }}>
            <Button onClick={() => setIsCompareOpen(false)} sx={{ fontWeight: 900, color: 'white' }}>CLOSE</Button>
         </DialogActions>
      </Dialog>

      {/* 8. Footer Metadata */}
      <Box sx={{ mt: 10, p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 1 }}>
         <Stack direction="row" spacing={3} alignItems="flex-start">
            <Box sx={{ bgcolor: alpha('#10b981', 0.1), p: 1, borderRadius: 1 }}><Info size={20} color="#10b981" /></Box>
            <Box>
               <Typography variant="subtitle2" sx={{ fontWeight: 950, color: '#fff', mb: 0.5, letterSpacing: 1 }}>FORENSIC SIGNAL PROTOCOL</Typography>
               <Typography variant="caption" sx={{ color: '#708090', lineHeight: 1.6, display: 'block', fontWeight: 600 }}>
                  Authoritative signals are derived from institutional order flow and Strategy V2.2 breakout logic.
                  All historical outcomes are verified against NSE Spot closing nodes.
                  Latest sync confirmed at {latestUpdate} IST.
               </Typography>
            </Box>
         </Stack>
      </Box>
    </Box>
  );
}

function ModeButton({ active, children, onClick }: any) {
    return (
        <Button
            onClick={onClick}
            sx={{
                px: 3, py: 1,
                borderRadius: 0.5,
                bgcolor: active ? '#00D1FF' : 'transparent',
                color: active ? '#000' : '#708090',
                fontWeight: 950,
                fontSize: '0.75rem',
                border: active ? 'none' : '1px solid rgba(255,255,255,0.08)',
                '&:hover': { bgcolor: active ? '#00D1FF' : 'rgba(255,255,255,0.03)' }
            }}
        >
            {children}
        </Button>
    );
}

function SummaryStat({ label, value, color }: any) {
    return (
        <Paper sx={{ p: 2, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.03)', height: '100%' }}>
            <Typography variant="caption" sx={{ color: '#708090', fontWeight: 900, fontSize: '0.6rem', display: 'block', mb: 0.5 }}>{label}</Typography>
            <Typography variant="h4" sx={{ fontWeight: 950, color, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
        </Paper>
    );
}

function HistorySelect({ label, value, onChange, options }: any) {
    return (
        <FormControl fullWidth size="small">
            <InputLabel sx={{ color: '#708090', fontWeight: 800, fontSize: '0.7rem' }}>{label}</InputLabel>
            <Select value={value} label={label} onChange={(e) => onChange(e.target.value)}
                sx={{ bgcolor: 'rgba(255,255,255,0.02)', color: 'white', fontWeight: 800, fontSize: '0.75rem', '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.05)' } }}>
                {options.map((o: string) => (<MenuItem key={o} value={o} sx={{ fontSize: '0.75rem', fontWeight: 700 }}>{o.replace(/_/g, ' ')}</MenuItem>))}
            </Select>
        </FormControl>
    );
}

function OutcomeBadge({ outcome }: { outcome: string }) {
    let color = '#708090';
    let icon = <Clock size={12} />;
    if (outcome === 'TARGET_HIT') { color = '#10b981'; icon = <CheckCircle size={12} />; }
    if (outcome === 'STOP_LOSS' || outcome === 'STOP_HIT') { color = '#ef4444'; icon = <XCircle size={12} />; }
    if (outcome === 'EXPIRED') { color = 'orange'; icon = <AlertCircle size={12} />; }
    return (
        <Stack direction="row" spacing={1} alignItems="center" sx={{ color, fontWeight: 900, fontSize: '0.65rem' }}>
            {icon}
            <Typography variant="caption" sx={{ fontWeight: 950, fontSize: '0.65rem' }}>{outcome?.replace(/_/g, ' ')}</Typography>
        </Stack>
    );
}

function CompareRow({ label, values }: any) {
    return (
        <TableRow>
            <TableCell sx={{ fontWeight: 800, color: '#708090', fontSize: '0.65rem' }}>{label}</TableCell>
            {values.map((v: any, i: number) => <TableCell key={i} sx={{ fontWeight: 900, color: 'white', fontSize: '0.75rem' }}>{v || '—'}</TableCell>)}
        </TableRow>
    );
}
