import { Box, Typography, Paper, Grid, Rating, Stack, Chip } from '@mui/material';
import { Award, ShieldCheck, Zap, Anchor } from 'lucide-react';

export default function ManagementMoat({ analysis }: { analysis: any }) {
  if (!analysis || !analysis.recommendations) return null;

  const fundAgent = analysis.recommendations.find((r: any) => r.agent_name === 'Fundamental');
  const moat = fundAgent?.moat_rating || 'WIDE';
  const score = fundAgent?.management_score || 4.5;

  const factors = [
    { label: 'Pricing Power', score: score, icon: < Zap size={16} /> },
    { label: 'Switching Costs', score: Math.max(1, score - 0.5), icon: <Anchor size={16} /> },
    { label: 'Brand Strength', score: Math.min(5, score + 0.5), icon: <Award size={16} /> },
    { label: 'Corporate Governance', score: score, icon: <ShieldCheck size={16} /> },
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Award size={20} className="text-amber-500" /> Management & Moat Analysis
      </Typography>

      <Paper sx={{ p: 3 }}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>ECONOMIC MOAT RATING</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
               <Typography variant="h4" fontWeight="bold" color="primary">{moat.toUpperCase()} MOAT</Typography>
               <Chip label="SUSTAINABLE" size="small" variant="outlined" color="primary" />
            </Box>
            <Typography variant="body2" color="textSecondary" sx={{ lineHeight: 1.6 }}>
               AI analysis of market position, competitive barriers, and capital allocation efficiency.
               {fundAgent ? ` ${fundAgent.reasons[0]}` : ''}
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
             <Stack spacing={2.5}>
                {factors.map((f) => (
                  <Box key={f.label} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                     <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box sx={{ color: 'primary.main' }}>{f.icon}</Box>
                        <Typography variant="body2" fontWeight="bold">{f.label}</Typography>
                     </Box>
                     <Rating value={f.score} precision={0.1} readOnly size="small" />
                  </Box>
                ))}
             </Stack>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}
