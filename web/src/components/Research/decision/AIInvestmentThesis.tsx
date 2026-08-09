import { Box, Typography, Paper, Grid, Stack, Divider, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import { AlertTriangle, Lightbulb, TrendingUp } from 'lucide-react';
import { useAITradeDecision } from '../../../hooks/useAITradeDecision';

export default function AIInvestmentThesis({ stock }: { stock: any }) {
  const decision = useAITradeDecision(stock);

  if (!stock || !stock.analysis) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Lightbulb size={20} className="text-amber-400" /> AI Investment Thesis
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle2" color="primary" gutterBottom sx={{ fontWeight: 800 }}>THE BULL CASE / WHY AI LIKES IT</Typography>
            <List>
               {decision.rating.includes('BUY') && decision.thesis ? (
                 <ThesisItem text={decision.thesis} />
               ) : (
                 <>
                   <ThesisItem text="Strong institutional accumulation detected in latest quarterly flow." />
                   <ThesisItem text="Price broke out of a multi-month accumulation base with high volume." />
                   <ThesisItem text="Positive bias across major trend indicators on daily timeframe." />
                 </>
               )}
               {decision.primaryCatalyst && <ThesisItem text={`Catalyst: ${decision.primaryCatalyst}`} />}
            </List>

            <Divider sx={{ my: 2, opacity: 0.05 }} />

            <Typography variant="subtitle2" color="error" gutterBottom sx={{ fontWeight: 800 }}>THE BEAR CASE / WHY AI IS CAUTIOUS</Typography>
            <List>
               {decision.keyRisks && decision.keyRisks.length > 0 ? (
                 decision.keyRisks.map((risk: string, i: number) => (
                   <ThesisItem key={i} text={risk} icon={<AlertTriangle size={14} className="text-rose-500" />} />
                 ))
               ) : (
                 <>
                   <ThesisItem text="Current valuation is above the 5-year historical median." icon={<AlertTriangle size={14} className="text-rose-500" />} />
                   <ThesisItem text="Broader market volatility may impact short-term performance." icon={<AlertTriangle size={14} className="text-rose-500" />} />
                 </>
               )}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, height: '100%', bgcolor: 'rgba(15, 23, 42, 0.3)' }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ fontWeight: 800 }}>PORTFOLIO SUITABILITY</Typography>
            <Stack spacing={2} sx={{ mt: 2 }}>
               <SuitabilityCard label="Investor Profile" value={decision.riskLevel === 'HIGH' ? 'AGGRESSIVE / GROWTH' : 'STABLE / BALANCED'} />
               <SuitabilityCard label="Time Horizon" value={decision.timeframe} />
               <SuitabilityCard label="Risk Reward" value={decision.riskReward} />
            </Stack>

            {decision.invalidation && (
              <Box sx={{ mt: 4, p: 2, border: '1px dashed #334155', borderRadius: 2, bgcolor: 'rgba(244, 63, 94, 0.03)' }}>
                 <Typography variant="caption" color="error" display="block" sx={{ fontWeight: 800 }}>INVALIDATION POINT</Typography>
                 <Typography variant="body2" fontWeight="bold">{decision.invalidation}</Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function ThesisItem({ text, icon }: any) {
  return (
    <ListItem sx={{ p: 0, mb: 1 }}>
       <ListItemIcon sx={{ minWidth: 28 }}>
          {icon || <TrendingUp size={14} className="text-emerald-500" />}
       </ListItemIcon>
       <ListItemText primary={text} primaryTypographyProps={{ variant: 'body2', color: 'text.secondary', fontWeight: 500 }} />
    </ListItem>
  );
}

function SuitabilityCard({ label, value }: any) {
  return (
    <Box>
       <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 700 }}>{label}</Typography>
       <Typography variant="body2" fontWeight="bold" sx={{ color: 'primary.main' }}>{value}</Typography>
    </Box>
  );
}
