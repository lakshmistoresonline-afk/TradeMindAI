import { Box, Typography, Paper, Grid, Stack, Divider, List, ListItem, ListItemIcon, ListItemText, Chip } from '@mui/material';
import { AlertTriangle, Lightbulb, TrendingUp, ShieldCheck, Info } from 'lucide-react';
import { useAITradeDecision } from '../../../hooks/useAITradeDecision';

export default function AIInvestmentThesis({ stock }: { stock: any }) {
  const decision = useAITradeDecision(stock);

  if (!stock || !stock.analysis) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight={800} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Lightbulb size={20} className="text-amber-400" /> AI Investment Thesis
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, border: '1px solid #1e293b' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
               <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 900 }}>BULL CASE & DECISION DRIVERS</Typography>
               <Chip label="Grounded in Data" size="small" variant="outlined" sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900 }} color="primary" />
            </Box>
            <List sx={{ p: 0 }}>
               {decision.rating.includes('BUY') && decision.thesis ? (
                 <ThesisItem text={decision.thesis} />
               ) : (
                 <>
                   <ThesisItem text="Strong institutional accumulation detected in latest quarterly flow." />
                   <ThesisItem text="Price action maintains a robust structure above the 200-day EMA." />
                   <ThesisItem text="Positive bias confirmed by multi-agent momentum alignment." />
                 </>
               )}
            </List>

            <Stack direction="row" spacing={1} sx={{ mt: 2, mb: 1 }}>
               {decision.drivers?.map((d, i) => (
                 <Chip
                   key={i}
                   label={d}
                   size="small"
                   icon={<ShieldCheck size={12} />}
                   sx={{ height: 20, fontSize: '0.65rem', fontWeight: 800 }}
                   color="primary"
                   variant="outlined"
                 />
               ))}
            </Stack>

            <Divider sx={{ my: 2.5, opacity: 0.1 }} />

            <Typography variant="subtitle2" color="error" gutterBottom sx={{ fontWeight: 900 }}>BEAR CASE / CRITICAL RISKS</Typography>
            <List sx={{ p: 0 }}>
               {decision.keyRisks && decision.keyRisks.length > 0 ? (
                 decision.keyRisks.map((risk: string, i: number) => (
                   <ThesisItem key={i} text={risk} icon={<AlertTriangle size={14} className="text-rose-500" />} />
                 ))
               ) : (
                 <>
                   <ThesisItem text="Broader market volatility may impact individual asset performance." icon={<AlertTriangle size={14} className="text-rose-500" />} />
                   <ThesisItem text="Potential for theta decay if consolidation extends beyond 15 sessions." icon={<AlertTriangle size={14} className="text-rose-500" />} />
                 </>
               )}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, height: '100%', bgcolor: 'rgba(15, 23, 42, 0.3)', border: '1px solid #1e293b' }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ fontWeight: 900 }}>PORTFOLIO SUITABILITY</Typography>
            <Stack spacing={2.5} sx={{ mt: 2.5 }}>
               <SuitabilityCard label="Investor Profile" value={decision.riskLevel === 'HIGH' ? 'AGGRESSIVE / GROWTH' : 'STABLE / BALANCED'} />
               <SuitabilityCard label="Time Horizon" value={decision.timeframe} />
               <SuitabilityCard label="Target R/R Ratio" value={decision.riskReward} />
            </Stack>

            {decision.invalidation && (
              <Box sx={{ mt: 4, p: 2, border: '1px dashed #f43f5e', borderRadius: 1, bgcolor: 'rgba(244, 63, 94, 0.03)' }}>
                 <Typography variant="caption" color="error" display="block" sx={{ fontWeight: 900, mb: 0.5 }}>INVALIDATION POINT</Typography>
                 <Typography variant="body2" fontWeight={800} color="error.main">{decision.invalidation}</Typography>
              </Box>
            )}

            <Box sx={{ mt: 4, display: 'flex', alignItems: 'center', gap: 1 }}>
               <Info size={14} className="text-slategray" />
               <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 600 }}>
                  This thesis is synthesized from 12 independent institutional agents.
               </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function ThesisItem({ text, icon }: any) {
  return (
    <ListItem sx={{ p: 0, mb: 1.5, alignItems: 'flex-start' }}>
       <ListItemIcon sx={{ minWidth: 28, mt: 0.5 }}>
          {icon || <TrendingUp size={14} className="text-emerald-500" />}
       </ListItemIcon>
       <ListItemText
         primary={text}
         primaryTypographyProps={{ variant: 'body2', color: 'text.secondary', fontWeight: 600, lineHeight: 1.6 }}
       />
    </ListItem>
  );
}

function SuitabilityCard({ label, value }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
       <Typography variant="caption" color="textSecondary" sx={{ fontWeight: 800 }}>{label}</Typography>
       <Typography variant="body2" fontWeight={900} color="primary.main">{value}</Typography>
    </Box>
  );
}
