import { useState } from 'react';
import { Box, Drawer, IconButton, TextField, Typography, Paper, Fab, CircularProgress, Chip } from '@mui/material';
import { X, Send, Bot, BrainCircuit } from 'lucide-react';
import { chatWithAssistant } from '../api/client';
import { normalizeAITradeDecision } from '../hooks/useAITradeDecision';

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
      let contextPrompt = message;
      if (stockContext) {
        const decision = normalizeAITradeDecision(stockContext);
        contextPrompt = `Context: Analyzing ${stockContext.symbol} (${stockContext.name}).
Price: ₹${stockContext.last_price}.
AI Rating: ${decision.rating}.
Conviction: ${decision.conviction}%.
Thesis: ${decision.thesis}.
Question: ${message}`;
      }

      const response = await chatWithAssistant(contextPrompt);
      setChat(prev => [...prev, { role: 'assistant', content: response }]);
    } catch (e) {
      setChat(prev => [...prev, { role: 'assistant', content: "System Link Error: I'm currently unable to reach institutional knowledge agents. Please try again." }]);
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
                  <Typography variant="h6" fontWeight={800}>AI Copilot</Typography>
                  <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>LEAD ANALYST ENGINE ACTIVE</Typography>
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
                  border: m.role === 'user' ? 'none' : '1px solid #334155',
                  borderRadius: 2
                }}
               >
                 <Typography variant="body2" sx={{ fontWeight: m.role === 'user' ? 600 : 400, lineHeight: 1.6 }}>{m.content}</Typography>
               </Paper>
             ))}
             {loading && (
               <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', ml: 1 }}>
                  <CircularProgress size={16} />
                  <Typography variant="caption" color="textSecondary">Reasoning...</Typography>
               </Box>
             )}
          </Box>

          <Box sx={{ p: 3, bgcolor: '#0f172a', borderTop: '1px solid #334155' }}>
             <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  placeholder="Ask about setups, catalysts, or risks..."
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
                  sx={{ width: 40, height: 40, bgcolor: 'primary.main', color: 'black', '&:hover': { bgcolor: 'primary.dark' }, borderRadius: 1 }}
                >
                  <Send size={18} />
                </IconButton>
             </Box>
             <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip label="Verify Catalyst" size="small" variant="outlined" sx={{ fontWeight: 700 }} onClick={() => setMessage("Verify the primary catalysts for this decision.")} />
                <Chip label="Invalidation Points" size="small" variant="outlined" sx={{ fontWeight: 700 }} onClick={() => setMessage("What specific events would invalidate this thesis?")} />
             </Box>
          </Box>
        </Box>
      </Drawer>
    </>
  );
}
