import { Box, Typography, Paper, Chip, Stack } from '@mui/material';
import { Brain, Cpu, Zap, Search } from 'lucide-react';

interface AnalysisReportProps {
  data: any;
}

export default function AnalysisReport({ data }: AnalysisReportProps) {
  if (!data || !data.recommendations) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', py: 8 }}>
        <Search size={48} className="text-slategray mb-4 opacity-20" />
        <Typography color="textSecondary">Select a stock to view AI analysis report</Typography>
      </Box>
    );
  }

  const getIcon = (agent: string) => {
    switch (agent) {
      case 'Technical': return <Brain size={18} />;
      case 'Fundamental': return <Cpu size={18} />;
      case 'Sentiment': return <Search size={18} />;
      default: return <Zap size={18} />;
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" fontWeight="bold">AI Report: {data.symbol}</Typography>
        <Chip label="AI Consensus Active" color="primary" size="small" variant="outlined" />
      </Box>

      {data.technical_data?.ml_prediction && (
        <Paper sx={{ p: 3, mb: 3, border: '1px solid #2979FF', backgroundColor: 'rgba(41, 121, 255, 0.05)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, color: '#2979FF' }}>
            <Cpu size={20} />
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>ML Predictive Intelligence</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="body2" color="textSecondary">5-Day Price Direction Prediction</Typography>
              <Typography variant="h5" sx={{ color: data.technical_data.ml_prediction.prediction === 'UP' ? '#10b981' : '#f43f5e', fontWeight: 'bold' }}>
                {data.technical_data.ml_prediction.prediction}
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="body2" color="textSecondary">Model Confidence</Typography>
              <Typography variant="h5" sx={{ fontWeight: 'bold' }}>{data.technical_data.ml_prediction.confidence}%</Typography>
            </Box>
          </Box>
        </Paper>
      )}

      <Stack spacing={3}>
        {data.recommendations.map((rec: any, index: number) => (
          <Paper key={index} sx={{ p: 3, backgroundColor: 'rgba(15, 23, 42, 0.5)' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, color: '#10b981' }}>
              {getIcon(rec.agent)}
              <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 'bold', textTransform: 'uppercase' }}>
                {rec.agent} Agent Analysis
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ lineHeight: 1.6, whiteSpace: 'pre-line' }}>
              {rec.analysis}
            </Typography>
          </Paper>
        ))}

        <Paper sx={{ p: 3, border: '1px solid #10b981', backgroundColor: 'rgba(16, 185, 129, 0.05)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, color: '#10b981' }}>
            <Zap size={20} />
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>Final Consensus</Typography>
          </Box>
          <Typography variant="body1" sx={{ fontWeight: 500, lineHeight: 1.6 }}>
            {data.consensus}
          </Typography>
        </Paper>
      </Stack>
    </Box>
  );
}
