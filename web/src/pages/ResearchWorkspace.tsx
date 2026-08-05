import { useState } from 'react';
import { Box, Typography, Paper, Grid, List, ListItem, ListItemText, Chip, Button, TextField, InputAdornment, Stack, Divider } from '@mui/material';
import { Search, FileText } from 'lucide-react';

export default function ResearchWorkspace() {
  const [notes] = useState<any[]>([
    { symbol: 'RELIANCE', content: 'Bullish SMC breakout confirmed on daily.', tags: ['SMC', 'BULLISH'], date: 'Aug 04' },
    { symbol: 'TCS', content: 'PE 32x is slightly high, wait for correction to 3800.', tags: ['FUNDAMENTAL'], date: 'Jul 28' },
    { symbol: 'INFY', content: 'Institutional accumulation detected in last quarter.', tags: ['INSTITUTIONAL'], date: 'Jul 25' },
  ]);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
         <Typography variant="h4" sx={{ fontWeight: 'bold' }}>AI Research Workspace</Typography>
         <Button variant="contained" startIcon={<FileText size={18} />}>Export All Notes</Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>FILTER BY TAG</Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mt: 2 }}>
               <Chip label="SMC" clickable variant="filled" color="primary" />
               <Chip label="FUNDAMENTAL" clickable variant="outlined" />
               <Chip label="TECHNICAL" clickable variant="outlined" />
               <Chip label="INSTITUTIONAL" clickable variant="outlined" />
            </Stack>
          </Paper>

          <Paper sx={{ p: 3 }}>
             <Typography variant="subtitle2" color="textSecondary" gutterBottom>RECENT REPORTS</Typography>
             <List dense>
                <ListItem><ListItemText primary="Nifty 100 Mid-Year Audit" /></ListItem>
                <ListItem><ListItemText primary="IT Sector Outlook Q3" /></ListItem>
                <ListItem><ListItemText primary="Banking Liquidity Report" /></ListItem>
             </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={9}>
           <Paper sx={{ p: 0, overflow: 'hidden' }}>
              <Box sx={{ p: 2, borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                 <Typography variant="h6" fontWeight="bold">Centralized Research Feed</Typography>
                 <TextField
                  size="small"
                  placeholder="Search research..."
                  InputProps={{ startAdornment: <InputAdornment position="start"><Search size={16} /></InputAdornment> }}
                 />
              </Box>
              <List>
                 {notes.map((n, i) => (
                   <Box key={i}>
                     <ListItem sx={{ display: 'block', p: 3 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                           <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Typography variant="subtitle1" fontWeight="bold" color="primary">{n.symbol}</Typography>
                              <Typography variant="caption" color="textSecondary">{n.date}</Typography>
                           </Box>
                           <Stack direction="row" spacing={1}>
                              {n.tags.map((t: string) => <Chip key={t} label={t} size="small" sx={{ height: 18, fontSize: '0.6rem' }} />)}
                           </Stack>
                        </Box>
                        <Typography variant="body2" sx={{ lineHeight: 1.6 }}>{n.content}</Typography>
                     </ListItem>
                     <Divider sx={{ opacity: 0.05 }} />
                   </Box>
                 ))}
              </List>
           </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
