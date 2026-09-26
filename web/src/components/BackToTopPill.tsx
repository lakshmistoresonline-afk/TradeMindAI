import { useState, useEffect } from 'react';
import { Button, alpha } from '@mui/material';
import { ArrowUp } from 'lucide-react';
import { MONO_FONT, COLORS } from '../theme/institutionalTheme';

/**
 * BackToTopPill Component
 * Renders a floating "↑ TOP" pill badge on the bottom-right when scrolled past 250px.
 * Smoothly scrolls back to top (y=0) when tapped.
 */
export default function BackToTopPill() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY || document.documentElement.scrollTop;
      setVisible(scrollY > 250);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleScrollToTop = () => {
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: 'smooth'
    });
  };

  if (!visible) return null;

  return (
    <Button
      variant="contained"
      size="small"
      onClick={handleScrollToTop}
      startIcon={<ArrowUp size={14} />}
      sx={{
        position: 'fixed',
        bottom: { xs: 80, md: 32 },
        right: { xs: 16, md: 32 },
        zIndex: 1350,
        bgcolor: 'rgba(15, 23, 42, 0.95)',
        color: COLORS.cyan,
        border: `1px solid ${COLORS.borderCyan}`,
        borderRadius: 8,
        px: 2,
        py: 0.8,
        fontWeight: 950,
        fontSize: '0.7rem',
        fontFamily: MONO_FONT,
        backdropFilter: 'blur(16px)',
        boxShadow: '0 10px 25px -5px rgba(0, 209, 255, 0.3)',
        '&:hover': {
          bgcolor: alpha(COLORS.cyan, 0.2),
          borderColor: COLORS.cyan,
          transform: 'translateY(-2px)'
        }
      }}
    >
      TOP
    </Button>
  );
}
