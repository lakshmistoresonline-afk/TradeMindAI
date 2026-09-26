import { useState, useEffect } from 'react';
import { Paper, Box, Typography, Button, Stack, IconButton, alpha } from '@mui/material';
import { Download, X } from 'lucide-react';
import { MONO_FONT, COLORS } from '../theme/institutionalTheme';

/**
 * Native PWA Add-to-Homescreen Installer Banner
 * Listens for beforeinstallprompt and offers a 1-tap "INSTALL APP" experience on Android & Desktop.
 */
export default function InstallPwaPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const handleBeforeInstall = (e: any) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setVisible(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      setVisible(false);
    }
    setDeferredPrompt(null);
  };

  if (!visible) return null;

  return (
    <Paper
      elevation={0}
      sx={{
        position: 'fixed',
        bottom: { xs: 72, md: 24 },
        right: { xs: 16, md: 24 },
        left: { xs: 16, md: 'auto' },
        zIndex: 1400,
        bgcolor: 'rgba(15, 23, 42, 0.95)',
        border: `1px solid ${COLORS.borderCyan}`,
        borderRadius: 2,
        p: 2.5,
        backdropFilter: 'blur(20px)',
        boxShadow: '0 20px 40px -10px rgba(0, 209, 255, 0.3)',
        maxWidth: 380,
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Stack direction="row" spacing={1.5} alignItems="center">
          <Box sx={{ p: 1, bgcolor: alpha(COLORS.cyan, 0.15), borderRadius: 1.5 }}>
            <Download size={20} color={COLORS.cyan} />
          </Box>
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 950, color: '#fff', fontFamily: MONO_FONT }}>
              INSTALL TRADEMIND APP
            </Typography>
            <Typography variant="caption" sx={{ color: COLORS.slateText, fontWeight: 600, display: 'block' }}>
              Add to Home Screen for native app speed and offline access.
            </Typography>
          </Box>
        </Stack>
        <IconButton size="small" onClick={() => setVisible(false)} sx={{ color: COLORS.slateMuted, p: 0.5 }}>
          <X size={16} />
        </IconButton>
      </Box>

      <Stack direction="row" spacing={1.5} sx={{ mt: 2 }}>
        <Button
          fullWidth
          variant="contained"
          size="small"
          onClick={handleInstallClick}
          sx={{ bgcolor: COLORS.cyan, color: '#000', fontWeight: 950, fontFamily: MONO_FONT }}
        >
          INSTALL NOW
        </Button>
        <Button
          size="small"
          onClick={() => setVisible(false)}
          sx={{ color: COLORS.slateMuted, fontWeight: 800, fontSize: '0.7rem' }}
        >
          LATER
        </Button>
      </Stack>
    </Paper>
  );
}
