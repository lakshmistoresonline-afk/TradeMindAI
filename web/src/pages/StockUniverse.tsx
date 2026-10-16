import React, { useState, useEffect } from 'react';
import {
  Container, Typography, Tabs, Tab, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, TextField, InputAdornment, Chip, CircularProgress,
  Alert, Stack, Button, Card, CardContent, Grid
} from '@mui/material';
import { Search, Database, ArrowUpRight, ArrowDownRight, RefreshCw } from 'lucide-react';
import { apiClient } from '../api/client';

interface UniverseMeta {
  id: string;
  label: string;
  description: string;
  count: number;
}

interface Constituent {
  symbol: string;
  name?: string;
  exchange?: string;
  last_price?: number;
  change?: number;
  volume?: number;
  updated_at?: string;
}

export default function StockUniverse() {
  const [universes, setUniverses] = useState<UniverseMeta[]>([]);
  const [activeTab, setActiveTab] = useState(0);
  const [constituents, setConstituents] = useState<Constituent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState<string | null>(null);

  const currentUniverse = universes[activeTab] || { id: 'NIFTY_50', label: 'NIFTY 50', count: 50 };

  useEffect(() => {
    fetchUniverses();
  }, []);

  useEffect(() => {
    if (universes.length > 0) {
      fetchConstituents(universes[activeTab].id);
    }
  }, [activeTab, universes]);

  const fetchUniverses = async () => {
    try {
      const res = await apiClient.get('/universes');
      if (Array.isArray(res.data) && res.data.length > 0) {
        setUniverses(res.data);
      } else {
        setUniverses([
          { id: 'NIFTY_50', label: 'NIFTY 50', description: 'Benchmark 50 stock index.', count: 50 },
          { id: 'NIFTY_100_EXCL', label: 'NIFTY 100 — Exclusive', description: 'NIFTY 100 excluding NIFTY 50.', count: 50 },
          { id: 'NIFTY_200_EXCL', label: 'NIFTY 200 — Exclusive', description: 'NIFTY 200 excluding NIFTY 50 and 100.', count: 100 },
          { id: 'NIFTY_500_EXCL', label: 'NIFTY 500 — Exclusive', description: 'Broad NIFTY 500 excluding higher tiers.', count: 300 }
        ]);
      }
    } catch (err) {
      console.error('Failed to fetch universes metadata:', err);
      setError('Could not load universe metadata.');
    }
  };

  const fetchConstituents = async (universeId: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get(`/universes/${universeId}/constituents`, {
        params: { limit: 100, search: searchQuery || undefined }
      });
      if (res.data && Array.isArray(res.data.constituents)) {
        setConstituents(res.data.constituents);
      } else {
        setConstituents([]);
      }
    } catch (err) {
      console.error('Failed to fetch constituents:', err);
      setError('Failed to load constituents for this universe.');
      setConstituents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchConstituents(currentUniverse.id);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Stack spacing={1} mb={4}>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Database size={28} color="#00D1FF" />
          <Typography variant="h4" fontWeight={900}>Stock Universe Explorer</Typography>
        </Stack>
        <Typography variant="body2" color="text.secondary">
          Four exclusive NIFTY stock tiers with verified mutual exclusion. Stocks are assigned to one tab only according to index priority (NIFTY 50 → 100 → 200 → 500).
        </Typography>
      </Stack>

      {/* Universe Metadata Summary Cards */}
      <Grid container spacing={2} mb={4}>
        {universes.map((u, idx) => (
          <Grid item xs={12} sm={6} md={3} key={u.id}>
            <Card
              sx={{
                cursor: 'pointer',
                borderColor: activeTab === idx ? 'primary.main' : 'rgba(255,255,255,0.08)',
                backgroundColor: activeTab === idx ? 'rgba(0, 209, 255, 0.04)' : 'rgba(15, 23, 42, 0.85)',
                transition: 'all 0.2s ease',
                '&:hover': { borderColor: 'primary.light' }
              }}
              onClick={() => setActiveTab(idx)}
            >
              <CardContent>
                <Stack spacing={1}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="subtitle2" color="primary.main">{u.label}</Typography>
                    <Chip label={`${u.count} Stocks`} size="small" color={activeTab === idx ? 'primary' : 'default'} />
                  </Stack>
                  <Typography variant="caption" color="text.secondary" sx={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {u.description}
                  </Typography>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Main Content Area */}
      <Paper sx={{ p: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, val) => setActiveTab(val)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}
        >
          {universes.map((u) => (
            <Tab key={u.id} label={`${u.label} (${u.count})`} sx={{ fontWeight: 800 }} />
          ))}
        </Tabs>

        {/* Controls */}
        <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center" spacing={2} mb={3}>
          <form onSubmit={handleSearchSubmit} style={{ width: '100%', maxWidth: 400 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search symbol or company name..."
              value={searchQuery}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search size={18} color="#94a3b8" />
                  </InputAdornment>
                ),
              }}
            />
          </form>
          <Button
            variant="outlined"
            size="small"
            startIcon={<RefreshCw size={16} />}
            onClick={() => fetchConstituents(currentUniverse.id)}
          >
            Refresh Data
          </Button>
        </Stack>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {/* Constituents Table */}
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell>Company Name</TableCell>
                <TableCell>Exchange</TableCell>
                <TableCell align="right">Last Price</TableCell>
                <TableCell align="right">Change</TableCell>
                <TableCell align="right">Volume</TableCell>
                <TableCell align="center">Freshness</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
                    <CircularProgress size={32} />
                  </TableCell>
                </TableRow>
              ) : constituents.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
                    <Typography variant="body2" color="text.secondary">No constituents found in this exclusive tier.</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                constituents.map((c) => (
                  <TableRow key={c.symbol} hover>
                    <TableCell>
                      <Typography variant="subtitle2" fontWeight={800} color="primary.main">{c.symbol}</Typography>
                    </TableCell>
                    <TableCell>{c.name || '—'}</TableCell>
                    <TableCell>
                      <Chip label={c.exchange || 'NSE'} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell align="right">
                      {c.last_price ? `₹${c.last_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}` : '—'}
                    </TableCell>
                    <TableCell align="right">
                      {c.change !== undefined && c.change !== null ? (
                        <Stack direction="row" alignItems="center" justifyContent="flex-end" spacing={0.5}>
                          {c.change >= 0 ? <ArrowUpRight size={16} color="#10b981" /> : <ArrowDownRight size={16} color="#f43f5e" />}
                          <Typography variant="body2" fontWeight={800} color={c.change >= 0 ? 'success.main' : 'error.main'}>
                            {c.change > 0 ? `+${c.change.toFixed(2)}%` : `${c.change.toFixed(2)}%`}
                          </Typography>
                        </Stack>
                      ) : '—'}
                    </TableCell>
                    <TableCell align="right">
                      {c.volume ? c.volume.toLocaleString('en-IN') : '—'}
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={c.last_price ? 'FRESH' : 'UNAVAILABLE'}
                        size="small"
                        color={c.last_price ? 'success' : 'default'}
                        variant={c.last_price ? 'filled' : 'outlined'}
                      />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
}
