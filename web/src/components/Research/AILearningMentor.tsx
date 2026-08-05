import { Box, Typography, Paper, Accordion, AccordionSummary, AccordionDetails, Chip } from '@mui/material';
import { BookOpen, ChevronDown, Zap } from 'lucide-react';

export default function AILearningMentor() {
  const concepts = [
    {
      term: 'Order Block (SMC)',
      definition: 'A specific price level where institutional buyers or sellers have placed large orders, creating a supply or demand zone.',
      why_it_matters: 'Identifying these zones helps retail traders align with institutional flow.'
    },
    {
      term: 'RSI Divergence',
      definition: 'When the price makes a new high/low but the RSI indicator does not, suggesting a weakening trend.',
      why_it_matters: 'It often precedes a price reversal or consolidation.'
    },
    {
      term: 'Wide Moat',
      definition: 'A significant competitive advantage that allows a company to protect its long-term profits and market share.',
      why_it_matters: 'Wide moat companies are generally safer long-term investments.'
    },
    {
      term: 'Sharpe Ratio',
      definition: 'A measure of risk-adjusted return, calculated by dividing the excess return by the volatility.',
      why_it_matters: 'Higher Sharpe ratios indicate better returns for each unit of risk taken.'
    }
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <BookOpen size={20} className="text-amber-500" /> AI Learning & Mentor
      </Typography>

      <Paper sx={{ p: 0, overflow: 'hidden' }}>
        <Box sx={{ p: 2, bgcolor: 'rgba(255, 171, 0, 0.05)', borderBottom: '1px solid #334155' }}>
           <Typography variant="body2" color="textSecondary">
              Your personalized mentor explaining complex institutional concepts used in this research.
           </Typography>
        </Box>
        {concepts.map((c, i) => (
          <Accordion key={i} sx={{ bgcolor: 'transparent', boxShadow: 'none', '&:before': { display: 'none' } }}>
            <AccordionSummary expandIcon={<ChevronDown size={18} />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                 <Chip label="Concept" size="small" sx={{ height: 18, fontSize: '0.6rem' }} />
                 <Typography variant="subtitle2" fontWeight="bold">{c.term}</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails sx={{ pt: 0, pb: 3, px: 3 }}>
              <Typography variant="body2" sx={{ lineHeight: 1.6, mb: 2 }}>{c.definition}</Typography>
              <Box sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 2, borderLeft: '3px solid #FFAB00' }}>
                 <Typography variant="caption" fontWeight="bold" color="#FFAB00" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                    <Zap size={12} /> WHY IT MATTERS
                 </Typography>
                 <Typography variant="body2" color="textSecondary">{c.why_it_matters}</Typography>
              </Box>
            </AccordionDetails>
          </Accordion>
        ))}
      </Paper>
    </Box>
  );
}
