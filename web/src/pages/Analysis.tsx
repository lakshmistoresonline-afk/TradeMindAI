import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent, Autocomplete, TextField, CircularProgress, Stack } from '@mui/material';
import { Brain, Cpu, Zap, Search } from 'lucide-react';
import { getStocks } from '../api/client';
import AnalysisReport from '../components/AnalysisReport';

export default function Analysis() {
  const [stocks, setStocks] = useState<any[]>([]);
  const [selectedStock, setSelectedStock] = useState<any | null>(null);

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
              selectedStock.analysis ? (
                <AnalysisReport data={{ ...selectedStock.analysis, symbol: selectedStock.symbol }} />
              ) : (
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', py: 8 }}>
                  <CircularProgress sx={{ mb: 2 }} />
                  <Typography color="textSecondary">AI is processing {selectedStock.symbol}...</Typography>
                </Box>
              )
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
