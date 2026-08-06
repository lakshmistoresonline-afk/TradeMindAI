import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Chip, Button, Divider, CircularProgress } from '@mui/material';
import { Target, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getOpportunities } from '../../api/client';

export default function OpportunityEngine() {
  const navigate = useNavigate();
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getOpportunities()
      .then(setOpportunities)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress size={24} /></Box>;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Target size={20} className="text-emerald-500" /> AI Opportunity Engine
      </Typography>

      <Grid container spacing={3}>
         {opportunities.length > 0 ? opportunities.map((opp) => (
           <Grid item xs={12} md={4} key={opp.symbol}>
              <Paper sx={{ p: 3, height: '100%', border: '1px solid #334155', '&:hover': { borderColor: '#10b981' }, cursor: 'pointer', transition: 'all 0.2s' }}>
                 <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" fontWeight="bold">{opp.symbol}</Typography>
                    <Chip label={`${opp.conviction_score}% AI`} color="primary" size="small" />
                 </Box>
                 <Chip label={opp.type} size="small" variant="outlined" sx={{ mb: 2, fontSize: '0.65rem' }} />
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
                    sx={{ justifyContent: 'space-between' }}
                 >
                    View Research
                 </Button>
              </Paper>
           </Grid>
         )) : (
            <Grid item xs={12}>
               <Paper sx={{ p: 4, textAlign: 'center' }}>
                  <Typography color="textSecondary">The AI is currently scanning the Nifty 100 for high-conviction opportunities. Check back shortly.</Typography>
               </Paper>
            </Grid>
         )}
      </Grid>
    </Box>
  );
}
