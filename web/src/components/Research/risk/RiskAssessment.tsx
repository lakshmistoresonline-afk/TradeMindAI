import React from 'react';
import { Box, Typography, Paper, Grid, Chip, LinearProgress } from '@mui/material';
import { ShieldAlert } from 'lucide-react';

interface RiskAssessmentProps {
  stock?: any;
}

export const RiskAssessment: React.FC<RiskAssessmentProps> = ({ stock }) => {
  const beta = stock?.beta || 1.0;
  const marketRisk = Math.min(Math.round(beta * 60), 100);
  const volRisk = Math.min(Math.round(beta * 70), 100);

  const risks = [
    { label: 'Market Risk', score: marketRisk, level: marketRisk > 70 ? 'HIGH' : marketRisk > 40 ? 'MEDIUM' : 'LOW', desc: 'Sensitivity to broader Nifty 100 volatility.' },
    { label: 'Business Risk', score: stock?.debt_to_equity ? Math.min(Math.round(stock.debt_to_equity * 40), 100) : 25, level: 'LOW', desc: 'Financial stability and management quality.' },
    { label: 'Liquidity Risk', score: stock?.avg_volume ? 15 : 45, level: 'LOW', desc: 'Ease of entry/exit without price impact.' },
    { label: 'Volatility Risk', score: volRisk, level: volRisk > 70 ? 'HIGH' : volRisk > 40 ? 'MEDIUM' : 'LOW', desc: 'Expected daily price swings based on Beta.' },
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <ShieldAlert size={20} className="text-rose-500" /> Risk Assessment
      </Typography>

      <Grid container spacing={3}>
        {risks.map((risk) => (
          <Grid item xs={12} sm={6} md={3} key={risk.label}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle2" fontWeight="bold">{risk.label}</Typography>
                <Chip
                  label={risk.level}
                  size="small"
                  sx={{
                    bgcolor: risk.level === 'HIGH' ? 'rgba(244, 63, 94, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                    color: risk.level === 'HIGH' ? '#f43f5e' : '#10b981',
                    fontSize: '0.6rem', fontWeight: 'bold'
                  }}
                />
              </Box>
              <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mb: 2, height: 40 }}>
                {risk.desc}
              </Typography>
              <Box sx={{ mt: 'auto' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                   <Typography variant="caption">Risk Probability</Typography>
                   <Typography variant="caption" fontWeight="bold">{risk.score}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={risk.score}
                  color={risk.score > 70 ? 'error' : risk.score > 40 ? 'warning' : 'primary'}
                  sx={{ height: 6, borderRadius: 2 }}
                />
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default RiskAssessment;
