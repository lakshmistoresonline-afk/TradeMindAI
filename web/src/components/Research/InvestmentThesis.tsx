import { Box, Typography, Paper, Grid, Stack, Divider, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import { AlertTriangle, Lightbulb, TrendingUp } from 'lucide-react';

export default function InvestmentThesis({ analysis }: any) {
  if (!analysis) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Lightbulb size={20} className="text-amber-400" /> Investment Thesis
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle2" color="primary" gutterBottom>THE BULL CASE</Typography>
            <List>
               <ThesisItem text="Strong institutional accumulation detected in latest quarterly flow." />
               <ThesisItem text="Price broke out of a 6-month Wyckoff accumulation base with high volume." />
               <ThesisItem text="ML models predict a 72% probability of a 5% move in 10 trading days." />
            </List>

            <Divider sx={{ my: 2, opacity: 0.05 }} />

            <Typography variant="subtitle2" color="error" gutterBottom>THE BEAR CASE / RISKS</Typography>
            <List>
               <ThesisItem text="Current valuation (P/E 34x) is 15% above the 5-year historical median." icon={<AlertTriangle size={14} className="text-rose-500" />} />
               <ThesisItem text="Rising input costs may impact operating margins in the next two quarters." icon={<AlertTriangle size={14} className="text-rose-500" />} />
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, height: '100%', bgcolor: 'rgba(15, 23, 42, 0.3)' }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>PORTFOLIO SUITABILITY</Typography>
            <Stack spacing={2} sx={{ mt: 2 }}>
               <SuitabilityCard label="Investor Profile" value="AGGRESSIVE / GROWTH" />
               <SuitabilityCard label="Holding Horizon" value="6 - 18 MONTHS" />
               <SuitabilityCard label="Strategy Alignment" value="MOMENTUM & QUALITY" />
            </Stack>

            <Box sx={{ mt: 4, p: 2, border: '1px dashed #334155', borderRadius: 2 }}>
               <Typography variant="caption" color="textSecondary" display="block">INVALIDATION POINT</Typography>
               <Typography variant="body2" fontWeight="bold">Thesis fails if price closes below ₹2,340 on weekly timeframe.</Typography>
            </Box>
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
       <ListItemText primary={text} primaryTypographyProps={{ variant: 'body2', color: 'text.secondary' }} />
    </ListItem>
  );
}

function SuitabilityCard({ label, value }: any) {
  return (
    <Box>
       <Typography variant="caption" color="textSecondary">{label}</Typography>
       <Typography variant="body2" fontWeight="bold">{value}</Typography>
    </Box>
  );
}
