import { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Grid, Paper, Stack, Chip,
  CircularProgress, alpha, LinearProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import {
  TrendingUp, Target
} from 'lucide-react';
import { apiClient } from '../api/client';

export default function OpportunityRadar() {
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const res = await apiClient.get('/shadow/intelligence/radar');
      setOpportunities(res.data);
    } catch (err) {
      console.error("Radar fetch failed", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 900 }}>OPPORTUNITY RADAR</Typography>
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>ALPHA DISCOVERY LAYER • NON-TRADE SIGNALS</Typography>
        </Box>
        <Stack direction="row" spacing={1}>
           <Chip label="LIVE SCANNING" color="primary" sx={{ fontWeight: 900 }} />
           <Chip label="200 SYMBOLS" variant="outlined" sx={{ fontWeight: 900 }} />
        </Stack>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
           <Paper sx={{ p: 3 }}>
              <TableContainer>
                 <Table size="small">
                    <TableHead>
                       <TableRow>
                          <TableCell>SYMBOL</TableCell>
                          <TableCell>CATEGORY</TableCell>
                          <TableCell>INTELLIGENCE SCORE</TableCell>
                          <TableCell>EVIDENCE THESIS</TableCell>
                          <TableCell>DATA FRESHNESS</TableCell>
                          <TableCell align="right">ACTION</TableCell>
                       </TableRow>
                    </TableHead>
                    <TableBody>
                       {opportunities.map((opp: any) => (
                          <TableRow key={opp.id} hover>
                             <TableCell sx={{ fontWeight: 900, color: 'primary.main', fontSize: '1rem' }}>{opp.symbol}</TableCell>
                             <TableCell>
                                <Chip
                                   label={opp.type}
                                   size="small"
                                   icon={opp.type.includes('ACCUMULATION') ? <Target size={12}/> : <TrendingUp size={12}/>}
                                   sx={{ fontWeight: 800, fontSize: '0.6rem', borderRadius: 0.5 }}
                                />
                             </TableCell>
                             <TableCell>
                                <Stack direction="row" spacing={2} alignItems="center">
                                   <Typography variant="body2" fontWeight={800} sx={{ minWidth: 40 }}>{opp.conviction_score}%</Typography>
                                   <LinearProgress
                                      variant="determinate"
                                      value={opp.conviction_score}
                                      sx={{
                                        flexGrow: 1,
                                        height: 6,
                                        borderRadius: 3,
                                        bgcolor: alpha('#fff', 0.05),
                                        '& .MuiLinearProgress-bar': {
                                          bgcolor: opp.conviction_score > 80 ? '#10b981' : '#3b82f6'
                                        }
                                      }}
                                   />
                                </Stack>
                             </TableCell>
                             <TableCell sx={{ maxWidth: 400 }}>
                                <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 600, fontSize: '0.8rem' }}>
                                   {opp.ai_thesis}
                                </Typography>
                             </TableCell>
                             <TableCell>
                                <Chip label="FRESH" size="small" sx={{ height: 18, fontSize: '0.55rem', fontWeight: 900, bgcolor: alpha('#10b981', 0.1), color: '#10b981' }} />
                             </TableCell>
                             <TableCell align="right">
                                <Chip label="RESEARCH" size="small" sx={{ cursor: 'pointer', fontWeight: 900 }} />
                             </TableCell>
                          </TableRow>
                       ))}
                    </TableBody>
                 </Table>
              </TableContainer>
           </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
