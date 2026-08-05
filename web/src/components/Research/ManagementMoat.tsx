import { Box, Typography, Paper, Grid, Rating, Stack } from '@mui/material';
import { Award, ShieldCheck, Zap, Anchor } from 'lucide-react';

export default function ManagementMoat() {
  const factors = [
    { label: 'Pricing Power', score: 4.5, icon: < Zap size={16} /> },
    { label: 'Switching Costs', score: 4.0, icon: <Anchor size={16} /> },
    { label: 'Brand Strength', score: 5.0, icon: <Award size={16} /> },
    { label: 'Corporate Governance', score: 4.8, icon: <ShieldCheck size={16} /> },
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
               <Typography variant="h4" fontWeight="bold" color="primary">WIDE MOAT</Typography>
               <Chip label="SUSTAINABLE" size="small" variant="outlined" color="primary" />
            </Box>
            <Typography variant="body2" color="textSecondary" sx={{ lineHeight: 1.6 }}>
               The company possesses a dominant market position with high entry barriers.
               Management has demonstrated exceptional capital allocation efficiency over the last decade.
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

import { Chip } from '@mui/material';
