import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Chip, List, ListItem, Divider, CircularProgress } from '@mui/material';
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
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>AI Trade Coach & Journal</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 0, overflow: 'hidden' }}>
            {loading ? (
              <Box sx={{ p: 4, textAlign: 'center' }}><CircularProgress /></Box>
            ) : (
              <List>
                {journal.length > 0 ? journal.map((entry, i) => (
                  <Box key={i}>
                    <ListItem sx={{ display: 'block', p: 4 }}>
                       <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                             <Typography variant="h6" fontWeight="bold">{entry.symbol}</Typography>
                             <Chip label={entry.pnl >= 0 ? 'PROFIT' : 'LOSS'} color={entry.pnl >= 0 ? 'success' : 'error'} size="small" />
                          </Box>
                          <Typography variant="h6" color={entry.pnl >= 0 ? 'primary' : 'error'} fontWeight="bold">
                             {entry.pnl >= 0 ? '+' : ''}₹{entry.pnl.toLocaleString()}
                          </Typography>
                       </Box>

                       <Box sx={{ p: 2, bgcolor: 'rgba(16, 185, 129, 0.05)', borderRadius: 2, mb: 2, borderLeft: '4px solid #10b981' }}>
                          <Typography variant="subtitle2" color="primary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                             <Book size={16} /> AI COACH FEEDBACK
                          </Typography>
                          <Typography variant="body2" sx={{ lineHeight: 1.6 }}>{entry.feedback}</Typography>
                       </Box>

                       <Grid container spacing={2}>
                          <Grid item xs={6}>
                             <Typography variant="caption" color="textSecondary" gutterBottom display="block">MISTAKES</Typography>
                             {entry.mistakes && entry.mistakes.length > 0 ? entry.mistakes.map((m: any) => (
                               <Chip key={m} label={m} size="small" variant="outlined" color="error" sx={{ mr: 1, fontSize: '0.6rem' }} />
                             )) : <Typography variant="body2" color="primary">NONE</Typography>}
                          </Grid>
                          <Grid item xs={6}>
                             <Typography variant="caption" color="textSecondary" gutterBottom display="block">LESSONS LEARNED</Typography>
                             {entry.lessons && entry.lessons.map((l: any) => (
                               <Typography key={l} variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                  <Lightbulb size={12} className="text-amber-500" /> {l}
                               </Typography>
                             ))}
                          </Grid>
                       </Grid>
                    </ListItem>
                    <Divider />
                  </Box>
                )) : (
                  <Box sx={{ p: 4, textAlign: 'center' }}>
                     <Typography color="textSecondary">No journal entries found. Add your executed trades to get AI feedback.</Typography>
                  </Box>
                )}
              </List>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
           <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>Learning Statistics</Typography>
              <Box sx={{ mt: 3 }}>
                 <StatRow label="Accuracy following AI" value="85%" />
                 <StatRow label="Impatience Score" value="Low" />
                 <StatRow label="Risk Management" value="Good" />
              </Box>
           </Paper>
           <Paper sx={{ p: 3, bgcolor: 'rgba(255, 171, 0, 0.05)', border: '1px solid #FFAB00' }}>
              <Typography variant="subtitle2" color="#FFAB00" gutterBottom>COACH TIP</Typography>
              <Typography variant="body2">Your best trades happen between 10:30 and 11:30 AM when institutional volume is highest. Try to avoid opening positions before 10 AM.</Typography>
           </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function StatRow({ label, value }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
       <Typography variant="body2" color="textSecondary">{label}</Typography>
       <Typography variant="body2" fontWeight="bold">{value}</Typography>
    </Box>
  );
}
