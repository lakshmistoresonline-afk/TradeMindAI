import { useState, useEffect } from 'react';
import { Box, Typography, Paper, List, ListItem, Chip, Stack, CircularProgress } from '@mui/material';
import { Newspaper, ArrowUpRight, ArrowDownRight, Zap } from 'lucide-react';
import { getStockNews } from '../../api/client';

export default function AINewsCenter({ symbol }: { symbol: string }) {
  const [news, setNews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getStockNews(symbol)
      .then(setNews)
      .finally(() => setLoading(false));
  }, [symbol]);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress size={24} /></Box>;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Newspaper size={20} className="text-emerald-500" /> AI News Center: {symbol}
      </Typography>

      <Paper sx={{ p: 0, overflow: 'hidden' }}>
        <List>
          {news.length > 0 ? news.map((item, idx) => (
            <ListItem key={idx} divider={idx !== news.length - 1} sx={{ display: 'block', p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Typography variant="subtitle1" fontWeight="bold">{item.title}</Typography>
                <Stack direction="row" spacing={1}>
                  <Chip
                    label={item.sentiment_label?.toUpperCase() || 'NEUTRAL'}
                    size="small"
                    icon={item.sentiment_label === 'bullish' ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                    sx={{
                      bgcolor: item.sentiment_label === 'bullish' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
                      color: item.sentiment_label === 'bullish' ? '#10b981' : '#f43f5e'
                    }}
                  />
                  <Chip label={item.source} size="small" variant="outlined" sx={{ fontSize: '0.65rem' }} />
                </Stack>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ lineHeight: 1.6, mb: 1.5 }}>
                {item.content || item.summary}
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                 <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'primary.main' }}>
                    <Zap size={14} />
                    <Typography variant="caption" fontWeight="bold">AI IMPACT ANALYSIS ACTIVE</Typography>
                 </Box>
                 <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 'bold' }}>
                    {item.published_at ? new Date(item.published_at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) : '---'}
                 </Typography>
              </Box>
            </ListItem>
          )) : (
            <Box sx={{ p: 4, textAlign: 'center' }}>
               <Typography color="textSecondary">No recent institutional news found for {symbol}.</Typography>
            </Box>
          )}
        </List>
      </Paper>
    </Box>
  );
}
