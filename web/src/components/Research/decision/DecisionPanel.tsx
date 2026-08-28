import { Box, Typography, Paper, Grid, Chip, Divider, Stack, LinearProgress, Tooltip } from '@mui/material';
import { ShieldCheck, AlertTriangle, Zap, Target, Clock, Info, Shield, Calendar, Database } from 'lucide-react';
import { useAITradeDecision } from '../../../hooks/useAITradeDecision';

export default function DecisionPanel({ stock }: { stock: any }) {
  const decision = useAITradeDecision(stock);

  if (!stock || !stock.analysis) return null;

  const isBullish = decision.rating.includes('BUY');
  const isBearish = decision.rating.includes('SELL');

  return (
    <Paper
      elevation={4}
      sx={{
        p: 0,
        mb: 4,
        overflow: 'hidden',
        border: '1px solid #1e293b',
        bgcolor: '#0f172a',
        borderRadius: 2
      }}
    >
      <Grid container>
        {/* Rating & Conviction */}
        <Grid item xs={12} md={4} sx={{ p: 3, bgcolor: isBullish ? 'rgba(16, 185, 129, 0.08)' : isBearish ? 'rgba(244, 63, 94, 0.08)' : 'rgba(255,255,255,0.03)', borderRight: '1px solid #1e293b' }}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
             <Box>
                <Typography variant="subtitle2" color="textSecondary">AI TRADE DECISION</Typography>
                <Chip label={decision.status} size="small" variant="outlined" sx={{ height: 16, fontSize: '0.55rem', fontWeight: 900, mt: 0.5 }} color={decision.status === 'ACTIVE' ? 'primary' : 'default'} />
             </Box>
             <Tooltip title="Confidence level based on multi-agent alignment.">
                <Chip
                  label={`${decision.conviction}% CONVICTION`}
                  size="small"
                  sx={{ height: 18, fontSize: '0.65rem', fontWeight: 800, bgcolor: isBullish ? '#10b981' : isBearish ? '#f43f5e' : '#334155', color: '#000' }}
                />
             </Tooltip>
          </Stack>

          <Typography variant="h2" sx={{ fontWeight: 900, color: isBullish ? '#10b981' : isBearish ? '#f43f5e' : '#fbbf24', my: 1.5, fontSize: { xs: '2.5rem', md: '3.5rem' } }}>
            {decision.rating}
          </Typography>

          <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
             <Box>
                <Typography variant="caption" color="textSecondary" display="block">RISK LEVEL</Typography>
                <Typography variant="subtitle2" sx={{ color: decision.riskLevel === 'HIGH' ? '#f43f5e' : decision.riskLevel === 'MODERATE' ? '#fbbf24' : '#10b981', fontWeight: 800 }}>{decision.riskLevel}</Typography>
             </Box>
             <Box>
                <Typography variant="caption" color="textSecondary" display="block">TIME HORIZON</Typography>
                <Typography variant="subtitle2" sx={{ fontWeight: 800, color: 'primary.main' }}>{decision.timeframe}</Typography>
             </Box>
          </Stack>

          <Box sx={{ mt: 3 }}>
            <LinearProgress
              variant="determinate"
              value={decision.conviction}
              color={isBullish ? 'primary' : isBearish ? 'error' : 'warning'}
              sx={{ height: 6, borderRadius: 5, bgcolor: 'rgba(255,255,255,0.05)' }}
            />
          </Box>

          <Box sx={{ mt: 4, pt: 2, borderTop: '1px solid rgba(255,255,255,0.05)' }}>
             <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontSize: '0.65rem' }}>
                <Database size={10} /> Model: {decision.modelVersion}
             </Typography>
             <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontSize: '0.65rem', mt: 0.5 }}>
                <Calendar size={10} /> Data: {decision.updatedAt ? new Date(decision.updatedAt).toLocaleString() : 'LIVE'}
             </Typography>
          </Box>
        </Grid>

        {/* Execution & Thesis */}
        <Grid item xs={12} md={8} sx={{ p: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={6} sm={3}>
              {decision.entryLow && decision.entryHigh ? (
                <DecisionStat icon={<Zap size={14} />} label="ENTRY ZONE" value={`₹${decision.entryLow.toLocaleString()} - ₹${decision.entryHigh.toLocaleString()}`} color="#3b82f6" />
              ) : (
                <DecisionStat icon={<Zap size={14} />} label="ENTRY" value={`₹${decision.entry?.toLocaleString()}`} color="#3b82f6" />
              )}
            </Grid>
            <Grid item xs={6} sm={3}>
              <DecisionStat icon={<Target size={14} />} label="TARGET" value={decision.target ? `₹${decision.target.toLocaleString()}` : '---'} color="#10b981" />
            </Grid>
            <Grid item xs={6} sm={3}>
              <DecisionStat icon={<Shield size={14} />} label="STOP LOSS" value={decision.stopLoss ? `₹${decision.stopLoss.toLocaleString()}` : '---'} color="#f43f5e" />
            </Grid>
            <Grid item xs={6} sm={3}>
              <DecisionStat icon={<Clock size={14} />} label="R / R RATIO" value={decision.riskReward || '1:2.0'} color="#fff" />
            </Grid>
          </Grid>

          <Divider sx={{ my: 2, opacity: 0.1 }} />

          <Box sx={{ mb: 2 }}>
             <Typography variant="subtitle2" color="textSecondary" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                AI EXPLAINABILITY <Chip label="AI GENERATED" size="small" sx={{ height: 14, fontSize: '0.5rem', fontWeight: 900 }} />
             </Typography>
             <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.6 }}>
                {decision.thesis}
             </Typography>
             {decision.drivers && decision.drivers.length > 0 && (
               <Stack direction="row" spacing={1} sx={{ mt: 1.5 }}>
                  {decision.drivers.map((d, i) => (
                    <Chip key={i} label={d} size="small" variant="filled" sx={{ height: 20, fontSize: '0.65rem', fontWeight: 700, bgcolor: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6' }} />
                  ))}
               </Stack>
             )}
          </Box>

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
             <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', gap: 1.5, p: 1.5, bgcolor: 'rgba(16, 185, 129, 0.05)', borderRadius: 1 }}>
                <ShieldCheck size={18} className="text-emerald-500" />
                <Box>
                   <Typography variant="caption" color="textSecondary" sx={{ display: 'block', fontWeight: 700 }}>PRIMARY CATALYST</Typography>
                   <Typography variant="caption" fontWeight={600}>{decision.primaryCatalyst || 'Institutional accumulation detected.'}</Typography>
                </Box>
             </Box>
             <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', gap: 1.5, p: 1.5, bgcolor: 'rgba(244, 63, 94, 0.05)', borderRadius: 1 }}>
                <AlertTriangle size={18} className="text-rose-500" />
                <Box>
                   <Typography variant="caption" color="textSecondary" sx={{ display: 'block', fontWeight: 700 }}>KEY RISK</Typography>
                   <Typography variant="caption" fontWeight={600}>{decision.keyRisks?.[0] || 'Market volatility risk.'}</Typography>
                </Box>
             </Box>
          </Stack>
        </Grid>
      </Grid>

      <Box sx={{ px: 2, py: 1, bgcolor: 'rgba(255,255,255,0.02)', borderTop: '1px solid rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', gap: 1 }}>
         <Info size={12} className="text-slategray" />
         <Typography variant="caption" color="textSecondary">
            AI-generated analysis is informational and may be inaccurate. Validate signals independently before making trading decisions.
         </Typography>
      </Box>
    </Paper>
  );
}

function DecisionStat({ icon, label, value, color }: any) {
  return (
    <Box>
       <Typography variant="caption" color="textSecondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 800 }}>{icon} {label}</Typography>
       <Typography variant="h5" sx={{ fontWeight: 900, color: color, my: 0.5, fontFamily: 'JetBrains Mono' }}>{value}</Typography>
    </Box>
  );
}
