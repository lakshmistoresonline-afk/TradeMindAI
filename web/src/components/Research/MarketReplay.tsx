import { useState } from 'react';
import { Box, Typography, Paper, Grid, Slider, Button, Stack, Chip } from '@mui/material';
import { Play, Pause, FastForward, Rewind, Clock } from 'lucide-react';

export default function MarketReplay() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [frame, setFrame] = useState(0);

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Clock size={20} className="text-blue-400" /> AI Market Replay
      </Typography>

      <Paper sx={{ p: 4 }}>
         <Typography variant="body2" color="textSecondary" align="center" gutterBottom>
            Replay historical price action and see AI predictions evolve in real-time.
         </Typography>

         <Box sx={{ my: 4, height: 200, bgcolor: 'rgba(15, 23, 42, 0.5)', border: '1px solid #334155', borderRadius: 2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography variant="h6" color="textSecondary opacity-30">PRICE ACTION VISUALIZATION REPLAY</Typography>
         </Box>

         <Stack spacing={2} sx={{ maxWidth: 600, mx: 'auto' }}>
            <Slider value={frame} onChange={(_, v) => setFrame(v as number)} min={0} max={100} />
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4, alignItems: 'center' }}>
               <IconButton><Rewind size={24} /></IconButton>
               <IconButton onClick={() => setIsPlaying(!isPlaying)} sx={{ bgcolor: 'primary.main', color: 'black', '&:hover': { bgcolor: 'primary.dark' } }}>
                  {isPlaying ? <Pause size={24} /> : <Play size={24} />}
               </IconButton>
               <IconButton><FastForward size={24} /></IconButton>
            </Box>
         </Stack>

         <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Chip label="2008 Crash" variant="outlined" size="small" />
            <Chip label="2020 COVID Bottom" variant="outlined" size="small" />
            <Chip label="2024 Election Volatility" variant="outlined" size="small" />
         </Box>
      </Paper>
    </Box>
  );
}

import { IconButton } from '@mui/material';
