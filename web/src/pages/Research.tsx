import { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Grid, Paper, Stack, Chip, Divider,
  CircularProgress, Autocomplete, TextField
} from '@mui/material';
import { History, Search } from 'lucide-react';
import { apiClient, getStocks } from '../api/client';

export default function Research() {
  const [stocks, setStocks] = useState<any[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('RELIANCE');
  const [research, setResearch] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStocks().then(setStocks);
  }, []);

  const fetchStockData = useCallback(async (symbol: string) => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/shadow/research/stock/${symbol}`);
      setResearch(res.data);
    } catch (err) {
      console.error("Research fetch failed", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStockData(selectedSymbol);
  }, [fetchStockData, selectedSymbol]);

  return (
    <Box sx={{ pb: 8 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 6 }}>
        <Box>
           <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>RESEARCH TERMINAL</Typography>
           <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
              NIFTY-200 FORENSIC ENGINE
           </Typography>
        </Box>
        <Autocomplete
          sx={{ width: 350 }}
          options={stocks}
          getOptionLabel={(option) => `${option.symbol} - ${option.name}`}
          onChange={(_, newValue) => newValue && setSelectedSymbol(newValue.symbol)}
          renderInput={(params) => (
            <TextField
                {...params}
                label="Search Universe..."
                size="small"
                InputProps={{ ...params.InputProps, startAdornment: <Search size={16} style={{ marginLeft: 8, marginRight: -4, color: 'slategray' }} /> }}
            />
          )}
        />
      </Box>

      {loading ? (
         <Box sx={{ py: 20, textAlign: 'center' }}><CircularProgress size={32} /></Box>
      ) : (
         <Grid container spacing={4}>
            <Grid item xs={12} md={8}>
               <Paper sx={{ p: 4, mb: 4, borderLeft: '4px solid', borderColor: '#00D1FF', bgcolor: '#0f172a' }}>
                  <Typography variant="h3" sx={{ fontWeight: 950 }}>{selectedSymbol}</Typography>
                  <Typography variant="body2" sx={{ color: 'slategray', fontWeight: 800, mt: 1 }}>
                     {research?.technical_context?.sector || 'NIFTY-200 CONSTITUENT'}
                  </Typography>
                  <Divider sx={{ my: 3, opacity: 0.05 }} />
                  <Typography variant="body1" sx={{ color: 'text.secondary', lineHeight: 1.8, fontSize: '0.95rem' }}>
                     {research?.summary || "Analyzing institutional order flow and structural market alignment..."}
                  </Typography>
               </Paper>

               <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 4 }}>QUANTITATIVE PROFILE</Typography>
                  <Grid container spacing={4}>
                     <ProfileMetric label="PE RATIO" value="24.2" />
                     <ProfileMetric label="MARKET CAP" value="18.4T" />
                     <ProfileMetric label="RS RATING" value="82" color="#10b981" />
                     <ProfileMetric label="BETA" value="0.92" />
                  </Grid>
               </Paper>
            </Grid>

            <Grid item xs={12} md={4}>
               <Stack spacing={4}>
                  <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                     <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 3 }}>SIGNAL RELEVANCE</Typography>
                     <Typography variant="body2" sx={{ color: 'slategray', mb: 3 }}>
                        Current Strategy V2.2 context for {selectedSymbol}.
                     </Typography>
                     <Chip label="NO ACTIVE SIGNAL" variant="outlined" sx={{ fontWeight: 900, color: 'slategray' }} />
                  </Paper>

                  <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
                     <Typography variant="subtitle2" sx={{ fontWeight: 900, mb: 3 }}>HISTORICAL TREND</Typography>
                     <Box sx={{ py: 4, textAlign: 'center', border: '1px dashed rgba(255,255,255,0.05)' }}>
                        <History size={32} color="slategray" style={{ opacity: 0.2, marginBottom: 12 }} />
                        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>AUDIT DATA LOADING...</Typography>
                     </Box>
                  </Paper>
               </Stack>
            </Grid>
         </Grid>
      )}
    </Box>
  );
}

function ProfileMetric({ label, value, color = '#fff' }: any) {
   return (
      <Grid item xs={6}>
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, display: 'block', mb: 0.5 }}>{label}</Typography>
         <Typography variant="h5" sx={{ fontWeight: 950, color, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
      </Grid>
   );
}
