import { useState, useRef, useEffect } from 'react';
import { Box, Typography, Paper, TextField, IconButton, Avatar, Stack, CircularProgress } from '@mui/material';
import { Send, Bot, User, Trash2 } from 'lucide-react';

interface Message {
  text: string;
  sender: 'ai' | 'user';
  timestamp: Date;
}

export default function AIChat() {
  const [messages, setMessages] = useState<Message[]>([
    { text: "Hello! I am your TradeMind Assistant. Ask me anything about the NSE market, technical patterns, or your portfolio.", sender: 'ai', timestamp: new Date() }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg: Message = { text: input, sender: 'user', timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Simulate API call to Groq via backend
      // In Phase 10 we will connect this to real backend endpoint
      setTimeout(() => {
        const aiMsg: Message = {
          text: `Analyzing ${input}... Based on current Nifty trends, the market shows strong support at 23,400. I recommend looking at HDFC Bank for a potential mean-reversion trade.`,
          sender: 'ai',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, aiMsg]);
        setLoading(false);
      }, 1500);
    } catch (error) {
      console.error(error);
      setLoading(false);
    }
  };

  return (
    <Box sx={{ height: 'calc(100vh - 120.dp)', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>AI Market Assistant</Typography>
        <IconButton onClick={() => setMessages([messages[0]])} size="small">
          <Trash2 size={18} />
        </IconButton>
      </Box>

      <Paper sx={{ flexGrow: 1, mb: 2, p: 3, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 2 }}>
        {messages.map((msg, i) => (
          <Box key={i} sx={{ alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start', maxWidth: '70%' }}>
            <Stack direction={msg.sender === 'user' ? 'row-reverse' : 'row'} spacing={1} alignItems="flex-start">
              <Avatar sx={{ bgcolor: msg.sender === 'user' ? 'primary.main' : 'secondary.main', width: 32, height: 32 }}>
                {msg.sender === 'user' ? <User size={18} /> : <Bot size={18} />}
              </Avatar>
              <Paper sx={{
                p: 2,
                bgcolor: msg.sender === 'user' ? 'primary.main' : 'background.default',
                borderRadius: msg.sender === 'user' ? '20px 4px 20px 20px' : '4px 20px 20px 20px'
              }}>
                <Typography variant="body2">{msg.text}</Typography>
                <Typography variant="caption" sx={{ opacity: 0.5, mt: 1, display: 'block', textAlign: 'right' }}>
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </Typography>
              </Paper>
            </Stack>
          </Box>
        ))}
        {loading && <CircularProgress size={20} sx={{ ml: 2 }} />}
        <div ref={messagesEndRef} />
      </Paper>

      <Paper sx={{ p: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder="Ask about market bias, SMC patterns, or stock analysis..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
          sx={{ '& .MuiOutlinedInput-root': { border: 'none' } }}
        />
        <IconButton color="primary" onClick={handleSend} disabled={!input.trim() || loading}>
          <Send size={24} />
        </IconButton>
      </Paper>
    </Box>
  );
}
