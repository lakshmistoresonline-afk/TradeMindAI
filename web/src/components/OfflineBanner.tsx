import { useState, useEffect } from 'react';
import { Box, Typography, Stack, alpha } from '@mui/material';
import { WifiOff, Wifi } from 'lucide-react';
import { MONO_FONT, COLORS } from '../theme/institutionalTheme';

/**
 * OfflineBanner Component
 * Monitors network connectivity and renders a gentle glassmorphic top banner when offline:
 * "🟡 Offline Mode — Displaying cached PWA signal snapshot"
 */
export default function OfflineBanner() {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const [restored, setRestored] = useState(false);

  useEffect(() => {
    const handleOffline = () => {
      setIsOffline(true);
      setRestored(false);
    };

    const handleOnline = () => {
      setIsOffline(false);
      setRestored(true);
      const timer = setTimeout(() => setRestored(false), 3500);
      return () => clearTimeout(timer);
    };

    window.addEventListener('offline', handleOffline);
    window.addEventListener('online', handleOnline);

    return () => {
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('online', handleOnline);
    };
  }, []);

  if (!isOffline && !restored) return null;

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 4,
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 1500,
        bgcolor: isOffline ? 'rgba(15, 23, 42, 0.95)' : alpha(COLORS.green, 0.15),
        border: `1px solid ${isOffline ? COLORS.borderPurple : COLORS.green}`,
        borderRadius: 2,
        px: 2.5,
        py: 0.8,
        backdropFilter: 'blur(16px)',
        boxShadow: isOffline ? '0 10px 30px rgba(245, 158, 11, 0.2)' : '0 10px 30px rgba(16, 185, 129, 0.2)',
      }}
    >
      <Stack direction="row" spacing={1.5} alignItems="center">
        {isOffline ? (
          <>
            <WifiOff size={16} color={COLORS.amber} />
            <Typography variant="caption" sx={{ color: COLORS.amber, fontWeight: 950, fontFamily: MONO_FONT, fontSize: '0.7rem' }}>
              OFFLINE MODE — DISPLAYING CACHED PWA SNAPSHOT
            </Typography>
          </>
        ) : (
          <>
            <Wifi size={16} color={COLORS.green} />
            <Typography variant="caption" sx={{ color: COLORS.green, fontWeight: 950, fontFamily: MONO_FONT, fontSize: '0.7rem' }}>
              BACK ONLINE — LIVE FEED SYNCHRONIZED
            </Typography>
          </>
        )}
      </Stack>
    </Box>
  );
}
