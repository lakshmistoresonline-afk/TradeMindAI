import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Button, alpha, Skeleton } from '@mui/material';
import { BarChart2, Plus, ArrowRight } from 'lucide-react';
import { getUserCharts } from '../api/client';
import { useNavigate } from 'react-router-dom';

export default function MyCharts() {
  const [charts, setCharts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getUserCharts().then(data => {
        setCharts(data || []);
        setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <Box sx={{ pb: 10, maxWidth: 1200, mx: 'auto', p: 4, color: 'white' }}>
      <Box sx={{ mb: 6, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
           <Typography variant="h4" sx={{ fontWeight: 950, letterSpacing: -1 }}>MY CHARTS</Typography>
           <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, letterSpacing: 1.5 }}>
              SAVED TECHNICAL SETUPS & STRUCTURAL MARKERS
           </Typography>
        </Box>
        <Button variant="contained" startIcon={<Plus size={18} />} onClick={() => navigate('/signals')} sx={{ fontWeight: 950 }}>CREATE NEW CHART</Button>
      </Box>

      {loading ? (
        <Grid container spacing={3}>
           {[1,2,3].map(i => (
             <Grid item xs={12} md={4} key={i}><Skeleton variant="rectangular" height={240} sx={{ borderRadius: 1 }} /></Grid>
           ))}
        </Grid>
      ) : charts.length > 0 ? (
        <Grid container spacing={3}>
            {charts.map((c) => (
                <Grid item xs={12} md={4} key={c.id}>
                    <Paper sx={{ p: 3, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', '&:hover': { borderColor: 'primary.main' } }}>
                        <Typography variant="h6" sx={{ fontWeight: 950, mb: 1 }}>{c.symbol}</Typography>
                        <Typography variant="caption" sx={{ color: 'slategray', display: 'block', mb: 3 }}>{c.name}</Typography>
                        <Box sx={{ height: 100, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 0.5, mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <BarChart2 size={32} color="slategray" style={{ opacity: 0.3 }} />
                        </Box>
                        <Button fullWidth endIcon={<ArrowRight size={14} />} sx={{ fontWeight: 800, color: 'primary.main' }}>OPEN SETUP</Button>
                    </Paper>
                </Grid>
            ))}
        </Grid>
      ) : (
        <Paper sx={{ py: 15, textAlign: 'center', bgcolor: alpha('#0f172a', 0.5), border: '1px dashed rgba(255,255,255,0.1)' }}>
            <BarChart2 size={56} color="slategray" style={{ opacity: 0.2, marginBottom: 16 }} />
            <Typography sx={{ color: 'slategray', fontWeight: 700 }}>You haven't saved any technical setups yet.</Typography>
            <Typography variant="caption" sx={{ color: 'slategray' }}>Open any signal to start marking up structural evidence.</Typography>
        </Paper>
      )}
    </Box>
  );
}
