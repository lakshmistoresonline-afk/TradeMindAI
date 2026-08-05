import { Box, Typography, Paper, Grid, LinearProgress, Divider } from '@mui/material';
import { Brain, Target, ShieldCheck, Clock, Zap } from 'lucide-react';

export default function AIExecutiveSummary({ analysis }: { analysis: any }) {
  if (!analysis) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Brain size={20} className="text-emerald-500" /> AI Executive Summary
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%', border: '1px solid #10b981', bgcolor: 'rgba(16, 185, 129, 0.05)' }}>
            <Typography variant="subtitle2" color="textSecondary">OVERALL RATING</Typography>
            <Typography variant="h3" color="primary" fontWeight="bold" sx={{ my: 1 }}>BUY</Typography>
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="caption">Confidence Score</Typography>
                <Typography variant="caption" fontWeight="bold">85%</Typography>
              </Box>
              <LinearProgress variant="determinate" value={85} sx={{ height: 8, borderRadius: 5 }} />
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Grid container spacing={2}>
              <Grid item xs={6} md={3}>
                <SummaryStat icon={<Target size={16} />} label="Probability" value="78.2%" />
              </Grid>
              <Grid item xs={6} md={3}>
                <SummaryStat icon={<ShieldCheck size={16} />} label="Risk Level" value="LOW" color="primary.main" />
              </Grid>
              <Grid item xs={6} md={3}>
                <SummaryStat icon={<Clock size={16} />} label="Horizon" value="3-6 Months" />
              </Grid>
              <Grid item xs={6} md={3}>
                <SummaryStat icon={<Zap size={16} />} label="Target" value="₹2,840" color="primary.main" />
              </Grid>
            </Grid>
            <Divider sx={{ my: 2, opacity: 0.1 }} />
            <Typography variant="body2" sx={{ lineHeight: 1.7, color: 'text.secondary' }}>
              {analysis.consensus}
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function SummaryStat({ icon, label, value, color }: any) {
  return (
    <Box>
      <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        {icon} {label}
      </Typography>
      <Typography variant="h6" fontWeight="bold" sx={{ color: color || 'text.primary' }}>{value}</Typography>
    </Box>
  );
}
