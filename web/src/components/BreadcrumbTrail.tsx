import { Breadcrumbs, Typography, Link, Box } from '@mui/material';
import { ChevronRight, Home } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { MONO_FONT, COLORS } from '../theme/institutionalTheme';

/**
 * BreadcrumbTrail Component
 * Renders clickable location paths (e.g., Home > Signals > LT) for instant navigation context.
 */
export default function BreadcrumbTrail() {
  const location = useLocation();
  const navigate = useNavigate();

  const pathnames = location.pathname.split('/').filter(x => x);

  if (pathnames.length === 0 || location.pathname === '/') return null;

  return (
    <Box sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
      <Breadcrumbs
        separator={<ChevronRight size={12} color={COLORS.slateMuted} />}
        aria-label="breadcrumb"
        sx={{
          '& .MuiBreadcrumbs-li': {
            fontSize: '0.675rem',
            fontWeight: 800,
            fontFamily: MONO_FONT,
          }
        }}
      >
        <Link
          underline="hover"
          sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: COLORS.slateMuted, cursor: 'pointer', '&:hover': { color: COLORS.cyan } }}
          onClick={() => navigate('/dashboard')}
        >
          <Home size={12} /> HOME
        </Link>
        {pathnames.map((value, index) => {
          const last = index === pathnames.length - 1;
          const to = `/${pathnames.slice(0, index + 1).join('/')}`;
          const formattedValue = value.toUpperCase().replace(/-/g, ' ');

          return last ? (
            <Typography key={to} sx={{ color: COLORS.cyan, fontWeight: 950, fontSize: '0.675rem', fontFamily: MONO_FONT }}>
              {formattedValue}
            </Typography>
          ) : (
            <Link
              key={to}
              underline="hover"
              sx={{ color: COLORS.slateMuted, cursor: 'pointer', '&:hover': { color: COLORS.cyan } }}
              onClick={() => navigate(to)}
            >
              {formattedValue}
            </Link>
          );
        })}
      </Breadcrumbs>
    </Box>
  );
}
