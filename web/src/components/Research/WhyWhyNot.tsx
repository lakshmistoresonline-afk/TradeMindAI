import { Box, Typography, Paper, Grid, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import { CheckCircle2, XCircle, HelpCircle } from 'lucide-react';

export default function WhyWhyNot({ analysis }: { analysis: any }) {
  if (!analysis || !analysis.recommendations) return null;

  const buyReasons = analysis.recommendations
    .filter((r: any) => r.signal === 'BUY')
    .flatMap((r: any) => r.reasons)
    .slice(0, 4);

  const cautionReasons = analysis.recommendations
    .filter((r: any) => r.signal === 'SELL' || r.signal === 'HOLD')
    .flatMap((r: any) => r.risks || r.reasons)
    .slice(0, 4);

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <HelpCircle size={20} className="text-emerald-500" /> AI Why / Why Not Engine
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, borderTop: '4px solid #10b981', height: '100%' }}>
            <Typography variant="subtitle1" fontWeight="bold" color="primary" gutterBottom>Reasons to Buy / Hold</Typography>
            <List dense>
              {buyReasons.map((reason: string, i: number) => (
                <ListItem key={i} sx={{ p: 0, mb: 1.5 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}><CheckCircle2 size={18} className="text-emerald-500" /></ListItemIcon>
                  <ListItemText
                    primary={reason}
                    primaryTypographyProps={{ variant: 'body2', fontWeight: 'bold' }}
                  />
                </ListItem>
              ))}
              {buyReasons.length === 0 && <Typography variant="body2" color="textSecondary">No strong bullish factors identified.</Typography>}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, borderTop: '4px solid #f43f5e', height: '100%' }}>
            <Typography variant="subtitle1" fontWeight="bold" color="error" gutterBottom>Reasons for Caution / Risks</Typography>
            <List dense>
              {cautionReasons.map((reason: string, i: number) => (
                <ListItem key={i} sx={{ p: 0, mb: 1.5 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}><XCircle size={18} className="text-rose-500" /></ListItemIcon>
                  <ListItemText
                    primary={reason}
                    primaryTypographyProps={{ variant: 'body2', fontWeight: 'bold' }}
                  />
                </ListItem>
              ))}
              {cautionReasons.length === 0 && <Typography variant="body2" color="textSecondary">No significant risks identified.</Typography>}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
