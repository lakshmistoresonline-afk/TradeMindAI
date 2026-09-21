import { Box, Typography, Stack, Divider } from '@mui/material';

export default function Terms() {
  return (
    <Box sx={{ pb: 10, maxWidth: 900, mx: 'auto', p: 4, color: 'white' }}>
      <Box sx={{ mb: 8, textAlign: 'center' }}>
        <Typography variant="h3" sx={{ fontWeight: 950, letterSpacing: -2, mb: 2 }}>TERMS OF SERVICE</Typography>
        <Typography variant="h6" sx={{ color: '#00D1FF', fontWeight: 800 }}>LEGAL OPERATING FRAMEWORK</Typography>
      </Box>

      <Stack spacing={4}>
         <section>
            <Typography variant="h6" sx={{ fontWeight: 900, mb: 2 }}>1. Acceptance of Terms</Typography>
            <Typography sx={{ color: '#708090', lineHeight: 1.8 }}>
               By accessing the TradeMind AI terminal, you agree to be bound by these Terms of Service and all
               applicable laws and regulations in the Republic of India.
            </Typography>
         </section>

         <section>
            <Typography variant="h6" sx={{ fontWeight: 900, mb: 2 }}>2. Use License</Typography>
            <Typography sx={{ color: '#708090', lineHeight: 1.8 }}>
               Permission is granted to temporarily access the materials on TradeMind AI for personal,
               non-commercial transitory viewing only. This is the grant of a license, not a transfer of title.
            </Typography>
         </section>

         <section>
            <Typography variant="h6" sx={{ fontWeight: 900, mb: 2 }}>3. Limitation of Liability</Typography>
            <Typography sx={{ color: '#708090', lineHeight: 1.8 }}>
               TradeMind AI or its suppliers shall not be held liable for any damages (including, without limitation,
               damages for loss of data or profit, or due to business interruption) arising out of the use or
               inability to use the materials on TradeMind AI.
            </Typography>
         </section>

         <Divider sx={{ opacity: 0.1 }} />
         <Typography variant="caption" sx={{ color: '#708090', textAlign: 'center' }}>
            © 2026 TradeMind AI • Institutional Signal Intelligence
         </Typography>
      </Stack>
    </Box>
  );
}
