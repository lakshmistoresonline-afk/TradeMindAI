import { useState, useEffect } from 'react';
import { Box, Modal, TextField, List, ListItem, ListItemText, ListItemIcon, Typography, Paper, InputAdornment } from '@mui/material';
import { Search, Zap, Command, PieChart, Briefcase } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getStocks } from '../api/client';

export default function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [stocks, setStocks] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    if (open) getStocks().then(setStocks);
  }, [open]);

  useEffect(() => {
    if (!query) {
       setResults([
         { title: 'Market Overview', path: '/', icon: <Zap size={18} /> },
         { title: 'Sector Rotation', path: '/sectors', icon: <PieChart size={18} /> },
         { title: 'My Portfolio', path: '/portfolio', icon: <Briefcase size={18} /> },
       ]);
       return;
    }
    const filtered = stocks.filter(s => s.symbol.toLowerCase().includes(query.toLowerCase()) || s.name?.toLowerCase().includes(query.toLowerCase()));
    setResults(filtered.map(s => ({ title: `${s.symbol} - ${s.name}`, path: '/analysis', state: { symbol: s.symbol }, icon: <Search size={18} /> })));
  }, [query, stocks]);

  const handleSelect = (item: any) => {
    navigate(item.path, { state: item.state });
    setOpen(false);
    setQuery('');
  };

  return (
    <Modal open={open} onClose={() => setOpen(false)} sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'center', pt: '15vh' }}>
      <Paper sx={{ width: 600, bgcolor: '#0f172a', border: '1px solid #334155', borderRadius: 4, overflow: 'hidden', boxShadow: '0 20px 50px rgba(0,0,0,0.5)' }}>
        <TextField
          autoFocus
          fullWidth
          placeholder="Search stocks, pages, or commands... (Ctrl + K)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          variant="standard"
          InputProps={{
            startAdornment: <InputAdornment position="start" sx={{ pl: 2 }}><Search size={20} className="text-emerald-500" /></InputAdornment>,
            disableUnderline: true,
            sx: { height: 60, fontSize: '1.2rem', px: 2 }
          }}
        />
        <Box sx={{ p: 1, borderTop: '1px solid #334155', maxHeight: 400, overflowY: 'auto' }}>
           <List>
              {results.map((item, idx) => (
                <ListItem key={idx} onClick={() => handleSelect(item)} sx={{ borderRadius: 2, cursor: 'pointer', '&:hover': { bgcolor: 'rgba(255,255,255,0.05)' } }}>
                   <ListItemIcon sx={{ minWidth: 40, color: 'slategray' }}>{item.icon}</ListItemIcon>
                   <ListItemText primary={item.title} />
                   <Command size={14} className="opacity-20" />
                </ListItem>
              ))}
           </List>
        </Box>
        <Box sx={{ p: 1.5, bgcolor: '#020617', display: 'flex', justifyContent: 'space-between', opacity: 0.5 }}>
           <Typography variant="caption">↑↓ to navigate</Typography>
           <Typography variant="caption">Enter to select</Typography>
           <Typography variant="caption">Esc to close</Typography>
        </Box>
      </Paper>
    </Modal>
  );
}
