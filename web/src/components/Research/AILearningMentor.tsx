import { Box, Typography, Paper, Accordion, AccordionSummary, AccordionDetails, Chip } from '@mui/material';
import { BookOpen, ChevronDown, Zap } from 'lucide-react';

export default function AILearningMentor() {
  const concepts = [
    {
      term: 'Order Block (SMC)',
      definition: 'A price region where institutional activity is concentrated, often leading to strong momentum shifts.',
      why_it_matters: 'TradeMind AI prioritizes these zones for high-conviction entry signals.'
    },
    {
      term: 'Consensus Agent',
      definition: 'Our meta-AI layer that weights 12 specialized analyst agents to provide a unified investment decision.',
      why_it_matters: 'Reduces individual agent bias and increases overall signal reliability.'
    },
    {
      term: 'Digital Twin',
      definition: 'A real-time data mirror of an asset that combines its technical posture, risk profile, and intelligence DNA.',
      why_it_matters: 'Provides a complete identity of the stock beyond simple price action.'
    },
    {
      term: 'Sharpe Ratio',
      definition: 'An institutional metric that evaluates how much excess return you receive for the extra volatility you endure.',
      why_it_matters: 'TradeMind AI only recommends trades with a favorable risk-adjusted profile.'
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
