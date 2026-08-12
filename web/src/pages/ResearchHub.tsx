import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, List, ListItemText, Chip, Button, TextField, InputAdornment, Stack, Divider, ListItemButton } from '@mui/material';
import { Search, FileText, BookOpen } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ResearchHub() {
  const navigate = useNavigate();
  const [notes, setNotes] = useState<any[]>([]);
  const [filterTag, setFilterTag] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
     // Fetch from backend
     import('../api/client').then(c => c.getTradeJournal().then(() => {
        // Map trades or other logic to show notes
        const initialNotes = [
          { symbol: 'RELIANCE', content: 'Bullish SMC breakout confirmed on daily.', tags: ['SMC', 'BULLISH'], date: 'Aug 04', category: 'Market Structure Analysis' },
          { symbol: 'TCS', content: 'PE 32x is slightly high, wait for correction to 3800.', tags: ['FUNDAMENTAL'], date: 'Jul 28', category: 'Fundamental Audits' },
          { symbol: 'INFY', content: 'Institutional accumulation detected in last quarter.', tags: ['INSTITUTIONAL'], date: 'Jul 25', category: 'Institutional Flow Reports' },
          { symbol: 'HDFCBANK', content: 'Volatility expansion expected following bank results.', tags: ['TECHNICAL'], date: 'Aug 10', category: 'Quant Performance Reports' },
        ];
        setNotes(initialNotes.map(n => ({...n, isSample: true})));
     }));
  }, []);

  const filteredNotes = notes.filter(n => {
     const matchesTag = !filterTag || n.tags.includes(filterTag) || n.category === filterTag;
     const matchesSearch = n.symbol.toLowerCase().includes(search.toLowerCase()) || n.content.toLowerCase().includes(search.toLowerCase());
     return matchesTag && matchesSearch;
  });

  const tags = ['SMC', 'FUNDAMENTAL', 'TECHNICAL', 'INSTITUTIONAL'];
  const categories = [
    'Market Structure Analysis',
    'Fundamental Audits',
    'Quant Performance Reports',
    'Institutional Flow Reports'
  ];

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
               {tags.map(tag => (
                 <Chip
                   key={tag}
                   label={tag}
                   clickable
                   variant={filterTag === tag ? "filled" : "outlined"}
                   color={filterTag === tag ? "primary" : "default"}
                   onClick={() => setFilterTag(filterTag === tag ? null : tag)}
                   sx={{ fontWeight: 800 }}
                 />
               ))}
            </Stack>
          </Paper>

          <Paper sx={{ p: 3 }}>
             <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ fontWeight: 800 }}>RESEARCH CATEGORIES</Typography>
             <List dense>
                {categories.map(cat => (
                  <ListItemButton
                    key={cat}
                    selected={filterTag === cat}
                    onClick={() => setFilterTag(filterTag === cat ? null : cat)}
                    sx={{ borderRadius: 1 }}
                  >
                    <ListItemText primary={cat} primaryTypographyProps={{ fontWeight: 600, fontSize: '0.85rem' }} />
                  </ListItemButton>
                ))}
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
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  InputProps={{ startAdornment: <InputAdornment position="start"><Search size={16} /></InputAdornment> }}
                 />
              </Box>
              <List>
                 {filteredNotes.length > 0 ? filteredNotes.map((n, i) => (
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
                 )) : (
                   <Box sx={{ p: 10, textAlign: 'center', opacity: 0.5 }}>
                      <BookOpen size={48} style={{ margin: '0 auto 16px' }} />
                      <Typography variant="h6">No research matches your filters</Typography>
                   </Box>
                 )}
              </List>
           </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
