import React, { useState, useEffect, createContext, useContext } from 'react';
import { Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Container, Snackbar, Alert, Stack, Divider, Button, Chip, Menu, MenuItem, Tooltip } from '@mui/material';
import { History, Bot, Activity, Zap, X, Settings, User, LogOut, ChevronDown } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMediaQuery, useTheme, IconButton, BottomNavigation, BottomNavigationAction, Paper as MuiPaper, Fab } from '@mui/material';
import { Menu as MenuIcon } from 'lucide-react';
import CommandPalette from './CommandPalette';
import AICopilot from '../pages/AICopilot';
import { API_BASE_URL, getMarketStats } from '../api/client';

const drawerWidth = 240;

// Notification Context
export const NotificationContext = createContext({
  showNotification: (_message: string, _severity: 'success' | 'error' | 'info' | 'warning') => {},
  setCopilotContext: (_context: any) => {}
});

export const useNotification = () => useContext(NotificationContext);

const primaryMenu = [
  { text: 'DASHBOARD', icon: <Activity size={20} />, path: '/' },
  { text: 'LIVE SIGNALS', icon: <Zap size={20} />, path: '/signals' },
  { text: 'HISTORY', icon: <History size={20} />, path: '/history' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [copilotOpen, setCopilotOpen] = useState(false);
  const [copilotContext, setCopilotContext] = useState<any>(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' as any });
  const [marketBrief, setMarketBrief] = useState<any>(null);

  // User Menu State
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const userMenuOpen = Boolean(anchorEl);

  useEffect(() => {
    getMarketStats().then(data => {
       const nifty = data?.['NIFTY 50'];
       if (nifty) setMarketBrief(nifty);
    }).catch(() => {});
  }, []);

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

  const handleUserMenuClick = (event: React.MouseEvent<HTMLElement>) => setAnchorEl(event.currentTarget);
  const handleUserMenuClose = () => setAnchorEl(null);

  return (
    <NotificationContext.Provider value={{ showNotification, setCopilotContext }}>
      <Box sx={{ display: 'flex' }}>
        <CommandPalette />
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: '#0f172a', borderBottom: '1px solid #334155' }} elevation={0}>
          <Toolbar>
            {isMobile && (
              <IconButton
                color="inherit"
                edge="start"
                onClick={() => setDrawerOpen(true)}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
            )}
            <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 900, mr: 1, letterSpacing: -1, color: 'white' }}>
              TRADEMIND AI
            </Typography>
            <Chip
              label="LIVE"
              size="small"
              sx={{ height: 16, fontSize: '0.5rem', fontWeight: 900, bgcolor: 'success.main', color: 'black', mr: 4 }}
            />

            {!isMobile && (
              <Stack direction="row" spacing={1} sx={{ flexGrow: 1 }}>
                {primaryMenu.map(item => (
                  <Button
                    key={item.text}
                    onClick={() => navigate(item.path)}
                    sx={{
                      color: location.pathname === item.path ? 'white' : 'slategray',
                      fontWeight: 800,
                      fontSize: '0.7rem',
                      letterSpacing: 1,
                      '&:hover': { color: 'primary.main' }
                    }}
                  >
                    {item.text}
                  </Button>
                ))}
              </Stack>
            )}

            <Stack direction="row" spacing={2} alignItems="center">
               {!isMobile && marketBrief && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, px: 2, py: 0.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.05)' }}>
                     <Activity size={14} className="text-emerald-500" />
                     <Typography variant="caption" sx={{ fontWeight: 900, color: 'primary.main', fontFamily: 'JetBrains Mono' }}>
                        NIFTY {marketBrief.value.toLocaleString()} ({marketBrief.change >= 0 ? '+' : ''}{marketBrief.change}%)
                     </Typography>
                  </Box>
               )}

               <Tooltip title="User Account">
                  <IconButton
                    onClick={handleUserMenuClick}
                    sx={{ bgcolor: 'rgba(255,255,255,0.05)', borderRadius: 2, p: 1 }}
                  >
                    <User size={18} />
                    <ChevronDown size={14} style={{ marginLeft: 4, opacity: 0.5 }} />
                  </IconButton>
               </Tooltip>

               <Menu
                 anchorEl={anchorEl}
                 open={userMenuOpen}
                 onClose={handleUserMenuClose}
                 PaperProps={{
                    sx: { width: 220, bgcolor: '#0f172a', border: '1px solid #334155', mt: 1.5, boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }
                 }}
               >
                  <Box sx={{ px: 2, py: 1.5 }}>
                     <Typography variant="subtitle2" sx={{ fontWeight: 900 }}>TradeMind User</Typography>
                     <Typography variant="caption" color="textSecondary">Institutional Access • Verified</Typography>
                  </Box>
                  <Divider sx={{ opacity: 0.05 }} />
                  <MenuItem onClick={() => { handleUserMenuClose(); navigate('/settings'); }}>
                     <ListItemIcon><Settings size={18} /></ListItemIcon>
                     <ListItemText primary="Settings" primaryTypographyProps={{ variant: 'body2', fontWeight: 800 }} />
                  </MenuItem>
                  <MenuItem onClick={() => { handleUserMenuClose(); navigate('/admin'); }}>
                     <ListItemIcon><Activity size={18} /></ListItemIcon>
                     <ListItemText primary="System Status" primaryTypographyProps={{ variant: 'body2', fontWeight: 800 }} />
                  </MenuItem>
                  <Divider sx={{ opacity: 0.05 }} />
                  <MenuItem onClick={handleUserMenuClose} sx={{ color: 'error.main' }}>
                     <ListItemIcon><LogOut size={18} color="currentColor" /></ListItemIcon>
                     <ListItemText primary="Sign Out" primaryTypographyProps={{ variant: 'body2', fontWeight: 800 }} />
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
            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box', backgroundColor: '#0f172a', borderRight: '1px solid #334155', color: 'white' },
          }}
        >
          <Toolbar />
          <Box sx={{ height: 'calc(100% - 64px)', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ flexGrow: 1, pt: 4 }}>
              <List>
                 {primaryMenu.map((item) => (
                   <ListItem key={item.text} disablePadding>
                      <ListItemButton
                        onClick={() => navigate(item.path)}
                        selected={location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path))}
                        sx={{
                          '&.Mui-selected': { backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981' },
                          '&.Mui-selected .MuiListItemIcon-root': { color: '#10b981' },
                          mx: 1.5,
                          borderRadius: 1,
                          mb: 1.5,
                          py: 1
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
                            letterSpacing: 1.5,
                            fontSize: '0.8rem'
                          }}
                        />
                      </ListItemButton>
                    </ListItem>
                 ))}
              </List>
            </Box>

            <Box sx={{ p: 2, borderTop: '1px solid rgba(255,255,255,0.03)' }}>
               <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Bot size={18} />}
                  onClick={() => setCopilotOpen(true)}
                  sx={{ borderColor: 'rgba(255,255,255,0.1)', color: 'slategray', fontWeight: 800, '&:hover': { borderColor: 'primary.main', color: 'primary.main' } }}
               >
                  ASK TRADEMIND
               </Button>
            </Box>
          </Box>
        </Drawer>

        <Drawer
          anchor="right"
          open={copilotOpen}
          onClose={() => setCopilotOpen(false)}
          sx={{ [`& .MuiDrawer-paper`]: { width: { xs: '100%', sm: 450 }, backgroundColor: '#020617', borderLeft: '1px solid #334155' } }}
        >
           <Box sx={{ p: 2, borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center', bgcolor: '#0f172a' }}>
              <Stack direction="row" spacing={1} alignItems="center">
                 <Bot size={20} className="text-emerald-500" />
                 <Typography variant="h6" fontWeight={900}>AI COPILOT</Typography>
              </Stack>
              <IconButton onClick={() => setCopilotOpen(false)}><X size={20} /></IconButton>
           </Box>
           <Box sx={{ height: 'calc(100% - 60px)', p: 0 }}>
              <AICopilot isDrawer stockContext={copilotContext} />
           </Box>
        </Drawer>

        <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, sm: 3 }, pb: { xs: 15, sm: 12 }, backgroundColor: '#020617', minHeight: '100vh', width: isMobile ? '100%' : `calc(100% - ${drawerWidth}px)` }}>
          <Toolbar />
          <Container maxWidth="xl" disableGutters={isMobile}>
            {children}
          </Container>
        </Box>

        <Snackbar open={notification.open} autoHideDuration={6000} onClose={handleClose}>
          <Alert onClose={handleClose} severity={notification.severity} sx={{ width: '100%', borderRadius: 1, fontWeight: 700 }}>
            {notification.message}
          </Alert>
        </Snackbar>

        {isMobile && (
          <MuiPaper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 1200 }} elevation={3}>
            <BottomNavigation
              showLabels
              value={location.pathname === '/' ? '/' : `/${location.pathname.split('/')[1]}`}
              onChange={(_, newValue) => navigate(newValue)}
              sx={{ bgcolor: '#0f172a', borderTop: '1px solid #1e293b' }}
            >
              <BottomNavigationAction label="Terminal" value="/" icon={<Activity size={20} />} />
              <BottomNavigationAction label="Signals" value="/signals" icon={<Zap size={20} />} />
              <BottomNavigationAction label="History" value="/history" icon={<History size={20} />} />
            </BottomNavigation>
          </MuiPaper>
        )}

        {!isMobile && (
           <Fab
             color="primary"
             aria-label="copilot"
             onClick={() => setCopilotOpen(true)}
             sx={{ position: 'fixed', bottom: 32, right: 32, zIndex: 1000, boxShadow: '0 8px 32px rgba(16, 185, 129, 0.3)' }}
           >
             <Bot size={24} color="black" />
           </Fab>
        )}
      </Box>
    </NotificationContext.Provider>
  );
}
