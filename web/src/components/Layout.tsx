import React, { useState, useEffect, createContext, useContext } from 'react';
import { Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Container, Snackbar, Alert, Stack, Divider, Chip, Menu, MenuItem, IconButton, Avatar, Button } from '@mui/material';
import {
  LayoutDashboard,
  Zap,
  LogOut,
  Activity,
  Menu as MenuIcon,
  ChevronDown,
  User,
  Database,
  FileText,
  ShieldCheck,
  TrendingUp,
  Home,
  Cpu
} from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMediaQuery, useTheme } from '@mui/material';
import { API_BASE_URL } from '../api/client';
import { useAuth } from '../hooks/useAuth';
import { useBackendHealth } from '../hooks/useBackendHealth';
import { formatNSEDateTime } from '../utils/nseDateUtils';
import MobileBottomNav from './MobileBottomNav';
import InstallPwaPrompt from './InstallPwaPrompt';

const drawerWidth = 260;

// Notification Context
export const NotificationContext = createContext({
  showNotification: (_message: string, _severity: 'success' | 'error' | 'info' | 'warning') => {}
});

export const useNotification = () => useContext(NotificationContext);

const userMenuItems = [
  { text: 'DASHBOARD', icon: <LayoutDashboard size={18} />, path: '/dashboard' },
  { text: 'SIGNALS', icon: <Zap size={18} />, path: '/signals' },
  { text: 'PERFORMANCE', icon: <TrendingUp size={18} />, path: '/performance' },
  { text: 'PRICING', icon: <FileText size={18} />, path: '/pricing' },
  { text: 'ACCOUNT', icon: <User size={18} />, path: '/account' },
];

const publicMenuItems = [
  { text: 'HOME', icon: <Home size={18} />, path: '/' },
  { text: 'PERFORMANCE', icon: <TrendingUp size={18} />, path: '/performance' },
  { text: 'PRICING', icon: <FileText size={18} />, path: '/pricing' },
  { text: 'TRUST CENTER', icon: <ShieldCheck size={18} />, path: '/trust' },
  { text: 'METHODOLOGY', icon: <Cpu size={18} />, path: '/methodology' },
];

const adminMenuItems = [
  { text: 'ADMIN DASHBOARD', icon: <LayoutDashboard size={18} />, path: '/admin/dashboard' },
  { text: 'SIGNAL OPS', icon: <Zap size={18} />, path: '/admin/signals' },
  { text: 'DATA PIPELINE', icon: <Database size={18} />, path: '/admin/data' },
  { text: 'SYSTEM STATUS', icon: <Activity size={18} />, path: '/admin/status' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const { user, isAdmin, logout } = useAuth();
  const { isOnline } = useBackendHealth();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' as any });
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [lastRefreshTime, setLastRefreshTime] = useState<Date>(new Date());

  useEffect(() => {
    const refreshInterval = setInterval(() => {
      setLastRefreshTime(new Date());
    }, 30000);

    try {
      const wsUrl = API_BASE_URL.replace('http', 'ws').replace('/api/v1', '/ws/alerts');
      const socket = new WebSocket(wsUrl);

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'AI_COMPLETED') {
            showNotification(data.message, 'success');
            setLastRefreshTime(new Date());
          }
        } catch (e) {
          console.error("WS Error:", e);
        }
      };

      socket.onerror = () => {
        try { socket.close(); } catch {}
      };

      return () => {
        clearInterval(refreshInterval);
        try { socket.close(); } catch {}
      };
    } catch {
      return () => clearInterval(refreshInterval);
    }
  }, []);

  const showNotification = (message: string, severity: 'success' | 'error' | 'info' | 'warning') => {
    setNotification({ open: true, message, severity });
  };

  const handleClose = () => setNotification({ ...notification, open: false });

  const handleProfileClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileClose = () => {
    setAnchorEl(null);
  };

  const currentPath = location.pathname + location.search;
  const navItems = user ? userMenuItems : publicMenuItems;

  return (
    <NotificationContext.Provider value={{ showNotification }}>
      <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#020617' }}>
        {/* Top Accent Gradient Line */}
        <Box sx={{ position: 'fixed', top: 0, left: 0, right: 0, height: 2, zIndex: 1400, background: 'linear-gradient(90deg, #00D1FF, #7C3AED, #10b981)' }} />

        <AppBar
          position="fixed"
          sx={{
            zIndex: (theme) => theme.zIndex.drawer + 1,
            backgroundColor: 'rgba(2, 6, 23, 0.85)',
            backdropFilter: 'blur(16px)',
            borderBottom: '1px solid rgba(255,255,255,0.06)',
            boxShadow: 'none'
          }}
        >
          <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 2, sm: 4 }, minHeight: 70 }}>
            <Stack direction="row" spacing={3} alignItems="center">
              {isMobile && (
                <IconButton color="inherit" onClick={() => setDrawerOpen(true)} sx={{ mr: 1 }}>
                  <MenuIcon />
                </IconButton>
              )}
              <Typography
                variant="h6"
                noWrap
                onClick={() => navigate(user ? '/dashboard' : '/')}
                sx={{
                  fontWeight: 950,
                  letterSpacing: -1,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                  fontSize: '1.2rem',
                  fontFamily: 'JetBrains Mono, monospace'
                }}
              >
                <Box sx={{ bgcolor: '#00D1FF', color: '#000', px: 1, py: 0.2, borderRadius: 1, fontSize: '0.85rem', fontWeight: 950 }}>TM</Box>
                TRADEMIND AI
                <Chip
                  label="INSTITUTIONAL"
                  size="small"
                  sx={{
                    height: 20,
                    fontSize: '0.55rem',
                    fontWeight: 950,
                    bgcolor: 'rgba(16, 185, 129, 0.15)',
                    color: '#10b981',
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                    borderRadius: 1,
                    ml: 0.5
                  }}
                />
              </Typography>

              {!isMobile && (
                <Stack direction="row" spacing={1.5} sx={{ ml: 4 }}>
                   <HeaderStatus
                     label="SERVER"
                     value={isOnline ? "LOCAL CONNECTED" : "OFFLINE MODE"}
                     color={isOnline ? "#10b981" : "#f59e0b"}
                     dot={true}
                   />
                   <HeaderStatus
                     label="LAST REFRESH"
                     value={formatNSEDateTime(lastRefreshTime)}
                     color="#10b981"
                     dot={true}
                   />
                   <HeaderStatus label="UNIVERSE" value="NIFTY 200 CANONICAL" color="#00D1FF" />
                   <HeaderStatus label="ENGINE" value="V2.6 HMM & CVD" color="#a855f7" />
                </Stack>
              )}
            </Stack>

            <Stack direction="row" spacing={2} alignItems="center">
              {user ? (
                <>
                  <IconButton onClick={handleProfileClick} sx={{ p: 0.5, border: '1px solid rgba(255,255,255,0.1)', borderRadius: 2, bgcolor: 'rgba(255,255,255,0.02)' }}>
                    <Avatar sx={{ width: 30, height: 38, bgcolor: '#7C3AED', fontSize: '0.75rem', fontWeight: 950, borderRadius: 1.5 }}>
                      {user.email?.substring(0, 2).toUpperCase() || 'TM'}
                    </Avatar>
                    <ChevronDown size={14} style={{ marginLeft: 6, opacity: 0.6 }} color="white" />
                  </IconButton>

                  <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleProfileClose}
                    PaperProps={{
                      sx: {
                        width: 240,
                        mt: 1.5,
                        bgcolor: '#0f172a',
                        border: '1px solid rgba(255,255,255,0.1)',
                        boxShadow: '0 10px 40px rgba(0,0,0,0.8)',
                        borderRadius: 2
                      }
                    }}
                  >
                    <Box sx={{ px: 2, py: 2 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 950, color: '#fff' }}>{user.email || 'TradeMind Pro'}</Typography>
                      <Typography variant="caption" sx={{ color: '#00D1FF', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.3 }}>
                        <ShieldCheck size={12} /> Institutional Tier
                      </Typography>
                    </Box>
                    <Divider sx={{ opacity: 0.08 }} />
                    <MenuItem onClick={() => { handleProfileClose(); navigate('/account'); }} sx={{ py: 1.2 }}>
                      <ListItemIcon><User size={16} color="#94a3b8" /></ListItemIcon>
                      <ListItemText primary="Account & Referral" primaryTypographyProps={{ variant: 'body2', fontWeight: 700, color: '#f8fafc' }} />
                    </MenuItem>
                    <MenuItem onClick={() => { handleProfileClose(); navigate('/status'); }} sx={{ py: 1.2 }}>
                      <ListItemIcon><Activity size={16} color="#94a3b8" /></ListItemIcon>
                      <ListItemText primary="System Diagnostics" primaryTypographyProps={{ variant: 'body2', fontWeight: 700, color: '#f8fafc' }} />
                    </MenuItem>
                    <Divider sx={{ opacity: 0.08 }} />
                    <MenuItem onClick={() => { handleProfileClose(); logout(); }} sx={{ color: '#f43f5e', py: 1.2 }}>
                      <ListItemIcon><LogOut size={16} color="#f43f5e" /></ListItemIcon>
                      <ListItemText primary="Disconnect Terminal" primaryTypographyProps={{ variant: 'body2', fontWeight: 800 }} />
                    </MenuItem>
                  </Menu>
                </>
              ) : (
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => navigate('/login')}
                  sx={{
                    fontWeight: 950,
                    bgcolor: '#00D1FF',
                    color: '#000',
                    px: 2.5,
                    py: 0.8,
                    borderRadius: 1.5,
                    '&:hover': { bgcolor: '#38bdf8' }
                  }}
                >
                  SIGN IN
                </Button>
              )}
            </Stack>
          </Toolbar>
        </AppBar>

        <Drawer
          variant={isMobile ? "temporary" : "permanent"}
          open={isMobile ? drawerOpen : true}
          onClose={() => setDrawerOpen(false)}
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            [`& .MuiDrawer-paper`]: {
              width: drawerWidth,
              boxSizing: 'border-box',
              backgroundColor: '#070d19',
              borderRight: '1px solid rgba(255,255,255,0.06)',
              color: 'white',
              backgroundImage: 'none'
            },
          }}
        >
          <Toolbar sx={{ minHeight: 70 }} />
          <Box sx={{ overflow: 'auto', mt: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
            <List sx={{ px: 2 }}>
               <Typography variant="caption" sx={{ px: 2, mb: 1.5, display: 'block', fontWeight: 900, color: '#64748b', letterSpacing: 1.5 }}>
                 {user ? 'PRIMARY COMMANDS' : 'PUBLIC DIRECTORY'}
               </Typography>
               {navItems.map((item) => (
                 <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                    <ListItemButton
                      onClick={() => { navigate(item.path); if (isMobile) setDrawerOpen(false); }}
                      selected={currentPath === item.path || (item.path !== '/' && location.pathname.startsWith(item.path))}
                      sx={{
                        borderRadius: 2,
                        py: 1.2,
                        px: 2,
                        '&.Mui-selected': {
                          backgroundColor: 'rgba(0, 209, 255, 0.1)',
                          color: '#00D1FF',
                          border: '1px solid rgba(0, 209, 255, 0.2)',
                          '& .MuiListItemIcon-root': { color: '#00D1FF' },
                          '& .MuiTypography-root': { fontWeight: 950 }
                        },
                        '&:hover': { backgroundColor: 'rgba(255,255,255,0.03)' }
                      }}
                    >
                      <ListItemIcon sx={{ color: '#64748b', minWidth: 36 }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.text}
                        primaryTypographyProps={{
                          variant: 'body2',
                          fontWeight: 800,
                          letterSpacing: 0.8,
                          fontSize: '0.725rem'
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
               ))}

               {isAdmin && (
                 <>
                   <Typography variant="caption" sx={{ px: 2, mt: 3, mb: 1.5, display: 'block', fontWeight: 950, color: '#a855f7', letterSpacing: 1.5 }}>ADMINISTRATION</Typography>
                   {adminMenuItems.map((item) => (
                     <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                        <ListItemButton
                          onClick={() => { navigate(item.path); if (isMobile) setDrawerOpen(false); }}
                          selected={currentPath === item.path || (location.pathname.startsWith(item.path))}
                          sx={{
                            borderRadius: 2,
                            py: 1.2,
                            px: 2,
                            '&.Mui-selected': {
                              backgroundColor: 'rgba(124, 58, 237, 0.1)',
                              color: '#a855f7',
                              border: '1px solid rgba(124, 58, 237, 0.2)',
                              '& .MuiListItemIcon-root': { color: '#a855f7' },
                              '& .MuiTypography-root': { fontWeight: 950 }
                            },
                            '&:hover': { backgroundColor: 'rgba(255,255,255,0.03)' }
                          }}
                        >
                          <ListItemIcon sx={{ color: '#64748b', minWidth: 36 }}>
                            {item.icon}
                          </ListItemIcon>
                          <ListItemText
                            primary={item.text}
                            primaryTypographyProps={{
                              variant: 'body2',
                              fontWeight: 800,
                              letterSpacing: 0.8,
                              fontSize: '0.725rem'
                            }}
                          />
                        </ListItemButton>
                      </ListItem>
                   ))}
                 </>
               )}
            </List>

            <Box sx={{ mt: 'auto', p: 2.5, borderTop: '1px solid rgba(255,255,255,0.05)', bgcolor: 'rgba(2, 6, 23, 0.4)' }}>
               <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 800, fontSize: '0.625rem', display: 'block', fontFamily: 'JetBrains Mono, monospace' }}>
                  TRADEMIND TERMINAL V2.3
               </Typography>
               <Typography variant="caption" sx={{ color: '#475569', fontWeight: 700, fontSize: '0.55rem' }}>
                  NIFTY-200 Quantitative Intelligence
               </Typography>
            </Box>
          </Box>
        </Drawer>

        <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, sm: 4 }, width: isMobile ? '100%' : `calc(100% - ${drawerWidth}px)` }}>
          <Toolbar sx={{ minHeight: 70 }} />
          <Container maxWidth="xl" disableGutters={isMobile}>
            {children}
          </Container>
        </Box>

        <Snackbar open={notification.open} autoHideDuration={6000} onClose={handleClose}>
          <Alert onClose={handleClose} severity={notification.severity} sx={{ width: '100%', borderRadius: 1, fontWeight: 800, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', color: '#fff' }}>
            {notification.message}
          </Alert>
        </Snackbar>

        {/* Mobile PWA Bottom Navigation & Add-To-Homescreen Installer */}
        {user && <MobileBottomNav />}
        <InstallPwaPrompt />
      </Box>
    </NotificationContext.Provider>
  );
}

function HeaderStatus({ label, value, color, dot }: any) {
   return (
      <Box sx={{ px: 1.2, py: 0.4, border: '1px solid rgba(255,255,255,0.06)', borderRadius: 1, bgcolor: 'rgba(255,255,255,0.02)', display: 'flex', alignItems: 'center', gap: 0.8 }}>
         {dot && (
           <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: color, boxShadow: `0 0 8px ${color}` }} />
         )}
         <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 900, fontSize: '0.55rem', fontFamily: 'JetBrains Mono, monospace' }}>{label}:</Typography>
         <Typography variant="caption" sx={{ color: color, fontWeight: 950, fontSize: '0.55rem', fontFamily: 'JetBrains Mono, monospace' }}>{value}</Typography>
      </Box>
   );
}
