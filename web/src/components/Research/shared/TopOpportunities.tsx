import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Chip, Button, Divider, CircularProgress } from '@mui/material';
import { Target, ChevronRight, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getOpportunities } from '../../../api/client';

export default function TopOpportunities() {
  const navigate = useNavigate();
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchOpps = () => {
    setLoading(true);
    getOpportunities()
      .then(setOpportunities)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchOpps();
  }, []);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress size={24} /></Box>;

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" fontWeight="bold" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Target size={20} className="text-emerald-500" /> Top Opportunities
        </Typography>
        <Button
          size="small"
          startIcon={<RefreshCw size={14} />}
          onClick={fetchOpps}
          sx={{ fontSize: '0.65rem', fontWeight: 800 }}
        >
          FORCE SCAN
        </Button>
      </Box>

      <Grid container spacing={3}>
         {opportunities.length > 0 ? opportunities.map((opp) => (
           <Grid item xs={12} md={4} key={opp.id}>
              <Paper sx={{ p: 3, height: '100%', border: '1px solid #334155', '&:hover': { borderColor: '#10b981' }, cursor: 'pointer', transition: 'all 0.2s', position: 'relative' }}>
                 {opp.indicators?.includes('AI SCANNING...') && (
                   <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, bgcolor: 'primary.main', opacity: 0.5 }} />
                 )}
                 <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" fontWeight="bold">{opp.symbol}</Typography>
                    <Chip
                      label={`${opp.conviction_score}% ${opp.indicators?.includes('AI SCANNING...') ? 'RAW' : 'AI'}`}
                      color={opp.indicators?.includes('AI SCANNING...') ? 'default' : 'primary'}
                      size="small"
                      sx={{ fontWeight: 800, fontSize: '0.6rem' }}
                    />
                 </Box>
                 <Chip label={opp.type} size="small" variant="outlined" sx={{ mb: 2, fontSize: '0.65rem', fontWeight: 800 }} />
                 <Typography variant="body2" color="textSecondary" sx={{ lineHeight: 1.6, height: 60, overflow: 'hidden' }}>
                    {opp.ai_thesis}
                 </Typography>
                 <Divider sx={{ my: 2, opacity: 0.1 }} />
                 <Button
                    fullWidth
                    variant="text"
                    size="small"
                    endIcon={<ChevronRight size={14} />}
                    onClick={() => navigate('/analysis', { state: { symbol: opp.symbol } })}
                    sx={{ justifyContent: 'space-between', fontWeight: 800 }}
                 >
                    Forensic Lab
                 </Button>
              </Paper>
           </Grid>
         )) : (
            <Grid item xs={12}>
               <Paper sx={{ p: 4, textAlign: 'center', border: '1px dashed #334155' }}>
                  <Typography color="textSecondary" sx={{ mb: 2 }}>The AI is currently scanning the Nifty 100 for high-conviction opportunities.</Typography>
                  <Button variant="outlined" size="small" onClick={() => navigate('/analysis')}>Start Manual Research</Button>
               </Paper>
            </Grid>
         )}
      </Grid>
    </Box>
  );
}
