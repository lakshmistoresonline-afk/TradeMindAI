import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Chip, List, ListItem, Divider, CircularProgress, Stack } from '@mui/material';
import { Book, Lightbulb } from 'lucide-react';
import { getTradeJournal } from '../api/client';

export default function Journal() {
  const [journal, setJournal] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTradeJournal()
      .then(setJournal)
      .finally(() => setLoading(false));
  }, []);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 900 }}>AI Trade Journal</Typography>
        <Chip label="Continuous Learning Mode" color="secondary" variant="outlined" sx={{ fontWeight: 800 }} />
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 0, overflow: 'hidden', border: '1px solid #1e293b' }}>
            {loading ? (
              <Box sx={{ p: 4, textAlign: 'center' }}><CircularProgress /></Box>
            ) : (
              <List>
                {journal.length > 0 ? journal.map((entry, i) => (
                  <Box key={i}>
                    <ListItem sx={{ display: 'block', p: 4 }}>
                       <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                             <Typography variant="h5" fontWeight={900}>{entry.symbol}</Typography>
                             <Chip
                                label={entry.pnl >= 0 ? 'PROFIT' : 'LOSS'}
                                color={entry.pnl >= 0 ? 'primary' : 'error'}
                                size="small"
                                sx={{ fontWeight: 800, borderRadius: 1 }}
                             />
                             <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>
                                {entry.exit_date ? new Date(entry.exit_date).toLocaleDateString(undefined, { dateStyle: 'medium' }) : '---'}
                             </Typography>
                          </Box>
                          <Typography variant="h5" color={entry.pnl >= 0 ? 'primary.main' : 'error.main'} sx={{ fontFamily: 'JetBrains Mono', fontWeight: 900 }}>
                             {entry.pnl >= 0 ? '+' : ''}₹{entry.pnl.toLocaleString()}
                          </Typography>
                       </Box>

                       <Box sx={{ p: 2.5, bgcolor: 'rgba(16, 185, 129, 0.05)', borderRadius: 2, mb: 3, borderLeft: '4px solid #10b981' }}>
                          <Typography variant="subtitle2" color="primary" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                             <Book size={16} /> AI COACH FEEDBACK
                          </Typography>
                          <Typography variant="body2" sx={{ lineHeight: 1.7, color: 'text.secondary', fontWeight: 500 }}>{entry.feedback}</Typography>
                       </Box>

                       <Grid container spacing={4}>
                          <Grid item xs={12} sm={6}>
                             <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 1.5 }}>TRADING MISTAKES</Typography>
                             <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                               {entry.mistakes && entry.mistakes.length > 0 ? entry.mistakes.map((m: any) => (
                                 <Chip key={m} label={m} size="small" color="error" variant="outlined" sx={{ fontWeight: 700, fontSize: '0.65rem' }} />
                               )) : <Typography variant="body2" color="primary" sx={{ fontWeight: 700 }}>NONE DETECTED</Typography>}
                             </Stack>
                          </Grid>
                          <Grid item xs={12} sm={6}>
                             <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 1.5 }}>AI LESSONS</Typography>
                             {entry.lessons && entry.lessons.map((l: any) => (
                               <Typography key={l} variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5, fontWeight: 600 }}>
                                  <Lightbulb size={14} className="text-amber-500" /> {l}
                               </Typography>
                             ))}
                          </Grid>
                       </Grid>
                    </ListItem>
                    {i < journal.length - 1 && <Divider sx={{ opacity: 0.05 }} />}
                  </Box>
                )) : (
                  <Box sx={{ p: 8, textAlign: 'center', opacity: 0.3 }}>
                     <Book size={64} />
                     <Typography variant="h6" sx={{ mt: 2 }}>Journal Empty</Typography>
                     <Typography variant="body2">Record your trades to activate the AI Coach.</Typography>
                  </Box>
                )}
              </List>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
           <Paper sx={{ p: 3, mb: 3, border: '1px solid #1e293b' }}>
              <Typography variant="subtitle2" color="textSecondary" sx={{ mb: 3 }}>LEARNING ANALYTICS</Typography>
              <Stack spacing={2.5}>
                 <StatRow label="Accuracy following AI" value="85%" color="primary.main" />
                 <StatRow label="Impatience Score" value="LOW" color="success.main" />
                 <StatRow label="Risk Management" value="EXCELLENT" color="primary.main" />
              </Stack>
           </Paper>
           <Paper sx={{ p: 3, bgcolor: 'rgba(255, 171, 0, 0.05)', border: '1px solid #FFAB00' }}>
              <Typography variant="subtitle2" color="#FFAB00" sx={{ mb: 1.5 }}>COACH'S INSIGHT</Typography>
              <Typography variant="body2" sx={{ lineHeight: 1.6, fontWeight: 500 }}>
                Your performance peaks during high-volume institutional windows (10:30 - 11:30 AM).
                Try to restrict entries to these high-probability periods.
              </Typography>
           </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function StatRow({ label, value, color }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
       <Typography variant="body2" color="textSecondary" sx={{ fontWeight: 600 }}>{label}</Typography>
       <Typography variant="body2" sx={{ fontWeight: 900, color: color || 'text.primary' }}>{value}</Typography>
    </Box>
  );
}
