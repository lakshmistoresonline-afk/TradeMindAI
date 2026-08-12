import { useState, useEffect, useRef } from 'react';
import { Box, Typography, Paper, TextField, IconButton, List, ListItem, Avatar, Stack, Chip, CircularProgress } from '@mui/material';
import { Send, Bot, User, Sparkles, BrainCircuit, TrendingUp, Info } from 'lucide-react';
import { chatWithAssistant } from '../api/client';

export default function AICopilot({ isDrawer = false }: { isDrawer?: boolean }) {
  const [messages, setMessages] = useState<any[]>([
    { role: 'assistant', content: 'TRADEMIND AI Copilot active. How can I assist your institutional research today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
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
    <Box sx={{ height: isDrawer ? '100%' : 'calc(100vh - 140px)', display: 'flex', flexDirection: 'column' }}>
      {!isDrawer && (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
           <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ p: 1, bgcolor: 'primary.main', borderRadius: 1, color: 'black' }}>
                 <Bot size={24} />
              </Box>
              <Box>
                 <Typography variant="h5" sx={{ fontWeight: 800 }}>AI Copilot</Typography>
                 <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>LLAMA 3.1 INSTITUTIONAL ENGINE</Typography>
              </Box>
           </Box>
           <Stack direction="row" spacing={1}>
              <Chip icon={<Sparkles size={14} />} label="Context: Terminal" size="small" variant="outlined" sx={{ fontWeight: 800 }} />
              <Chip icon={<BrainCircuit size={14} />} label="Agent: Lead Analyst" size="small" variant="outlined" sx={{ fontWeight: 800 }} />
           </Stack>
        </Box>
      )}

      <Paper sx={{
        flexGrow: 1,
        mb: 2,
        overflowY: 'auto',
        p: isDrawer ? 2 : 3,
        display: 'flex',
        flexDirection: 'column',
        bgcolor: isDrawer ? 'transparent' : 'rgba(15, 23, 42, 0.3)',
        border: isDrawer ? 'none' : '1px solid #1e293b'
      }}>
        <List sx={{ flexGrow: 1 }}>
          {messages.map((m, i) => (
            <ListItem key={i} sx={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start', mb: 3, px: 0 }}>
              <Stack direction="row" spacing={2} sx={{ maxWidth: '80%' }}>
                {m.role === 'assistant' && <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}><Bot size={18} color="black" /></Avatar>}
                <Box sx={{
                  p: 2,
                  borderRadius: 2,
                  bgcolor: m.role === 'user' ? 'primary.main' : 'rgba(255,255,255,0.05)',
                  color: m.role === 'user' ? 'black' : 'white',
                  border: m.role === 'assistant' ? '1px solid #334155' : 'none'
                }}>
                  <Typography variant="body2" sx={{ fontWeight: 500, lineHeight: 1.6 }}>{m.content}</Typography>
                </Box>
                {m.role === 'user' && <Avatar sx={{ bgcolor: '#334155', width: 32, height: 32 }}><User size={18} /></Avatar>}
              </Stack>
            </ListItem>
          ))}
          {loading && (
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
               <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}><Bot size={18} color="black" /></Avatar>
               <CircularProgress size={16} color="primary" />
               <Typography variant="caption" color="textSecondary">Reasoning...</Typography>
            </Box>
          )}
          <div ref={endRef} />
        </List>
      </Paper>

      <Stack direction="row" spacing={2} sx={{ p: 1, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 2, border: '1px solid #334155' }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder="Ask about market bias, SMC patterns, or stock analysis..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          sx={{ '& .MuiOutlinedInput-notchedOutline': { border: 'none' } }}
        />
        <IconButton
          color="primary"
          onClick={handleSend}
          disabled={!input.trim() || loading}
          sx={{ alignSelf: 'flex-end', mb: 0.5, mr: 0.5, bgcolor: 'primary.main', color: 'black', '&:hover': { bgcolor: 'primary.dark' } }}
        >
          <Send size={20} />
        </IconButton>
      </Stack>

      <Stack direction="row" spacing={3} sx={{ mt: 1, px: 1 }}>
         <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <TrendingUp size={12} /> Probabilistic outcomes are AI generated.
         </Typography>
         <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Info size={12} /> Grounded in 10-year historical dataset.
         </Typography>
      </Stack>
    </Box>
  );
}
