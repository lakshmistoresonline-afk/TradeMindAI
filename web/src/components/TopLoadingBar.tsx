import { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { COLORS } from '../theme/institutionalTheme';

/**
 * TopLoadingBar (NProgress-style Route Transition Progress Bar)
 * Animates a glowing cyan/purple bar across the top of the screen during route transitions.
 */
export default function TopLoadingBar() {
  const location = useLocation();
  const [progress, setProgress] = useState(0);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setVisible(true);
    setProgress(30);

    const timer1 = setTimeout(() => setProgress(70), 100);
    const timer2 = setTimeout(() => setProgress(100), 250);
    const timer3 = setTimeout(() => {
      setVisible(false);
      setProgress(0);
    }, 400);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [location.pathname, location.search]);

  if (!visible) return null;

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: 3,
        zIndex: 2000,
        pointerEvents: 'none',
        bgcolor: 'transparent',
      }}
    >
      <Box
        sx={{
          height: '100%',
          width: `${progress}%`,
          background: `linear-gradient(90deg, ${COLORS.cyan}, ${COLORS.purpleDark}, ${COLORS.green})`,
          transition: 'width 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: '0 0 10px rgba(0, 209, 255, 0.8)',
        }}
      />
    </Box>
  );
}
