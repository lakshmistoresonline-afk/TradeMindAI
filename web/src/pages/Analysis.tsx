import React from 'react';
import { Box, Typography, Paper, Grid, Card, CardContent } from '@mui/material';
import { Brain, Cpu, Zap } from 'lucide-react';

export default function Analysis() {
  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>AI Intelligence</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 4, minHeight: 500 }}>
            <Typography variant="h6" gutterBottom>Consensus Engine</Typography>
            <Typography color="textSecondary" sx={{ mb: 4 }}>
              Select a stock from the market list to view detailed AI reasoning, sentiment analysis, and multi-agent technical synthesis.
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <AnalysisStep icon={<Brain size={20} />} title="Technical Agent" status="Waiting for input..." />
              <AnalysisStep icon={<Cpu size={20} />} title="Fundamental Agent" status="Waiting for input..." />
              <AnalysisStep icon={<Zap size={20} />} title="Consensus Agent" status="Waiting for input..." />
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Agent Status</Typography>
              <Typography variant="body2" color="textSecondary">
                Our agents are currently scanning 50+ Nifty stocks every 15 minutes.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

function AnalysisStep({ icon, title, status }: any) {
  return (
    <Box sx={{ p: 2, border: '1px solid #334155', borderRadius: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
      <Box sx={{ p: 1, backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#10b981', borderRadius: '50%' }}>
        {icon}
      </Box>
      <Box>
        <Typography fontWeight="bold">{title}</Typography>
        <Typography variant="caption" color="textSecondary">{status}</Typography>
      </Box>
    </Box>
  );
}
