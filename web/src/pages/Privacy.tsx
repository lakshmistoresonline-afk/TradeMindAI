import { Box, Typography, Stack, Divider } from '@mui/material';

export default function Privacy() {
  return (
    <Box sx={{ pb: 10, maxWidth: 900, mx: 'auto', p: 4, color: 'white' }}>
      <Box sx={{ mb: 8, textAlign: 'center' }}>
        <Typography variant="h3" sx={{ fontWeight: 950, letterSpacing: -2, mb: 2 }}>PRIVACY POLICY</Typography>
        <Typography variant="h6" sx={{ color: '#00D1FF', fontWeight: 800 }}>DATA PROTECTION & CONSENT</Typography>
      </Box>

      <Stack spacing={4}>
         <section>
            <Typography variant="h6" sx={{ fontWeight: 900, mb: 2 }}>1. Information Collection</Typography>
            <Typography sx={{ color: '#708090', lineHeight: 1.8 }}>
               We collect only the information necessary to provide institutional signal intelligence services.
               This includes your name, email address, and terminal usage statistics.
            </Typography>
         </section>

         <section>
            <Typography variant="h6" sx={{ fontWeight: 900, mb: 2 }}>2. Data Usage</Typography>
            <Typography sx={{ color: '#708090', lineHeight: 1.8 }}>
               Your data is used to personalize your terminal experience, provide security updates, and
               improve our machine-learning models. We do not sell your personal data to third parties.
            </Typography>
         </section>

         <section>
            <Typography variant="h6" sx={{ fontWeight: 900, mb: 2 }}>3. Security</Typography>
            <Typography sx={{ color: '#708090', lineHeight: 1.8 }}>
               We implement industry-standard security measures, including Firebase Authentication and
               encrypted PostgreSQL storage, to protect your personal information.
            </Typography>
         </section>

         <Divider sx={{ opacity: 0.1 }} />
         <Typography variant="caption" sx={{ color: '#708090', textAlign: 'center' }}>
            © 2026 TradeMind AI • Secure Financial Research
         </Typography>
      </Stack>
    </Box>
  );
}
