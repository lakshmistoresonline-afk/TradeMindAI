import { Box, Typography, Paper, Grid, Chip, List, ListItem, ListItemText, ListItemIcon, Divider } from '@mui/material';
import { Target, Zap, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function MarketStructure({ smc }: { smc: any }) {
  if (!smc) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Target size={20} className="text-amber-500" /> Institutional Market Structure (SMC/ICT)
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>ORDER BLOCKS & LIQUIDITY</Typography>
            <List>
              {smc.order_blocks && smc.order_blocks.length > 0 ? smc.order_blocks.map((ob: any, idx: number) => (
                <ListItem key={idx} sx={{ bgcolor: 'rgba(255,255,255,0.02)', mb: 1, borderRadius: 2 }}>
                  <ListItemIcon>
                    {ob.type === 'bullish' ? <ShieldCheck className="text-emerald-500" /> : <AlertTriangle className="text-rose-500" />}
                  </ListItemIcon>
                  <ListItemText
                    primary={`${ob.type.toUpperCase()} ORDER BLOCK`}
                    secondary={`Detected at index ${ob.index}. Price level showing institutional ${ob.type === 'bullish' ? 'accumulation' : 'distribution'}.`}
                  />
                  <Chip label="ACTIVE" size="small" color="primary" variant="outlined" />
                </ListItem>
              )) : <Typography variant="body2" color="textSecondary">No primary order blocks detected in current range.</Typography>}

              {smc.fvgs && smc.fvgs.map((fvg: any, idx: number) => (
                <ListItem key={`fvg-${idx}`} sx={{ bgcolor: 'rgba(255,255,255,0.02)', mb: 1, borderRadius: 2 }}>
                  <ListItemIcon>
                    <Zap className="text-blue-400" />
                  </ListItemIcon>
                  <ListItemText
                    primary={`FAIR VALUE GAP (${fvg.type.toUpperCase()})`}
                    secondary="Imbalance detected in institutional delivery. Price likely to revisit."
                  />
                  <Chip label="IMBALANCE" size="small" variant="outlined" />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>MARKET PHASE (WYCKOFF)</Typography>
            <Box sx={{ mt: 2, textAlign: 'center', p: 4, border: '1px dashed #334155', borderRadius: 4 }}>
                <Typography variant="h5" color="primary" fontWeight="bold">{(smc.wyckoff || 'SIDEWAYS').toUpperCase()}</Typography>
                <Typography variant="caption" color="textSecondary">Institutional Bias detection</Typography>
                <Box sx={{ mt: 3, display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap' }}>
                   <Chip label="Volume Depth Analyzed" size="small" />
                   <Chip label="Cycle Alignment" size="small" />
                </Box>
            </Box>
            <Divider sx={{ my: 3, opacity: 0.1 }} />
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>ELLIOTT WAVE COUNT</Typography>
            <Typography variant="h6" fontWeight="bold">{smc.elliott || 'Wave 3 (Impulse)'}</Typography>
            <Typography variant="body2" color="textSecondary">
               {smc.elliott?.includes('3') ? 'The strongest part of the trend. High conviction long entries supported by wave structure.' : 'Corrective or transitional structure detected.'}
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
