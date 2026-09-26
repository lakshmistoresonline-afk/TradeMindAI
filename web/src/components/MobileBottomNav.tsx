import { Paper, BottomNavigation, BottomNavigationAction } from '@mui/material';
import { LayoutDashboard, Zap, TrendingUp, FileText, User } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { MONO_FONT, COLORS } from '../theme/institutionalTheme';

/**
 * Mobile Bottom Navigation Bar (Android Material 3 & iOS Native Ergonomics)
 * Renders on small screens to give a 100% native mobile app feel.
 */
export default function MobileBottomNav() {
  const navigate = useNavigate();
  const location = useLocation();

  const currentPath = location.pathname;

  const getActiveTab = () => {
    if (currentPath.startsWith('/dashboard')) return 0;
    if (currentPath.startsWith('/signals')) return 1;
    if (currentPath.startsWith('/performance')) return 2;
    if (currentPath.startsWith('/pricing')) return 3;
    if (currentPath.startsWith('/account')) return 4;
    return 0;
  };

  return (
    <Paper
      elevation={0}
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 1300,
        display: { xs: 'block', md: 'none' },
        bgcolor: 'rgba(2, 6, 23, 0.95)',
        backdropFilter: 'blur(20px)',
        borderTop: `1px solid ${COLORS.borderLight}`,
        pb: 'env(safe-area-inset-bottom)',
      }}
    >
      <BottomNavigation
        showLabels
        value={getActiveTab()}
        sx={{
          bgcolor: 'transparent',
          height: 64,
          '& .MuiBottomNavigationAction-root': {
            color: COLORS.slateMuted,
            minWidth: 0,
            py: 1,
            '&.Mui-selected': {
              color: COLORS.cyan,
              '& .MuiSvgIcon-root, & svg': {
                color: COLORS.cyan,
                transform: 'scale(1.15)',
                transition: 'transform 0.2s ease-in-out',
              },
            },
            '& .MuiBottomNavigationAction-label': {
              fontSize: '0.625rem',
              fontWeight: 950,
              fontFamily: MONO_FONT,
              letterSpacing: 0.5,
              mt: 0.5,
              '&.Mui-selected': {
                fontSize: '0.65rem',
                color: COLORS.cyan,
              },
            },
          },
        }}
      >
        <BottomNavigationAction
          label="HOME"
          icon={<LayoutDashboard size={20} />}
          onClick={() => navigate('/dashboard')}
        />
        <BottomNavigationAction
          label="SIGNALS"
          icon={<Zap size={20} />}
          onClick={() => navigate('/signals')}
        />
        <BottomNavigationAction
          label="TRACK"
          icon={<TrendingUp size={20} />}
          onClick={() => navigate('/performance')}
        />
        <BottomNavigationAction
          label="PRICING"
          icon={<FileText size={20} />}
          onClick={() => navigate('/pricing')}
        />
        <BottomNavigationAction
          label="ACCOUNT"
          icon={<User size={20} />}
          onClick={() => navigate('/account')}
        />
      </BottomNavigation>
    </Paper>
  );
}
