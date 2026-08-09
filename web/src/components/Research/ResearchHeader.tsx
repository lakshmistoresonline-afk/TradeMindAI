import { Box, Typography, Grid, Paper, Chip, Divider } from '@mui/material';
import { TrendingUp, TrendingDown, Layers, Activity, DollarSign, Clock } from 'lucide-react';

export default function ResearchHeader({ stock }: { stock: any }) {
  const formatCurrency = (val: number) => {
    if (!val) return '---';
    if (val >= 1e12) return `₹${(val / 1e12).toFixed(2)}T`;
    if (val >= 1e7) return `₹${(val / 1e7).toFixed(2)} Cr`;
    return `₹${val.toLocaleString()}`;
  };

  const formatPct = (val: number) => val ? `${(val * 100).toFixed(2)}%` : '---';

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: { xs: 'flex-start', sm: 'center' }, mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight={900} sx={{ fontSize: { xs: '1.8rem', sm: '2.5rem' }, letterSpacing: -1 }}>{stock.name}</Typography>
          <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center', mt: 1, flexWrap: 'wrap' }}>
            <Typography variant="h6" color="textSecondary" sx={{ fontWeight: 800, fontFamily: 'JetBrains Mono' }}>{stock.symbol}</Typography>
            <Chip label={stock.sector} size="small" variant="outlined" icon={<Layers size={14} />} sx={{ fontWeight: 700 }} />
            <Chip label={stock.industry} size="small" variant="outlined" sx={{ fontWeight: 700 }} />
            <Chip label="LIVE" size="small" color="primary" sx={{ height: 20, fontSize: '0.6rem', fontWeight: 900 }} />
          </Box>
        </Box>
        <Box sx={{ textAlign: { xs: 'left', sm: 'right' }, width: { xs: '100%', sm: 'auto' } }}>
          <Typography variant="h3" fontWeight={900} sx={{ fontSize: { xs: '2rem', sm: '3rem' }, fontFamily: 'JetBrains Mono' }}>₹{stock.last_price?.toLocaleString()}</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: { xs: 'flex-start', sm: 'flex-end' }, gap: 1 }}>
            {stock.change_pct >= 0 ? <TrendingUp size={24} className="text-emerald-500" /> : <TrendingDown size={24} className="text-rose-500" />}
            <Typography variant="h5" color={stock.change_pct >= 0 ? 'primary' : 'error'} fontWeight={900}>
              {(stock.change_pct || 0) >= 0 ? '+' : ''}{stock.change_pct?.toFixed(2)}%
            </Typography>
          </Box>
          <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', justifyContent: { xs: 'flex-start', sm: 'flex-end' }, gap: 0.5, mt: 1, fontWeight: 700 }}>
             <Clock size={12} /> {stock.updated_at ? new Date(stock.updated_at).toLocaleString() : '---'}
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, bgcolor: 'rgba(15, 23, 42, 0.3)', border: '1px solid #1e293b' }}>
            <Grid container spacing={3}>
              <MetricItem label="Market Cap" value={formatCurrency(stock.market_cap)} icon={<Activity size={16} />} />
              <MetricItem label="Enterprise Value" value={formatCurrency(stock.enterprise_value)} icon={<DollarSign size={16} />} />
              <MetricItem label="52W High" value={`₹${stock.high_52w?.toLocaleString()}`} />
              <MetricItem label="52W Low" value={`₹${stock.low_52w?.toLocaleString()}`} />
              <MetricItem label="P/E Ratio" value={stock.pe_ratio?.toFixed(2)} />
              <MetricItem label="P/B Ratio" value={stock.pb_ratio?.toFixed(2)} />
              <MetricItem label="Div. Yield" value={formatPct(stock.dividend_yield)} />
              <MetricItem label="Beta (1Y)" value={stock.beta?.toFixed(2)} />
            </Grid>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
           <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', bgcolor: 'rgba(16, 185, 129, 0.05)', border: '1px solid #10b981' }}>
              <Typography variant="caption" color="textSecondary" align="center" gutterBottom sx={{ fontWeight: 800 }}>AVERAGE DAILY VOLUME</Typography>
              <Typography variant="h5" fontWeight={900} align="center">{(stock.avg_volume / 1e6).toFixed(2)}M</Typography>
              <Divider sx={{ my: 2, opacity: 0.1 }} />
              <Typography variant="caption" color="textSecondary" align="center" gutterBottom sx={{ fontWeight: 800 }}>DELIVERY PERCENTAGE</Typography>
              <Typography variant="h5" fontWeight={900} align="center" color="primary">
                 {stock.delivery_pct ? `${stock.delivery_pct.toFixed(1)}%` : '---'}
              </Typography>
           </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function MetricItem({ label, value, icon }: any) {
  return (
    <Grid item xs={6} sm={3}>
      <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 700 }}>
        {icon} {label.toUpperCase()}
      </Typography>
      <Typography variant="body1" fontWeight={800} sx={{ fontFamily: 'JetBrains Mono' }}>{value || '---'}</Typography>
    </Grid>
  );
}
