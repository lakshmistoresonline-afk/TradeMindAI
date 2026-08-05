import { useState } from 'react';
import { Box, Typography, Paper, Grid, Button, Stack, Chip, Divider } from '@mui/material';
import { ShieldAlert, Zap, Globe, DollarSign, CloudLightning } from 'lucide-react';

export default function ScenarioSimulator() {
  const [activeScenario, setActiveScenario] = useState<string | null>(null);

  const scenarios = [
    { id: 'nifty_crash', name: 'Nifty -10% Crash', icon: <CloudLightning size={16} />, impact: 'EXTREME', color: '#f43f5e' },
    { id: 'oil_spike', name: 'Oil +20% Spike', icon: <Zap size={16} />, impact: 'HIGH', color: '#fbbf24' },
    { id: 'rate_hike', name: 'RBI +50bps Hike', icon: <DollarSign size={16} />, impact: 'MEDIUM', color: '#3b82f6' },
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Globe size={20} className="text-blue-500" /> AI Scenario Simulator
      </Typography>

      <Paper sx={{ p: 4 }}>
         <Typography variant="body2" color="textSecondary" sx={{ mb: 4 }}>
            Test your investment thesis against hypothetical macro shocks.
         </Typography>

         <Grid container spacing={3}>
            {scenarios.map((s) => (
              <Grid item xs={12} md={4} key={s.id}>
                 <Paper
                  onClick={() => setActiveScenario(s.id)}
                  sx={{
                    p: 3, cursor: 'pointer',
                    border: activeScenario === s.id ? `1px solid ${s.color}` : '1px solid #334155',
                    bgcolor: activeScenario === s.id ? `${s.color}05` : 'transparent',
                    '&:hover': { bgcolor: 'rgba(255,255,255,0.02)' }
                  }}
                 >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                       <Box sx={{ color: s.color }}>{s.icon}</Box>
                       <Typography variant="subtitle2" fontWeight="bold">{s.name}</Typography>
                    </Box>
                    <Chip label={s.impact} size="small" sx={{ height: 18, fontSize: '0.6rem', bgcolor: `${s.color}20`, color: s.color, fontWeight: 'bold' }} />
                 </Paper>
              </Grid>
            ))}
         </Grid>

         {activeScenario && (
           <Box sx={{ mt: 6, p: 3, bgcolor: 'rgba(15, 23, 42, 0.5)', borderRadius: 2, borderLeft: `4px solid ${scenarios.find(s => s.id === activeScenario)?.color}` }}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>PROJECTION FOR {scenarios.find(s => s.id === activeScenario)?.name.toUpperCase()}</Typography>
              <Typography variant="body2" sx={{ lineHeight: 1.7, color: 'text.secondary' }}>
                 Under this scenario, the stock is projected to see a **-8.4% correction** due to high correlation with the macro variable.
                 Institutional models suggest reducing exposure by 15% and hedging with sector-specific puts.
                 Recovery timeline is estimated at **4 - 6 weeks**.
              </Typography>
           </Box>
         )}
      </Paper>
    </Box>
  );
}
