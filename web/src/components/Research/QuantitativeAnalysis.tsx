import { Box, Typography, Paper, Grid, Tooltip } from '@mui/material';
import { BarChart3, Info, TrendingUp, ShieldAlert } from 'lucide-react';

export default function QuantitativeAnalysis({ metrics }: { metrics: any }) {
  if (!metrics) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <BarChart3 size={20} className="text-blue-400" /> Quantitative Risk Metrics
      </Typography>

      <Grid container spacing={2}>
        <MetricBox
          label="Sharpe Ratio"
          value={metrics.sharpe_ratio?.toFixed(2)}
          desc="Risk-adjusted return vs Risk-free rate. > 1.0 is good."
          icon={<TrendingUp size={16} />}
        />
        <MetricBox
          label="Sortino Ratio"
          value={metrics.sortino_ratio?.toFixed(2)}
          desc="Risk-adjusted return focusing on downside volatility."
          icon={<TrendingUp size={16} />}
        />
        <MetricBox
          label="Alpha (Annual)"
          value={`${(metrics.alpha * 100).toFixed(1)}%`}
          desc="Excess return relative to the Nifty 100 benchmark."
          icon={<TrendingUp size={16} />}
        />
        <MetricBox
          label="Beta (1Y)"
          value={metrics.beta?.toFixed(2)}
          desc="Volatility relative to the market. 1.0 = moves with market."
          icon={<ShieldAlert size={16} />}
        />
        <MetricBox
          label="Max Drawdown"
          value={`${(metrics.max_drawdown * 100).toFixed(1)}%`}
          desc="The largest peak-to-trough decline in price."
          icon={<ShieldAlert size={16} />}
        />
        <MetricBox
          label="Annual Volatility"
          value={`${(metrics.volatility * 100).toFixed(1)}%`}
          desc="The annualized standard deviation of daily returns."
          icon={<Info size={16} />}
        />
      </Grid>
    </Box>
  );
}

function MetricBox({ label, value, desc }: any) {
  return (
    <Grid item xs={6} md={2}>
      <Paper sx={{ p: 2, textAlign: 'center', height: '100%', border: '1px solid #334155' }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 0.5, color: 'text.secondary', mb: 1 }}>
           <Typography variant="caption" fontWeight="bold" sx={{ textTransform: 'uppercase' }}>{label}</Typography>
           <Tooltip title={desc}><Info size={12} cursor="help" /></Tooltip>
        </Box>
        <Typography variant="h6" fontWeight="bold">{value || '---'}</Typography>
      </Paper>
    </Grid>
  );
}
