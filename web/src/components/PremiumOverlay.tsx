import { Box, Typography, Button, alpha } from '@mui/material';
import { Lock, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface PremiumOverlayProps {
    title?: string;
    blur?: boolean;
}

export default function PremiumOverlay({ title = "PREMIUM ANALYSIS", blur = true }: PremiumOverlayProps) {
  const navigate = useNavigate();

  return (
    <Box sx={{
        position: 'relative',
        minHeight: 200,
        width: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 1,
        overflow: 'hidden',
        bgcolor: alpha('#00D1FF', 0.02)
    }}>
      {blur && (
        <Box sx={{
            position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
            backdropFilter: 'blur(8px)', zIndex: 1,
            background: 'linear-gradient(180deg, rgba(15, 23, 42, 0.5) 0%, rgba(15, 23, 42, 0.9) 100%)'
        }} />
      )}

      <Box sx={{ zIndex: 2, textAlign: 'center', p: 4 }}>
         <Lock size={32} color="#00D1FF" style={{ marginBottom: 16 }} />
         <Typography variant="h6" sx={{ fontWeight: 950, color: 'white', mb: 1 }}>{title}</Typography>
         <Typography variant="body2" sx={{ color: '#708090', mb: 4, maxWidth: 300, mx: 'auto' }}>
            Institutional-grade evidence and machine-learning thesis are reserved for PRO members.
         </Typography>
         <Button
            variant="contained"
            onClick={() => navigate('/pricing')}
            startIcon={<Zap size={18} />}
            sx={{ px: 4, py: 1.2, fontWeight: 950 }}
         >
            UNLOCK ACCESS
         </Button>
      </Box>
    </Box>
  );
}
