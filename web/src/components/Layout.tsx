import React, { useState, createContext, useContext, useEffect } from 'react';
import { Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Container, Snackbar, Alert, Stack, Chip, Divider } from '@mui/material';
import { LayoutDashboard, LineChart, BrainCircuit, Settings, TrendingUp, Briefcase, PieChart, Bot, Wallet, Calendar, ShieldAlert, Code, Monitor, Trophy, Star, Book, ShieldCheck } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMediaQuery, useTheme, IconButton } from '@mui/material';
import { Menu as MenuIcon } from 'lucide-react';
import CommandPalette from './CommandPalette';

const drawerWidth = 240;
const workspaces = [
  { id: '1', name: 'AI Research', type: 'INSTITUTIONAL' },
  { id: '2', name: 'Intraday Feed', type: 'TRADING' },
  { id: '3', name: 'Quant Engine', type: 'ANALYTICS' },
];

// Notification Context
export const NotificationContext = createContext({
  showNotification: (_message: string, _severity: 'success' | 'error' | 'info' | 'warning') => {}
});

export const useNotification = () => useContext(NotificationContext);

const menuItems = [
  { text: 'Dashboard', icon: <LayoutDashboard size={20} />, path: '/' },
  { text: 'Market', icon: <LineChart size={20} />, path: '/market' },
  { text: 'Options', icon: <Box sx={{ width: 20, height: 20, border: '2px solid currentColor', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Box sx={{ width: 10, height: 10, bgcolor: 'currentColor', borderRadius: '50%' }} /></Box>, path: '/options' },
  { text: 'Treemap', icon: <Box sx={{ width: 20, height: 20, border: '1px solid currentColor', display: 'flex' }}><Box sx={{ flex: 1, borderRight: '1px solid currentColor' }} /><Box sx={{ flex: 1 }} /></Box>, path: '/treemap' },
  { text: 'Heatmap', icon: <Box sx={{ width: 20, height: 20, display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '2px' }}><Box sx={{ bgcolor: 'currentColor', opacity: 0.8 }} /><Box sx={{ border: '1px solid currentColor' }} /><Box sx={{ border: '1px solid currentColor' }} /><Box sx={{ bgcolor: 'currentColor', opacity: 0.5 }} /></Box>, path: '/heatmap' },
  { text: 'Portfolio', icon: <Briefcase size={20} />, path: '/portfolio' },
  { text: 'Stress Test', icon: <ShieldAlert size={20} />, path: '/stress-test' },
  { text: 'AI Analysis', icon: <BrainCircuit size={20} />, path: '/analysis' },
  { text: 'Research Lab', icon: <Book size={20} />, path: '/research' },
  { text: 'AI Chat', icon: <Bot size={20} />, path: '/chat' },
  { text: 'Strategy', icon: <Box sx={{ width: 20, height: 20, display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Code size={20} /></Box>, path: '/strategy' },
  { text: 'Paper Trading', icon: <Wallet size={20} />, path: '/paper-trading' },
  { text: 'Trade Journal', icon: <Book size={20} />, path: '/journal' },
  { text: 'Calendar', icon: <Calendar size={20} />, path: '/calendar' },
  { text: 'Top Picks', icon: <Trophy size={20} />, path: '/ranking' },
  { text: 'Control Center', icon: <ShieldCheck size={20} />, path: '/admin' },
  { text: 'Sector Rotation', icon: <PieChart size={20} />, path: '/sectors' },
  { text: 'Settings', icon: <Settings size={20} />, path: '/settings' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [activeWorkspace, setActiveWorkspace] = useState(workspaces[0]);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' as any });
  const [pinnedStocks] = useState<string[]>(['RELIANCE', 'TCS', 'HDFCBANK']);

  const showNotification = (message: string, severity: 'success' | 'error' | 'info' | 'warning') => {
    setNotification({ open: true, message, severity });

    // Browser Native Notification
    if (Notification.permission === 'granted') {
      new Notification('TradeMind AI Alert', { body: message });
    }
  };

  useEffect(() => {
    const saved = localStorage.getItem('active_workspace');
    if (saved) {
       const ws = workspaces.find(w => w.id === saved);
       if (ws) setActiveWorkspace(ws);
    }
  }, []);

  const handleWorkspaceChange = (ws: any) => {
     setActiveWorkspace(ws);
     localStorage.setItem('active_workspace', ws.id);
     showNotification(`Switched to ${ws.name} workspace`, 'success');

     // Vision 2.0: Deep Workspace Navigation
     if (ws.id === '1') {
       navigate('/');
     } else if (ws.id === '2') {
       navigate('/market');
     } else if (ws.id === '3') {
       navigate('/ranking');
     }
  };

  const handleClose = () => setNotification({ ...notification, open: false });

  return (
    <NotificationContext.Provider value={{ showNotification }}>
      <Box sx={{ display: 'flex' }}>
        <CommandPalette />
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: '#0f172a', borderBottom: '1px solid #334155' }} elevation={0}>
          <Toolbar>
            {isMobile && (
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={() => setDrawerOpen(true)}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
            )}
            <TrendingUp className="text-emerald-500 mr-2" />
            <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold', mr: 4, display: { xs: 'none', sm: 'block' } }}>
              TradeMind AI
            </Typography>

            <Stack direction="row" spacing={1} sx={{ ml: isMobile ? 0 : 4, overflowX: 'auto', py: 1 }}>
               {workspaces.map(ws => (
                 <Chip
                   key={ws.id}
                   icon={<Monitor size={14} />}
                   label={ws.name}
                   onClick={(e) => {
                     e.preventDefault();
                     handleWorkspaceChange(ws);
                   }}
                   variant={activeWorkspace.id === ws.id ? 'filled' : 'outlined'}
                   color={activeWorkspace.id === ws.id ? 'primary' : 'default'}
                   sx={{ cursor: 'pointer', flexShrink: 0, fontWeight: 'bold' }}
                 />
               ))}
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
          <Box sx={{ overflow: 'auto', mt: 2 }}>
            <List subheader={<Typography variant="caption" sx={{ p: 2, color: 'slategray', fontWeight: 'bold' }}>MENU</Typography>}>
              {menuItems.map((item) => (
                <ListItem key={item.text} disablePadding>
                  <ListItemButton
                    onClick={() => navigate(item.path)}
                    selected={location.pathname === item.path}
                    sx={{
                      '&.Mui-selected': { backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#10b981' },
                      '&.Mui-selected .MuiListItemIcon-root': { color: '#10b981' },
                      mx: 1,
                      borderRadius: 1,
                      mb: 0.5
                    }}
                  >
                    <ListItemIcon sx={{ color: 'slategray', minWidth: 40 }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText primary={item.text} primaryTypographyProps={{ variant: 'body2' }} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>

            <Divider sx={{ mx: 2, my: 1, opacity: 0.1 }} />

            <List subheader={<Typography variant="caption" sx={{ p: 2, color: 'slategray', fontWeight: 'bold' }}>PINNED STOCKS</Typography>}>
               {pinnedStocks.map(symbol => (
                 <ListItem key={symbol} disablePadding>
                    <ListItemButton
                      onClick={() => navigate('/analysis', { state: { symbol } })}
                      sx={{ mx: 1, borderRadius: 1, mb: 0.5 }}
                    >
                       <ListItemIcon sx={{ color: 'primary.main', minWidth: 40 }}><Star size={16} /></ListItemIcon>
                       <ListItemText primary={symbol} primaryTypographyProps={{ variant: 'body2', fontWeight: 'bold' }} />
                    </ListItemButton>
                 </ListItem>
               ))}
            </List>
          </Box>
        </Drawer>
        <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, sm: 3 }, backgroundColor: '#020617', minHeight: '100vh', width: isMobile ? '100%' : `calc(100% - ${drawerWidth}px)` }}>
          <Toolbar />
          <Container maxWidth="xl" disableGutters={isMobile}>
            {children}
          </Container>
        </Box>

        <Snackbar open={notification.open} autoHideDuration={6000} onClose={handleClose}>
          <Alert onClose={handleClose} severity={notification.severity} sx={{ width: '100%', borderRadius: 2 }}>
            {notification.message}
          </Alert>
        </Snackbar>
      </Box>
    </NotificationContext.Provider>
  );
}
