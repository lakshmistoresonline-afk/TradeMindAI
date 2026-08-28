import { useState } from 'react';
import { Box, Typography, Paper, Grid, Button, List, ListItem, ListItemSecondaryAction, IconButton, TextField, MenuItem, Select, FormControl, Divider, Chip, Tabs, Tab } from '@mui/material';
import { Plus, Trash2, Save, Play, Code, Zap, BarChart2, Settings, Rocket } from 'lucide-react';

export default function StrategyBuilder() {
  const [activeTab, setActiveTab] = useState(0);
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
        <Typography variant="h4" sx={{ fontWeight: 900 }}>Strategy Builder</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" startIcon={<Code size={18} />}>View JSON</Button>
          <Button variant="contained" startIcon={<Save size={18} />}>Save Strategy</Button>
        </Box>
      </Box>

      <Box sx={{ mb: 4, borderBottom: '1px solid #1e293b' }}>
         <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} textColor="primary" indicatorColor="primary">
            <Tab icon={<Settings size={18} />} iconPosition="start" label="BUILD" sx={{ fontWeight: 700 }} />
            <Tab icon={<BarChart2 size={18} />} iconPosition="start" label="BACKTEST" sx={{ fontWeight: 700 }} />
            <Tab icon={<Zap size={18} />} iconPosition="start" label="OPTIMIZE" sx={{ fontWeight: 700 }} />
            <Tab icon={<Rocket size={18} />} iconPosition="start" label="DEPLOY" sx={{ fontWeight: 700 }} />
         </Tabs>
      </Box>

      {activeTab === 0 && (
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

              <Typography variant="h6" fontWeight={800} gutterBottom>Condition Logic</Typography>
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
                sx={{ border: '2px dashed #334155', py: 2, mt: 2, color: 'text.secondary', fontWeight: 800 }}
                startIcon={<Plus size={18} />}
              >
                Add Condition Block
              </Button>

              <Box sx={{ mt: 6, p: 3, bgcolor: 'rgba(16, 185, 129, 0.05)', borderRadius: 2, border: '1px solid #10b981' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="subtitle1" fontWeight={800}>Action</Typography>
                    <Typography variant="body2" color="textSecondary">Execute institutional order flow on signal</Typography>
                  </Box>
                  <Chip label="MARKET BUY" color="primary" sx={{ fontWeight: 800 }} />
                </Box>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight={800} gutterBottom>Strategy Health</Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 4 }}>
                AI analysis of your current strategy logic based on historical market cycles.
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="textSecondary">Complexity</Typography>
                  <Typography variant="body2" fontWeight="bold">LOW</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2" color="textSecondary">Avg. Signals</Typography>
                  <Typography variant="body2" fontWeight="bold">~12/mo</Typography>
                </Box>
                <Button fullWidth variant="outlined" color="primary" startIcon={<Play size={18} />} sx={{ mt: 2, fontWeight: 800 }}>
                  Initialize Quick Backtest
                </Button>
              </Box>

              <Divider sx={{ my: 4, opacity: 0.1 }} />

              <Box sx={{ p: 2, bgcolor: 'rgba(41, 121, 255, 0.05)', border: '1px solid #2979FF', borderRadius: 2 }}>
                 <Typography variant="subtitle2" color="#2979FF" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1, fontWeight: 900 }}>
                    <Zap size={16} /> AI STRATEGY OPTIMIZER
                 </Typography>
                 <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                    AI can suggest optimized parameters for your rules to maximize Sharpe Ratio.
                 </Typography>
                 <Button fullWidth variant="contained" sx={{ bgcolor: '#2979FF', color: 'white', fontWeight: 800 }}>
                    Optimize Logic
                 </Button>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      )}

      {activeTab !== 0 && (
        <Paper sx={{ p: 8, textAlign: 'center', bgcolor: 'rgba(15, 23, 42, 0.3)', border: '1px dashed #334155' }}>
           <Typography variant="h6" color="textSecondary">Advanced Module Syncing...</Typography>
           <Typography variant="body2" color="textSecondary">This feature requires active connection to the TradeMind AI Cluster.</Typography>
        </Paper>
      )}
    </Box>
  );
}
