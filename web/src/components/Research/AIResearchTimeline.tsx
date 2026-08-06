import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Stepper, Step, StepLabel, StepContent, Chip, CircularProgress } from '@mui/material';
import { History } from 'lucide-react';
import { getStockTimeline } from '../../api/client';

export default function AIResearchTimeline({ symbol }: { symbol: string }) {
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getStockTimeline(symbol)
      .then(setTimeline)
      .finally(() => setLoading(false));
  }, [symbol]);

  if (loading) return <CircularProgress size={24} />;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <History size={20} className="text-blue-500" /> AI Intelligence Timeline: {symbol}
      </Typography>

      <Paper sx={{ p: 4 }}>
        {timeline.length > 0 ? (
          <Stepper orientation="vertical">
            {timeline.map((item, index) => (
              <Step key={index} active={true}>
                <StepLabel
                  StepIconComponent={() => <Box sx={{ width: 10, height: 10, bgcolor: item.type === 'RATING' ? 'primary.main' : 'text.secondary', borderRadius: '50%' }} />}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Typography variant="subtitle2" fontWeight="bold">{item.title}</Typography>
                    <Typography variant="caption" color="textSecondary">
                       {new Date(item.date).toLocaleDateString()}
                    </Typography>
                    <Chip label={item.type} size="small" variant="outlined" sx={{ height: 18, fontSize: '0.6rem' }} />
                  </Box>
                </StepLabel>
                <StepContent>
                  <Typography variant="body2" color="textSecondary">{item.desc}</Typography>
                </StepContent>
              </Step>
            ))}
          </Stepper>
        ) : (
          <Box sx={{ py: 4, textAlign: 'center' }}>
             <Typography color="textSecondary">No timeline events recorded yet.</Typography>
          </Box>
        )}
      </Paper>
    </Box>
  );
}
