import { Box, Typography, Paper, Grid, Chip, List, ListItem, Divider } from '@mui/material';
import { Book, Lightbulb } from 'lucide-react';

const mockJournal = [
  {
    symbol: 'TATASTEEL',
    pnl: 1240.50,
    status: 'PROFIT',
    feedback: 'Excellent execution. You followed the SMC breakout rule perfectly and exited before the sector resistance.',
    mistakes: [],
    lessons: ['Keep trailing stop loss on sector resistance.'],
    date: 'Aug 01'
  },
  {
    symbol: 'WIPRO',
    pnl: -450.20,
    status: 'LOSS',
    feedback: 'Premature entry. You entered before the EMA cross was confirmed. Be patient for confirmation.',
    mistakes: ['Entry without confirmation'],
    lessons: ['Wait for 15-min candle close for confirmation.'],
    date: 'Jul 28'
  }
];

export default function Journal() {
  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>AI Trade Coach & Journal</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 0, overflow: 'hidden' }}>
            <List>
               {mockJournal.map((entry, i) => (
                 <Box key={i}>
                   <ListItem sx={{ display: 'block', p: 4 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                         <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Typography variant="h6" fontWeight="bold">{entry.symbol}</Typography>
                            <Chip label={entry.status} color={entry.status === 'PROFIT' ? 'success' : 'error'} size="small" />
                         </Box>
                         <Typography variant="h6" color={entry.pnl >= 0 ? 'primary' : 'error'} fontWeight="bold">
                            {entry.pnl >= 0 ? '+' : ''}₹{entry.pnl}
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
                            {entry.mistakes.length > 0 ? entry.mistakes.map(m => (
                              <Chip key={m} label={m} size="small" variant="outlined" color="error" sx={{ mr: 1, fontSize: '0.6rem' }} />
                            )) : <Typography variant="body2" color="primary">NONE</Typography>}
                         </Grid>
                         <Grid item xs={6}>
                            <Typography variant="caption" color="textSecondary" gutterBottom display="block">LESSONS LEARNED</Typography>
                            {entry.lessons.map(l => (
                              <Typography key={l} variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                 <Lightbulb size={12} className="text-amber-500" /> {l}
                              </Typography>
                            ))}
                         </Grid>
                      </Grid>
                   </ListItem>
                   <Divider />
                 </Box>
               ))}
            </List>
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
