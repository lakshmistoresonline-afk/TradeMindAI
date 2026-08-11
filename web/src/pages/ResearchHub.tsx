import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, List, ListItemText, Chip, Button, TextField, InputAdornment, Stack, Divider, ListItemButton } from '@mui/material';
import { Search, FileText, BookOpen } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ResearchHub() {
  const navigate = useNavigate();
  const [notes, setNotes] = useState<any[]>([]);

  useEffect(() => {
     // Fetch from backend
     import('../api/client').then(c => c.getTradeJournal().then(() => {
        // Map trades or other logic to show notes
        setNotes([
          { symbol: 'RELIANCE', content: 'Bullish SMC breakout confirmed on daily.', tags: ['SMC', 'BULLISH'], date: 'Aug 04' },
          { symbol: 'TCS', content: 'PE 32x is slightly high, wait for correction to 3800.', tags: ['FUNDAMENTAL'], date: 'Jul 28' },
          { symbol: 'INFY', content: 'Institutional accumulation detected in last quarter.', tags: ['INSTITUTIONAL'], date: 'Jul 25' },
        ].map(n => ({...n, isSample: true})));
     }));
  }, []);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
         <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <BookOpen size={32} className="text-emerald-500" />
            <Typography variant="h4" sx={{ fontWeight: 900 }}>Research Hub</Typography>
         </Box>
         <Button variant="contained" startIcon={<FileText size={18} />}>Export Research</Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ fontWeight: 800 }}>FILTER BY TAG</Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mt: 2 }}>
               <Chip label="SMC" clickable variant="filled" color="primary" sx={{ fontWeight: 800 }} />
               <Chip label="FUNDAMENTAL" clickable variant="outlined" sx={{ fontWeight: 800 }} />
               <Chip label="TECHNICAL" clickable variant="outlined" sx={{ fontWeight: 800 }} />
               <Chip label="INSTITUTIONAL" clickable variant="outlined" sx={{ fontWeight: 800 }} />
            </Stack>
          </Paper>

          <Paper sx={{ p: 3 }}>
             <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ fontWeight: 800 }}>RESEARCH CATEGORIES</Typography>
             <List dense>
                <ListItemButton sx={{ borderRadius: 1 }}><ListItemText primary="Market Structure Analysis" primaryTypographyProps={{ fontWeight: 600, fontSize: '0.85rem' }} /></ListItemButton>
                <ListItemButton sx={{ borderRadius: 1 }}><ListItemText primary="Fundamental Audits" primaryTypographyProps={{ fontWeight: 600, fontSize: '0.85rem' }} /></ListItemButton>
                <ListItemButton sx={{ borderRadius: 1 }}><ListItemText primary="Quant Performance Reports" primaryTypographyProps={{ fontWeight: 600, fontSize: '0.85rem' }} /></ListItemButton>
                <ListItemButton sx={{ borderRadius: 1 }}><ListItemText primary="Institutional Flow Reports" primaryTypographyProps={{ fontWeight: 600, fontSize: '0.85rem' }} /></ListItemButton>
             </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={9}>
           <Paper sx={{ p: 0, overflow: 'hidden' }}>
              <Box sx={{ p: 2, borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                 <Typography variant="h6" fontWeight={800}>Centralized Research Feed</Typography>
                 <TextField
                  size="small"
                  placeholder="Search hub..."
                  InputProps={{ startAdornment: <InputAdornment position="start"><Search size={16} /></InputAdornment> }}
                 />
              </Box>
              <List>
                 {notes.map((n, i) => (
                   <Box key={i}>
                     <ListItemButton sx={{ display: 'block', p: 3 }} onClick={() => navigate('/analysis', { state: { symbol: n.symbol } })}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
                           <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                              <Typography variant="h6" fontWeight={900} color="primary">{n.symbol}</Typography>
                              <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>{n.date}</Typography>
                              {n.isSample && <Chip label="SAMPLE" size="small" variant="outlined" sx={{ height: 16, fontSize: '0.5rem', opacity: 0.6 }} />}
                           </Box>
                           <Stack direction="row" spacing={1}>
                              {n.tags.map((t: string) => <Chip key={t} label={t} size="small" sx={{ height: 18, fontSize: '0.6rem', fontWeight: 800 }} />)}
                           </Stack>
                        </Box>
                        <Typography variant="body2" sx={{ lineHeight: 1.6, color: 'text.secondary', fontWeight: 500 }}>{n.content}</Typography>
                        <Typography variant="caption" color="primary" sx={{ mt: 2, display: 'block', fontWeight: 800 }}>OPEN STOCK INTELLIGENCE →</Typography>
                     </ListItemButton>
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
