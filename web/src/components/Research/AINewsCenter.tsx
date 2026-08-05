import { Box, Typography, Paper, List, ListItem, Chip, Stack } from '@mui/material';
import { Newspaper, ArrowUpRight, ArrowDownRight, Zap } from 'lucide-react';

export default function AINewsCenter() {
  const news = [
    { title: 'Expansion into Emerging Markets', impact: 'BULLISH', score: 85, summary: 'Management announced a $2B investment in SE Asia, expected to boost revenue by 12%.' },
    { title: 'Regulatory Headwinds in EU', impact: 'BEARISH', score: 40, summary: 'New compliance requirements may increase operational costs in the tech segment.' },
    { title: 'Partnership with Global Tech Leader', impact: 'BULLISH', score: 92, summary: 'AI-driven logistics optimization project launched with Azure.' },
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Newspaper size={20} className="text-emerald-500" /> AI News Center
      </Typography>

      <Paper sx={{ p: 0, overflow: 'hidden' }}>
        <List>
          {news.map((item, idx) => (
            <ListItem key={idx} divider={idx !== news.length - 1} sx={{ display: 'block', p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Typography variant="subtitle1" fontWeight="bold">{item.title}</Typography>
                <Stack direction="row" spacing={1}>
                  <Chip
                    label={item.impact}
                    size="small"
                    icon={item.impact === 'BULLISH' ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                    sx={{ bgcolor: item.impact === 'BULLISH' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)', color: item.impact === 'BULLISH' ? '#10b981' : '#f43f5e' }}
                  />
                  <Chip label={`${item.score}% Importance`} size="small" variant="outlined" sx={{ fontSize: '0.65rem' }} />
                </Stack>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ lineHeight: 1.6, mb: 1.5 }}>
                {item.summary}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'primary.main' }}>
                 <Zap size={14} />
                 <Typography variant="caption" fontWeight="bold">AI IMPACT ANALYSIS ACTIVE</Typography>
              </Box>
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
}
