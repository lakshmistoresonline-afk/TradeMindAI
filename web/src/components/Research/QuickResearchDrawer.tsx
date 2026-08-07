import { Box, Typography, Drawer, IconButton, Divider, Stack, Chip, Button, Paper } from '@mui/material';
import { X, ExternalLink, Zap, Target, ShieldCheck, TrendingUp, TrendingDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface QuickResearchDrawerProps {
  open: boolean;
  onClose: () => void;
  stock: any;
}

export default function QuickResearchDrawer({ open, onClose, stock }: QuickResearchDrawerProps) {
  const navigate = useNavigate();

  if (!stock) return null;

  const analysis = stock.analysis || {};
  const structured = stock.structured_consensus || {};
  const rating = structured.rating || (analysis.consensus?.includes('BUY') ? 'BUY' : analysis.consensus?.includes('SELL') ? 'SELL' : 'HOLD');
  const conviction = structured.conviction || stock.ai_investment_score || 0;
  const isBullish = rating.includes('BUY');
  const isBearish = rating.includes('SELL');

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: { width: { xs: '100%', sm: 400 }, bgcolor: '#0f172a', borderLeft: '1px solid #1e293b' }
      }}
    >
      <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight={800}>Quick Research</Typography>
          <IconButton onClick={onClose} size="small" sx={{ color: 'text.secondary' }}>
            <X size={20} />
          </IconButton>
        </Box>

        <Divider sx={{ mb: 3, opacity: 0.1 }} />

        <Box sx={{ mb: 4 }}>
           <Typography variant="h4" fontWeight={900}>{stock.symbol}</Typography>
           <Typography variant="body2" color="textSecondary">{stock.name}</Typography>

           <Stack direction="row" spacing={2} sx={{ mt: 2 }} alignItems="center">
              <Typography variant="h5" fontWeight={700}>₹{stock.last_price?.toLocaleString()}</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: stock.change_pct >= 0 ? 'primary.main' : 'error.main' }}>
                 {stock.change_pct >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                 <Typography variant="body2" fontWeight="bold">{stock.change_pct?.toFixed(2)}%</Typography>
              </Box>
           </Stack>
        </Box>

        <Paper sx={{ p: 3, mb: 4, bgcolor: isBullish ? 'rgba(16, 185, 129, 0.05)' : isBearish ? 'rgba(244, 63, 94, 0.05)' : 'rgba(255,255,255,0.02)', border: '1px solid #334155' }}>
           <Typography variant="caption" color="textSecondary" fontWeight={700}>AI RATING</Typography>
           <Typography variant="h3" fontWeight={900} color={isBullish ? 'primary.main' : isBearish ? 'error.main' : 'warning.main'} sx={{ my: 1 }}>
              {rating}
           </Typography>
           <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="caption" fontWeight={700}>{conviction}% CONVICTION</Typography>
              <Chip label="12 Agents Active" size="small" sx={{ height: 16, fontSize: '0.6rem', bgcolor: 'rgba(255,255,255,0.05)' }} />
           </Box>
        </Paper>

        <Stack spacing={3} sx={{ flexGrow: 1 }}>
           <QuickStat icon={<Target size={16} />} label="PRICE TARGET" value={`₹${structured.target?.toLocaleString() || '---'}`} color="primary.main" />
           <QuickStat icon={<ShieldCheck size={16} />} label="STOP LOSS" value={`₹${structured.stop_loss?.toLocaleString() || '---'}`} color="error.main" />
           <QuickStat icon={<Zap size={16} />} label="ENTRY ZONE" value={`₹${stock.last_price?.toLocaleString()}`} color="info.main" />

           <Box>
              <Typography variant="caption" color="textSecondary" fontWeight={700}>AI THESIS SUMMARY</Typography>
              <Typography variant="body2" sx={{ mt: 1, lineHeight: 1.6, color: 'text.secondary' }}>
                 {structured.thesis?.substring(0, 150) || analysis.consensus?.substring(0, 150)}...
              </Typography>
           </Box>
        </Stack>

        <Button
          fullWidth
          variant="contained"
          onClick={() => {
            onClose();
            navigate('/analysis', { state: { symbol: stock.symbol } });
          }}
          startIcon={<ExternalLink size={18} />}
          sx={{ mt: 4, py: 1.5, fontWeight: 800 }}
        >
          Open Full Forensic Lab
        </Button>
      </Box>
    </Drawer>
  );
}

function QuickStat({ icon, label, value, color }: any) {
  return (
    <Box>
       <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 700 }}>
          {icon} {label}
       </Typography>
       <Typography variant="h6" fontWeight={800} sx={{ color }}>{value}</Typography>
    </Box>
  );
}
