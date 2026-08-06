import { useState } from 'react';
import { Box, Drawer, IconButton, TextField, Typography, Paper, Fab, CircularProgress, Chip } from '@mui/material';
import { X, Send, Bot, BrainCircuit } from 'lucide-react';
import { chatWithAssistant } from '../api/client';

export default function AICopilot({ stockContext }: { stockContext?: any }) {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [chat, setChat] = useState<any[]>([
    { role: 'assistant', content: `Hello! I'm your institutional AI Copilot. ${stockContext ? `I'm currently analyzing ${stockContext.symbol}.` : "How can I help you today?"}` }
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!message.trim()) return;
    const userMsg = { role: 'user', content: message };
    setChat([...chat, userMsg]);
    setMessage('');
    setLoading(true);

    try {
      // Enhanced context for Copilot
      const contextPrompt = stockContext ? `Context: You are analyzing ${stockContext.symbol}. Current price ₹${stockContext.last_price}. AI Score: ${stockContext.ai_investment_score}. \nQuestion: ${message}` : message;
      const response = await chatWithAssistant(contextPrompt);
      setChat(prev => [...prev, { role: 'assistant', content: response }]);
    } catch (e) {
      setChat(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Fab
        color="primary"
        onClick={() => setOpen(true)}
        sx={{ position: 'fixed', bottom: 30, right: 30, width: 60, height: 60, boxShadow: '0 8px 32px rgba(16, 185, 129, 0.4)' }}
      >
        <Bot size={28} />
      </Fab>

      <Drawer
        anchor="right"
        open={open}
        onClose={() => setOpen(false)}
        PaperProps={{ sx: { width: { xs: '100%', sm: 450 }, bgcolor: '#020617', borderLeft: '1px solid #334155' } }}
      >
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ p: 3, bgcolor: '#0f172a', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
               <BrainCircuit size={24} className="text-emerald-500" />
               <Box>
                  <Typography variant="h6" fontWeight="bold">AI Copilot</Typography>
                  <Typography variant="caption" color="textSecondary">Institutional Analysis Active</Typography>
               </Box>
            </Box>
            <IconButton onClick={() => setOpen(false)} size="small"><X size={20} /></IconButton>
          </Box>

          <Box sx={{ flexGrow: 1, p: 3, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 2 }}>
             {chat.map((m, i) => (
               <Paper
                key={i}
                sx={{
                  p: 2,
                  alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '85%',
                  bgcolor: m.role === 'user' ? '#10b981' : 'rgba(15, 23, 42, 0.5)',
                  color: m.role === 'user' ? '#000' : '#fff',
                  border: m.role === 'user' ? 'none' : '1px solid #334155'
                }}
               >
                 <Typography variant="body2" sx={{ fontWeight: m.role === 'user' ? 500 : 400, lineHeight: 1.6 }}>{m.content}</Typography>
               </Paper>
             ))}
             {loading && <CircularProgress size={20} sx={{ ml: 2 }} />}
          </Box>

          <Box sx={{ p: 3, bgcolor: '#0f172a', borderTop: '1px solid #334155' }}>
             <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  placeholder="Ask me anything about the market..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  size="small"
                  multiline
                  maxRows={4}
                  InputProps={{ sx: { bgcolor: '#020617' } }}
                />
                <IconButton
                  color="primary"
                  disabled={!message.trim() || loading}
                  onClick={handleSend}
                  sx={{ width: 40, height: 40, bgcolor: 'primary.main', color: 'black', '&:hover': { bgcolor: 'primary.dark' } }}
                >
                  <Send size={18} />
                </IconButton>
             </Box>
             <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                <Chip label="Simulate Buy" size="small" variant="outlined" onClick={() => setMessage("What if I buy this stock today?")} />
                <Chip label="Risk Audit" size="small" variant="outlined" onClick={() => setMessage("Run a deep risk audit.")} />
             </Box>
          </Box>
        </Box>
      </Drawer>
    </>
  );
}
