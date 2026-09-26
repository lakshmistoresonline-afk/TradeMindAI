/**
 * TradeMind AI: Institutional Glassmorphic Theme & Design Tokens (V3.3)
 * Provides a uniform, cohesive design system across all user and admin pages.
 */

export const MONO_FONT = "'JetBrains Mono', monospace";
export const BODY_FONT = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";

export const COLORS = {
  bgObsidian: '#020617',
  surfaceSlate: 'rgba(15, 23, 42, 0.85)',
  surfaceSlateSolid: '#0f172a',
  borderLight: 'rgba(255, 255, 255, 0.08)',
  borderCyan: 'rgba(0, 209, 255, 0.25)',
  borderPurple: 'rgba(124, 58, 237, 0.25)',
  borderGreen: 'rgba(16, 185, 129, 0.25)',

  cyan: '#00D1FF',
  purple: '#a855f7',
  purpleDark: '#7C3AED',
  green: '#10b981',
  red: '#f43f5e',
  amber: '#f59e0b',
  slateText: '#94a3b8',
  slateMuted: '#64748b',
  textBright: '#f8fafc',
};

export const GLASS_PANEL_STYLE = {
  bgcolor: COLORS.surfaceSlate,
  border: `1px solid ${COLORS.borderLight}`,
  borderRadius: 2,
  backdropFilter: 'blur(16px)',
  boxShadow: '0 20px 40px -15px rgba(0, 0, 0, 0.5)',
};

export const GRADIENT_ACCENT_BAR = {
  height: 3,
  width: '100%',
  background: `linear-gradient(90deg, ${COLORS.cyan}, ${COLORS.purpleDark}, ${COLORS.green})`,
};

export const HERO_BANNER_STYLE = {
  p: { xs: 3, md: 4 },
  borderRadius: 3,
  background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(11, 19, 41, 0.85))',
  border: `1px solid ${COLORS.borderLight}`,
  backdropFilter: 'blur(16px)',
  boxShadow: '0 20px 40px -15px rgba(0, 0, 0, 0.5)',
  position: 'relative' as const,
  overflow: 'hidden' as const,
};

export const TABLE_HEAD_CELL_STYLE = {
  color: COLORS.slateMuted,
  fontWeight: 900,
  fontSize: '0.65rem',
  letterSpacing: 1,
  borderBottom: `1px solid ${COLORS.borderLight}`,
  py: 1.8,
};

export const TABLE_ROW_STYLE = {
  '& td': { borderBottom: '1px solid rgba(255,255,255,0.03)', py: 1.5 },
  transition: 'all 0.15s ease-in-out',
  '&:hover': {
    bgcolor: 'rgba(255,255,255,0.02)',
  },
};
