import { useState, useEffect } from 'react';
import { Box, Typography, Paper, TextField, Button, List, ListItem, Chip, Stack, IconButton, Divider, Grid, CircularProgress } from '@mui/material';
import { Save, Tag, Paperclip, MessageSquare, Search } from 'lucide-react';
import { getResearchNotes, saveResearchNote } from '../../api/client';

export default function ResearchNotebook({ symbol }: { symbol: string }) {
  const [note, setNote] = useState('');
  const [notes, setNotes] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getResearchNotes(symbol).then(data => {
      setNotes(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [symbol]);

  const handleSave = async () => {
    if (!note.trim()) return;
    try {
      const newNote = await saveResearchNote({ symbol, content: note, tags: ['USER'] });
      setNotes([newNote, ...notes]);
      setNote('');
    } catch (e) {
      alert("Failed to save note");
    }
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <MessageSquare size={20} className="text-emerald-500" /> AI Research Notebook: {symbol}
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>NEW RESEARCH NOTE</Typography>
            <TextField
              fullWidth
              multiline
              rows={6}
              placeholder="Record your findings, observations or institutional logic..."
              value={note}
              onChange={(e) => setNote(e.target.value)}
              variant="outlined"
              sx={{ mt: 1, bgcolor: 'rgba(255,255,255,0.02)' }}
            />
            <Stack direction="row" spacing={1} sx={{ mt: 2, justifyContent: 'space-between' }}>
               <Box sx={{ display: 'flex', gap: 1 }}>
                  <IconButton size="small" color="primary"><Tag size={18} /></IconButton>
                  <IconButton size="small" color="primary"><Paperclip size={18} /></IconButton>
               </Box>
               <Button variant="contained" startIcon={<Save size={18} />} onClick={handleSave}>Save Note</Button>
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} md={7}>
           <Paper sx={{ p: 0, height: '100%', overflow: 'hidden', position: 'relative' }}>
              <Box sx={{ p: 2, borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                 <Typography variant="subtitle2" fontWeight="bold">RESEARCH TIMELINE</Typography>
              </Box>
              {loading && <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress size={24} /></Box>}
              <List sx={{ maxHeight: 350, overflowY: 'auto' }}>
                 {notes.map((item) => (
                   <Box key={item.id}>
                     <ListItem sx={{ display: 'block', py: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                           <Typography variant="caption" color="textSecondary">{new Date(item.created_at).toLocaleDateString()}</Typography>
                           <Stack direction="row" spacing={0.5}>
                              {item.tags.map((t: string) => <Chip key={t} label={t} size="small" sx={{ height: 16, fontSize: '0.6rem' }} />)}
                           </Stack>
                        </Box>
                        <Typography variant="body2" sx={{ lineHeight: 1.6 }}>{item.content}</Typography>
                     </ListItem>
                     <Divider sx={{ opacity: 0.05 }} />
                   </Box>
                 ))}
                 {!loading && notes.length === 0 && (
                    <Box sx={{ p: 4, textAlign: 'center' }}><Typography color="textSecondary" variant="caption">No notes found for this symbol.</Typography></Box>
                 )}
              </List>
           </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
