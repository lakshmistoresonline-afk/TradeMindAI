import React, { useState, useEffect, createContext, useContext } from 'react';
import { Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Container, Snackbar, Alert, Stack, Divider, Chip, Menu, MenuItem, IconButton, Avatar, alpha } from '@mui/material';
import {
  LayoutDashboard,
  Zap,
  LogOut,
  Activity,
  Menu as MenuIcon,
  ChevronDown,
  User,
  Database,
} from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMediaQuery, useTheme } from '@mui/material';
import { API_BASE_URL } from '../api/client';
import { useAuth } from '../hooks/useAuth';

const drawerWidth = 260;

// Notification Context
export const NotificationContext = createContext({
  showNotification: (_message: string, _severity: 'success' | 'error' | 'info' | 'warning') => {}
});

export const useNotification = () => useContext(NotificationContext);

const userMenuItems = [
  { text: 'DASHBOARD', icon: <LayoutDashboard size={20} />, path: '/dashboard' },
  { text: 'SIGNALS', icon: <Zap size={20} />, path: '/signals' },
  { text: 'ACCOUNT', icon: <User size={20} />, path: '/account' },
];

const adminMenuItems = [
  { text: 'COMMAND CENTER', icon: <LayoutDashboard size={20} />, path: '/admin/dashboard' },
  { text: 'SIGNAL OPS', icon: <Zap size={20} />, path: '/admin/signals' },
  { text: 'DATA FEEDS', icon: <Database size={20} />, path: '/admin/data' },
  { text: 'SYSTEM STATUS', icon: <Activity size={20} />, path: '/admin/status' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const { user, isAdmin, logout } = useAuth();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' as any });
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  useEffect(() => {
    const wsUrl = API_BASE_URL.replace('http', 'ws').replace('/api/v1', '/ws/alerts');
    const socket = new WebSocket(wsUrl);

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'AI_COMPLETED') {
          showNotification(data.message, 'success');
        }
      } catch (e) {
        console.error("WS Error:", e);
      }
    };

    return () => socket.close();
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

  return (
    <NotificationContext.Provider value={{ showNotification }}>
      <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#020617' }}>
        <AppBar
          position="fixed"
          sx={{
            zIndex: (theme) => theme.zIndex.drawer + 1,
            backgroundColor: 'rgba(5, 8, 12, 0.9)', // Slightly darker for V2.3.1
            backdropFilter: 'blur(12px)',
            borderBottom: '1px solid rgba(255,255,255,0.08)',
            boxShadow: 'none'
          }}
        >
          <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 2, sm: 4 } }}>
            <Stack direction="row" spacing={3} alignItems="center">
              {isMobile && (
                <IconButton color="inherit" onClick={() => setDrawerOpen(true)} sx={{ mr: 1 }}>
                  <MenuIcon />
                </IconButton>
              )}
              <Typography
                variant="h6"
                noWrap
                onClick={() => navigate('/')}
                sx={{
                  fontWeight: 950,
                  letterSpacing: -1,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                  fontSize: '1.25rem'
                }}
              >
                <Box sx={{ bgcolor: '#00D1FF', color: '#000', px: 1, borderRadius: 0.5, fontSize: '0.8rem', fontWeight: 900 }}>TM</Box>
                TRADEMIND AI
                <Chip
                  label="V2.2 FROZEN"
                  size="small"
                  sx={{
                    height: 18,
                    fontSize: '0.55rem',
                    fontWeight: 950,
                    bgcolor: '#10b981',
                    color: '#000',
                    borderRadius: 0.5,
                    ml: 1
                  }}
                />
              </Typography>

              {!isMobile && (
                <Stack direction="row" spacing={1} sx={{ ml: 4 }}>
                   <HeaderStatus label="SCAN" value="TOP 50 HARDENED" color="#10b981" />
                   <HeaderStatus label="MODE" value="SHADOW SIGNAL" color="#00D1FF" />
                </Stack>
              )}
            </Stack>

            <Stack direction="row" spacing={2} alignItems="center">
              {!isMobile && (
                <Stack direction="row" spacing={1} sx={{ mr: 4 }}>
                   <HeaderStatus label="MODE" value="SHADOW SIGNAL" color="#00D1FF" />
                   <HeaderStatus label="REAL TRADING" value="DISABLED" color="#ef4444" />
                   <HeaderStatus label="ROUTING" value="LOCKED" color="#ef4444" />
                </Stack>
              )}

              <IconButton onClick={handleProfileClick} sx={{ p: 0.5, border: '1px solid rgba(255,255,255,0.08)', borderRadius: 1 }}>
                <Avatar sx={{ width: 28, height: 28, bgcolor: '#7C3AED', fontSize: '0.7rem', fontWeight: 900, borderRadius: 0.5 }}>
                  {user?.email?.substring(0, 2).toUpperCase() || 'TR'}
                </Avatar>
                <ChevronDown size={14} style={{ marginLeft: 6, opacity: 0.5 }} color="white" />
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
                    borderRadius: 1
                  }
                }}
              >
                <Box sx={{ px: 2, py: 2 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 950, color: '#fff' }}>{user?.email || 'TradeMind Pro'}</Typography>
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700 }}>Institutional Access</Typography>
                </Box>
                <Divider sx={{ opacity: 0.05 }} />
                <MenuItem onClick={() => { handleProfileClose(); navigate('/status'); }} sx={{ py: 1.5 }}>
                  <ListItemIcon><Activity size={18} color="slategray" /></ListItemIcon>
                  <ListItemText primary="System Status" primaryTypographyProps={{ variant: 'body2', fontWeight: 800, color: 'slategray' }} />
                </MenuItem>
                <Divider sx={{ opacity: 0.05 }} />
                <MenuItem onClick={() => { handleProfileClose(); logout(); }} sx={{ color: '#ef4444', py: 1.5 }}>
                  <ListItemIcon><LogOut size={18} color="currentColor" /></ListItemIcon>
                  <ListItemText primary="Disconnect Terminal" primaryTypographyProps={{ variant: 'body2', fontWeight: 800 }} />
                </MenuItem>
              </Menu>
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
              backgroundColor: '#070a0f',
              borderRight: '1px solid rgba(255,255,255,0.08)',
              color: 'white',
              backgroundImage: 'none'
            },
          }}
        >
          <Toolbar sx={{ minHeight: 80 }} />
          <Box sx={{ overflow: 'auto', mt: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
            <List sx={{ px: 2 }}>
               <Typography variant="caption" sx={{ px: 2, mb: 2, display: 'block', fontWeight: 900, color: 'slategray', letterSpacing: 2 }}>PRIMARY COMMANDS</Typography>
               {userMenuItems.map((item) => (
                 <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                    <ListItemButton
                      onClick={() => { navigate(item.path); if (isMobile) setDrawerOpen(false); }}
                      selected={currentPath === item.path || (location.pathname.startsWith(item.path))}
                      sx={{
                        borderRadius: 1,
                        py: 1.4,
                        '&.Mui-selected': {
                          backgroundColor: alpha('#00D1FF', 0.08),
                          color: '#00D1FF',
                          '& .MuiListItemIcon-root': { color: '#00D1FF' },
                          '& .MuiTypography-root': { fontWeight: 950 }
                        },
                        '&:hover': { backgroundColor: alpha('#fff', 0.03) }
                      }}
                    >
                      <ListItemIcon sx={{ color: 'slategray', minWidth: 40 }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.text}
                        primaryTypographyProps={{
                          variant: 'body2',
                          fontWeight: 800,
                          letterSpacing: 1,
                          fontSize: '0.75rem'
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
               ))}

               {isAdmin && (
                 <>
                   <Typography variant="caption" sx={{ px: 2, mt: 4, mb: 2, display: 'block', fontWeight: 900, color: 'secondary.main', letterSpacing: 2 }}>ADMINISTRATION</Typography>
                   {adminMenuItems.map((item) => (
                     <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                        <ListItemButton
                          onClick={() => { navigate(item.path); if (isMobile) setDrawerOpen(false); }}
                          selected={currentPath === item.path || (location.pathname.startsWith(item.path))}
                          sx={{
                            borderRadius: 1,
                            py: 1.4,
                            '&.Mui-selected': {
                              backgroundColor: alpha('#7C3AED', 0.08),
                              color: 'secondary.main',
                              '& .MuiListItemIcon-root': { color: 'secondary.main' },
                              '& .MuiTypography-root': { fontWeight: 950 }
                            },
                            '&:hover': { backgroundColor: alpha('#fff', 0.03) }
                          }}
                        >
                          <ListItemIcon sx={{ color: 'slategray', minWidth: 40 }}>
                            {item.icon}
                          </ListItemIcon>
                          <ListItemText
                            primary={item.text}
                            primaryTypographyProps={{
                              variant: 'body2',
                              fontWeight: 800,
                              letterSpacing: 1,
                              fontSize: '0.75rem'
                            }}
                          />
                        </ListItemButton>
                      </ListItem>
                   ))}
                 </>
               )}
            </List>

            <Box sx={{ mt: 'auto', p: 3, borderTop: '1px solid rgba(255,255,255,0.05)' }}>
               <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, fontSize: '0.6rem' }}>
                  © 2026 TRADEMIND AI • STRATEGY V2.2
               </Typography>
            </Box>
          </Box>
        </Drawer>

        <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, sm: 4 }, width: isMobile ? '100%' : `calc(100% - ${drawerWidth}px)` }}>
          <Toolbar sx={{ minHeight: 80 }} />
          <Container maxWidth="xl" disableGutters={isMobile}>
            {children}
          </Container>
        </Box>

        <Snackbar open={notification.open} autoHideDuration={6000} onClose={handleClose}>
          <Alert onClose={handleClose} severity={notification.severity} sx={{ width: '100%', borderRadius: 0.5, fontWeight: 800, bgcolor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', color: '#fff' }}>
            {notification.message}
          </Alert>
        </Snackbar>
      </Box>
    </NotificationContext.Provider>
  );
}


function HeaderStatus({ label, value, color }: any) {
   return (
      <Box sx={{ px: 1.5, py: 0.5, border: '1px solid rgba(255,255,255,0.05)', borderRadius: 0.5, bgcolor: 'rgba(255,255,255,0.02)' }}>
         <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, fontSize: '0.55rem', mr: 1 }}>{label}:</Typography>
         <Typography variant="caption" sx={{ color: color, fontWeight: 950, fontSize: '0.55rem' }}>{value}</Typography>
      </Box>
   );
}
