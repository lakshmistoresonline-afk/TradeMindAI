import { Box, Typography, Paper, Grid, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import { CheckCircle2, XCircle, HelpCircle, Info } from 'lucide-react';

export default function WhyWhyNot({ analysis }: { analysis: any }) {
  if (!analysis) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <HelpCircle size={20} className="text-emerald-500" /> Why / Why Not Engine
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, borderTop: '4px solid #10b981' }}>
            <Typography variant="subtitle1" fontWeight="bold" color="primary" gutterBottom>Reasons to Buy / Hold</Typography>
            <List dense>
              <ListItem sx={{ p: 0, mb: 1.5 }}>
                <ListItemIcon sx={{ minWidth: 32 }}><CheckCircle2 size={18} className="text-emerald-500" /></ListItemIcon>
                <ListItemText
                  primary="Bullish SMC Alignment"
                  secondary="Price is currently reacting off a primary institutional order block."
                  primaryTypographyProps={{ fontWeight: 'bold' }}
                />
              </ListItem>
              <ListItem sx={{ p: 0, mb: 1.5 }}>
                <ListItemIcon sx={{ minWidth: 32 }}><CheckCircle2 size={18} className="text-emerald-500" /></ListItemIcon>
                <ListItemText
                  primary="Strong Relative Strength"
                  secondary="Stock is outperforming the Nifty 100 by 4.2% over the last 30 days."
                  primaryTypographyProps={{ fontWeight: 'bold' }}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, borderTop: '4px solid #f43f5e' }}>
            <Typography variant="subtitle1" fontWeight="bold" color="error" gutterBottom>Reasons for Caution</Typography>
            <List dense>
              <ListItem sx={{ p: 0, mb: 1.5 }}>
                <ListItemIcon sx={{ minWidth: 32 }}><XCircle size={18} className="text-rose-500" /></ListItemIcon>
                <ListItemText
                  primary="Valuation Headwinds"
                  secondary="P/E ratio is at the 90th percentile of its 5-year historical range."
                  primaryTypographyProps={{ fontWeight: 'bold' }}
                />
              </ListItem>
              <ListItem sx={{ p: 0, mb: 1.5 }}>
                <ListItemIcon sx={{ minWidth: 32 }}><Info size={18} className="text-amber-500" /></ListItemIcon>
                <ListItemText
                  primary="Sector Consolidation"
                  secondary="The broader sector index is facing resistance at psychological levels."
                  primaryTypographyProps={{ fontWeight: 'bold' }}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
