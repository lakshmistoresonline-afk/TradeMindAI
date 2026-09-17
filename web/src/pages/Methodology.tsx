import { Box, Typography, Paper, Stack, Divider, alpha } from '@mui/material';

export default function Methodology() {
  return (
    <Box sx={{ pb: 10, maxWidth: 900, mx: 'auto', p: 4 }}>
      <Box sx={{ mb: 6, textAlign: 'center' }}>
        <Typography variant="h3" sx={{ fontWeight: 950, letterSpacing: -2, color: 'white' }}>SIGNAL METHODOLOGY</Typography>
        <Typography variant="h6" sx={{ color: '#00D1FF', fontWeight: 800, mt: 1 }}>STRATEGY V2.2 CORE PROTOCOL</Typography>
      </Box>

      {/* CANONICAL DATA FLOW */}
      <Box sx={{ mb: 8, p: 4, bgcolor: '#0f172a', borderRadius: 1, border: '1px solid rgba(255,255,255,0.05)' }}>
        <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, letterSpacing: 2, display: 'block', mb: 4, textAlign: 'center' }}>DATA ARCHITECTURE</Typography>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="center" justifyContent="center" sx={{ color: 'white' }}>
            <FlowBox label="MARKET DATA" color="#00D1FF" />
            <Box sx={{ opacity: 0.2 }}>→</Box>
            <FlowBox label="FEATURES" color="#00D1FF" />
            <Box sx={{ opacity: 0.2 }}>→</Box>
            <FlowBox label="MODEL" color="#00D1FF" />
            <Box sx={{ opacity: 0.2 }}>→</Box>
            <FlowBox label="V2.2 DECISION" color="#00D1FF" />
            <Box sx={{ opacity: 0.2 }}>→</Box>
            <FlowBox label="SIGNAL" color="#10b981" />
        </Stack>
      </Box>

      <Stack spacing={6}>
         <section>
            <Typography variant="h5" sx={{ fontWeight: 900, mb: 3 }}>1. Universe Selection</Typography>
            <Typography sx={{ color: 'slategray', lineHeight: 1.8 }}>
               TradeMind AI monitors the **NIFTY-200** universe, representing the top 200 liquid constituents of the National Stock Exchange of India.
               The universe is rebalanced monthly to align with official NSE index membership updates.
            </Typography>
         </section>

         <section>
            <Typography variant="h5" sx={{ fontWeight: 900, mb: 3 }}>2. Feature Engineering</Typography>
            <Typography sx={{ color: 'slategray', lineHeight: 1.8 }}>
               Signals are derived from over 42 quantitative features, including structural indicators (SMC), institutional order flow,
               multi-timeframe volatility (ATR), and relative strength metrics. All data is processed using **DuckDB-TA** for high-fidelity technical analysis.
            </Typography>
         </section>

         <section>
            <Typography variant="h5" sx={{ fontWeight: 900, mb: 3 }}>3. AI Multi-Agent Consensus</Typography>
            <Paper sx={{ p: 4, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="body1" sx={{ color: '#fff', fontWeight: 700, mb: 2 }}>consensual decision engine</Typography>
               <Typography sx={{ color: 'slategray', lineHeight: 1.8 }}>
                  Our V2.2 model utilizes a **Platt-Scaled ensemble** architecture. A final signal is only generated when multiple agents
                  (Trend, Momentum, and Institutional) reach a combined confidence threshold of **&gt; 52%**.
               </Typography>
            </Paper>
         </section>

         <section>
            <Typography variant="h5" sx={{ fontWeight: 900, mb: 3 }}>4. Forensic Integrity</Typography>
            <Typography sx={{ color: 'slategray', lineHeight: 1.8 }}>
               TradeMind AI maintains a **Zero-Fabrication** policy. Every signal is persisted to an authoritative Neon PostgreSQL ledger
               with immutable Prediction and Provenance IDs. Historical outcomes are verified intrabar with same-candle stop-loss priority.
            </Typography>
         </section>

         <Divider sx={{ opacity: 0.05 }} />

         <Box sx={{ p: 4, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 1, border: '1px dashed rgba(255,255,255,0.1)' }}>
            <Typography variant="caption" sx={{ color: 'slategray', fontStyle: 'italic', lineHeight: 1.6, display: 'block' }}>
               **Educational Disclaimer:** TradeMind AI is a research and signal intelligence platform.
               All performance data is based on observed shadow execution. Past performance is not indicative of future results.
               No real trading is executed via this interface.
            </Typography>
         </Box>
      </Stack>
    </Box>
  );
}

function FlowBox({ label, color }: { label: string; color: string }) {
    return (
        <Box sx={{
            px: 2, py: 1,
            bgcolor: alpha(color, 0.05),
            border: `1px solid ${alpha(color, 0.2)}`,
            borderRadius: 0.5,
            width: { xs: '100%', md: 'auto' },
            textAlign: 'center'
        }}>
            <Typography variant="caption" sx={{
                fontWeight: 950,
                color: color
            }}>{label}</Typography>
        </Box>
    );
}
