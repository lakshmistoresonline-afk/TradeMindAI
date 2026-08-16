import { useState, useEffect, useRef } from 'react';
import { Box, Typography, Paper, TextField, IconButton, List, ListItem, Avatar, Stack, Chip, CircularProgress, Button, Grid, Collapse } from '@mui/material';
import { Send, Bot, User, Sparkles, BrainCircuit, TrendingUp, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { chatWithAssistant } from '../api/client';

export default function AICopilot({ isDrawer = false, stockContext }: { isDrawer?: boolean, stockContext?: any }) {
  const [messages, setMessages] = useState<any[]>([
    { role: 'assistant', content: 'TRADEMIND AI Copilot active. How can I assist your institutional research today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showDebate, setShowDebate] = useState(false);
  const endRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => endRef.current?.scrollIntoView({ behavior: 'smooth' });
  useEffect(() => scrollToBottom(), [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const response = await chatWithAssistant(userMsg);
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'System Link Error: Unable to reach institutional agents. Please verify connectivity.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ height: isDrawer ? '100%' : 'calc(100vh - 140px)', display: 'flex', flexDirection: 'column', p: isDrawer ? 2 : 0 }}>
      {/* 1. Header & Controls */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
         {!isDrawer && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
               <Box sx={{ p: 1, bgcolor: 'primary.main', borderRadius: 1, color: 'black' }}>
                  <Bot size={24} />
               </Box>
               <Box>
                  <Typography variant="h5" sx={{ fontWeight: 800 }}>AI Copilot</Typography>
                  <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>LLAMA 3.1 INSTITUTIONAL ENGINE</Typography>
               </Box>
            </Box>
         )}

         <Stack direction="row" spacing={1} sx={{ ml: 'auto' }}>
            {stockContext?.analysis?.agent_debate && (
               <Button
                  size="small"
                  variant="outlined"
                  onClick={() => setShowDebate(!showDebate)}
                  startIcon={showDebate ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  sx={{ fontWeight: 900, fontSize: '0.6rem', height: 24, borderColor: showDebate ? 'primary.main' : 'rgba(255,255,255,0.1)' }}
               >
                  DEBATE
               </Button>
            )}
            <Chip icon={<Sparkles size={12} />} label="Context" size="small" variant="outlined" sx={{ fontWeight: 800, height: 24, fontSize: '0.6rem' }} />
            <Chip icon={<BrainCircuit size={12} />} label="Lead" size="small" variant="outlined" sx={{ fontWeight: 800, height: 24, fontSize: '0.6rem' }} />
         </Stack>
      </Box>

      {/* 2. Agent Debate Panel */}
      <Collapse in={showDebate}>
         <Box sx={{ mb: 2, p: 2, bgcolor: 'rgba(16, 185, 129, 0.02)', borderRadius: 1, border: '1px dashed #10b981' }}>
            <Typography variant="caption" color="primary" sx={{ fontWeight: 900, letterSpacing: 1, display: 'block', mb: 1.5 }}>Multi-Agent Reasoning Chain</Typography>
            <Grid container spacing={1}>
               {stockContext?.analysis?.agent_debate?.map((a: any, i: number) => (
                  <Grid item xs={12} key={i}>
                     <Box sx={{ p: 1, bgcolor: '#0f172a', borderRadius: 0.5, border: '1px solid #1e293b' }}>
                        <Typography variant="caption" sx={{ fontWeight: 900, color: 'primary.main', display: 'block' }}>{a.agent}</Typography>
                        <Typography variant="body2" sx={{ fontSize: '0.7rem', color: 'text.secondary', lineHeight: 1.4 }}>{a.summary}</Typography>
                     </Box>
                  </Grid>
               ))}
            </Grid>
         </Box>
      </Collapse>

      {/* 3. Messages Area */}
      <Paper sx={{
        flexGrow: 1,
        mb: 2,
        overflowY: 'auto',
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'rgba(15, 23, 42, 0.3)',
        border: '1px solid #1e293b'
      }}>
        <List sx={{ flexGrow: 1 }}>
          {messages.map((m, i) => (
            <ListItem key={i} sx={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start', mb: 2.5, px: 0 }}>
              <Stack direction="row" spacing={1.5} sx={{ maxWidth: '90%' }}>
                {m.role === 'assistant' && <Avatar sx={{ bgcolor: 'primary.main', width: 28, height: 28 }}><Bot size={16} color="black" /></Avatar>}
                <Box sx={{
                  p: 1.5,
                  borderRadius: 2,
                  bgcolor: m.role === 'user' ? 'primary.main' : 'rgba(255,255,255,0.05)',
                  color: m.role === 'user' ? 'black' : 'white',
                  border: m.role === 'assistant' ? '1px solid #334155' : 'none'
                }}>
                  <Typography variant="body2" sx={{ fontWeight: 500, lineHeight: 1.5, fontSize: '0.85rem' }}>{m.content}</Typography>
                </Box>
                {m.role === 'user' && <Avatar sx={{ bgcolor: '#334155', width: 28, height: 28 }}><User size={16} /></Avatar>}
              </Stack>
            </ListItem>
          ))}
          {loading && (
            <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
               <Avatar sx={{ bgcolor: 'primary.main', width: 28, height: 28 }}><Bot size={16} color="black" /></Avatar>
               <CircularProgress size={12} color="primary" />
               <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>Reasoning...</Typography>
            </Box>
          )}
          <div ref={endRef} />
        </List>
      </Paper>

      {/* 4. Input Area */}
      <Stack direction="row" spacing={1} sx={{ p: 0.5, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1.5, border: '1px solid #334155' }}>
        <TextField
          fullWidth
          multiline
          maxRows={3}
          placeholder="Ask institutional context..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          sx={{ '& .MuiOutlinedInput-notchedOutline': { border: 'none' }, '& .MuiInputBase-input': { fontSize: '0.85rem' } }}
        />
        <IconButton
          color="primary"
          onClick={handleSend}
          disabled={!input.trim() || loading}
          sx={{ alignSelf: 'flex-end', mb: 0.5, mr: 0.5, bgcolor: 'primary.main', color: 'black', width: 32, height: 32, '&:hover': { bgcolor: 'primary.dark' } }}
        >
          <Send size={16} />
        </IconButton>
      </Stack>

      {!isDrawer && (
        <Stack direction="row" spacing={3} sx={{ mt: 1.5, px: 1 }}>
           <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 700 }}>
              <TrendingUp size={10} /> Probabilistic outcomes.
           </Typography>
           <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 700 }}>
              <Info size={10} /> Grounded in 10-year data.
           </Typography>
        </Stack>
      )}
    </Box>
  );
}
