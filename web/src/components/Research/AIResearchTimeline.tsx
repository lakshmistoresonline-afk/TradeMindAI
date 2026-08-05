import { Box, Typography, Paper, Stepper, Step, StepLabel, StepContent, Chip } from '@mui/material';
import { Calendar, History, Activity } from 'lucide-react';

const mockTimeline = [
  { date: 'Aug 04, 2026', title: 'Rating Upgrade: BUY', desc: 'AI Investment Score increased from 62 to 78 following FII accumulation.', type: 'RATING' },
  { date: 'Jul 28, 2026', title: 'Pattern Breakout', desc: 'SMC Bullish Order Block formed at ₹2450 level.', type: 'TECHNICAL' },
  { date: 'Jul 15, 2026', title: 'Earnings Beat', desc: 'Quarterly revenue exceeded consensus by 4.2%. Management outlook positive.', type: 'FUNDAMENTAL' },
  { date: 'Jun 30, 2026', title: 'Rating Hold', desc: 'ML models showed high volatility bias. Neutral stance maintained.', type: 'RATING' },
];

export default function AIResearchTimeline() {
  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <History size={20} className="text-blue-500" /> AI Intelligence Timeline
      </Typography>

      <Paper sx={{ p: 4 }}>
        <Stepper orientation="vertical">
          {mockTimeline.map((item, index) => (
            <Step key={index} active={true}>
              <StepLabel
                StepIconComponent={() => <Box sx={{ width: 10, height: 10, bgcolor: item.type === 'RATING' ? 'primary.main' : 'text.secondary', borderRadius: '50%' }} />}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="subtitle2" fontWeight="bold">{item.title}</Typography>
                  <Typography variant="caption" color="textSecondary">{item.date}</Typography>
                  <Chip label={item.type} size="small" variant="outlined" sx={{ height: 18, fontSize: '0.6rem' }} />
                </Box>
              </StepLabel>
              <StepContent>
                <Typography variant="body2" color="textSecondary">{item.desc}</Typography>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </Paper>
    </Box>
  );
}
