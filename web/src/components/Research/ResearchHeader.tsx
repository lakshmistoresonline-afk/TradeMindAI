import { Box, Typography, Grid, Paper, Chip, Divider } from '@mui/material';
import { TrendingUp, TrendingDown, Layers, Activity, DollarSign, BarChart3 } from 'lucide-react';

export default function ResearchHeader({ stock }: { stock: any }) {
  const formatCurrency = (val: number) => {
    if (!val) return '---';
    if (val >= 1e12) return `₹${(val / 1e12).toFixed(2)}T`;
    if (val >= 1e7) return `₹${(val / 1e7).toFixed(2)}Cr`;
    return `₹${val.toLocaleString()}`;
  };

  const formatPct = (val: number) => val ? `${(val * 100).toFixed(2)}%` : '---';

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight="bold">{stock.name}</Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mt: 1 }}>
            <Typography variant="h6" color="textSecondary">{stock.symbol}</Typography>
            <Chip label={stock.sector} size="small" variant="outlined" icon={<Layers size={14} />} />
            <Chip label={stock.industry} size="small" variant="outlined" />
          </Box>
        </Box>
        <Box sx={{ textAlign: 'right' }}>
          <Typography variant="h4" fontWeight="bold">₹{stock.last_price?.toLocaleString()}</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 1 }}>
            {stock.change_pct >= 0 ? <TrendingUp size={20} className="text-emerald-500" /> : <TrendingDown size={20} className="text-rose-500" />}
            <Typography variant="h6" color={stock.change_pct >= 0 ? 'primary' : 'error'} fontWeight="bold">
              {stock.change_pct?.toFixed(2)}%
            </Typography>
          </Box>
        </Box>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, bgcolor: 'rgba(15, 23, 42, 0.3)' }}>
            <Grid container spacing={3}>
              <MetricItem label="Market Cap" value={formatCurrency(stock.market_cap)} icon={<Activity size={16} />} />
              <MetricItem label="Enterprise Value" value={formatCurrency(stock.enterprise_value)} icon={<DollarSign size={16} />} />
              <MetricItem label="52W High" value={`₹${stock.high_52w?.toLocaleString()}`} />
              <MetricItem label="52W Low" value={`₹${stock.low_52w?.toLocaleString()}`} />
              <MetricItem label="P/E Ratio" value={stock.pe_ratio?.toFixed(2)} />
              <MetricItem label="P/B Ratio" value={stock.pb_ratio?.toFixed(2)} />
              <MetricItem label="Dividend Yield" value={formatPct(stock.dividend_yield)} />
              <MetricItem label="Beta" value={stock.beta?.toFixed(2)} />
            </Grid>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
           <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', bgcolor: 'rgba(16, 185, 129, 0.05)', border: '1px solid #10b981' }}>
              <Typography variant="caption" color="textSecondary" align="center" gutterBottom>AVERAGE DAILY VOLUME</Typography>
              <Typography variant="h5" fontWeight="bold" align="center">{(stock.avg_volume / 1e6).toFixed(2)}M</Typography>
              <Divider sx={{ my: 2, opacity: 0.1 }} />
              <Typography variant="caption" color="textSecondary" align="center" gutterBottom>DELIVERY PERCENTAGE</Typography>
              <Typography variant="h5" fontWeight="bold" align="center" color="primary">58.4%</Typography>
           </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function MetricItem({ label, value, icon }: any) {
  return (
    <Grid item xs={6} sm={3}>
      <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        {icon} {label}
      </Typography>
      <Typography variant="body1" fontWeight="bold">{value || '---'}</Typography>
    </Grid>
  );
}
