import { useState } from 'react';
import { Box, Typography, Paper, Grid, Button, List, ListItem, ListItemSecondaryAction, IconButton, TextField, MenuItem, Select, FormControl } from '@mui/material';
import { Plus, Trash2, Save, Play, Code } from 'lucide-react';

export default function StrategyBuilder() {
  const [blocks, setBlocks] = useState<any[]>([]);
  const [name, setName] = useState('My New Strategy');

  const addBlock = () => {
    setBlocks([...blocks, { id: Date.now().toString(), type: 'INDICATOR', feature: 'momentum_rsi', op: 'lt', val: 30 }]);
  };

  const removeBlock = (id: string) => {
    setBlocks(blocks.filter(b => b.id !== id));
  };

  const updateBlock = (id: string, field: string, value: any) => {
    setBlocks(blocks.map(b => b.id === id ? { ...b, [field]: value } : b));
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" fontWeight="bold">AI Strategy Builder</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" startIcon={<Code size={18} />}>View Logic</Button>
          <Button variant="contained" startIcon={<Save size={18} />}>Save Strategy</Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 4, minHeight: 400 }}>
            <TextField
              fullWidth
              label="Strategy Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              variant="standard"
              sx={{ mb: 4, '& .MuiInput-input': { fontSize: '1.5rem', fontWeight: 'bold' } }}
            />

            <Typography variant="h6" gutterBottom>Condition Logic</Typography>
            <List>
              {blocks.map((block, index) => (
                <ListItem key={block.id} sx={{ bgcolor: 'rgba(255,255,255,0.03)', mb: 1, borderRadius: 2 }}>
                  <Typography sx={{ mr: 2, color: 'primary.main', fontWeight: 'bold' }}>{index === 0 ? 'IF' : 'AND'}</Typography>
                  <FormControl size="small" sx={{ minWidth: 200, mr: 2 }}>
                    <Select value={block.feature} onChange={(e) => updateBlock(block.id, 'feature', e.target.value)}>
                      <MenuItem value="momentum_rsi">RSI (14)</MenuItem>
                      <MenuItem value="trend_ema_cross">EMA 20/50 Cross</MenuItem>
                      <MenuItem value="volatility_bb">Bollinger %B</MenuItem>
                      <MenuItem value="smc_bullish_ob">Bullish Order Block</MenuItem>
                    </Select>
                  </FormControl>
                  <FormControl size="small" sx={{ minWidth: 100, mr: 2 }}>
                    <Select value={block.op} onChange={(e) => updateBlock(block.id, 'op', e.target.value)}>
                      <MenuItem value="lt">is less than</MenuItem>
                      <MenuItem value="gt">is greater than</MenuItem>
                      <MenuItem value="eq">is equal to</MenuItem>
                    </Select>
                  </FormControl>
                  <TextField
                    size="small"
                    type="number"
                    value={block.val}
                    onChange={(e) => updateBlock(block.id, 'val', e.target.value)}
                    sx={{ width: 100 }}
                  />
                  <ListItemSecondaryAction>
                    <IconButton edge="end" onClick={() => removeBlock(block.id)} color="error">
                      <Trash2 size={18} />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
            <Button
              fullWidth
              onClick={addBlock}
              sx={{ border: '2px dashed #334155', py: 2, mt: 2, color: 'text.secondary' }}
              startIcon={<Plus size={18} />}
            >
              Add Condition Block
            </Button>

            <Box sx={{ mt: 6, p: 3, bgcolor: 'rgba(16, 185, 129, 0.05)', borderRadius: 2, border: '1px solid #10b981' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="subtitle1" fontWeight="bold">Action</Typography>
                  <Typography variant="body2" color="textSecondary">Execute institutional order flow on signal</Typography>
                </Box>
                <Chip label="MARKET BUY" color="primary" />
              </Box>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Strategy Health</Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 4 }}>
              AI analysis of your current strategy logic based on 10Y historical data.
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Complexity</Typography>
                <Typography variant="body2" fontWeight="bold">LOW</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Historical Frequency</Typography>
                <Typography variant="body2" fontWeight="bold">~12/mo</Typography>
              </Box>
              <Button fullWidth variant="outlined" color="primary" startIcon={<Play size={18} />}>
                Run Quick Backtest
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

import { Chip } from '@mui/material';
