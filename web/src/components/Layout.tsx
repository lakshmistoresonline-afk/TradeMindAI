import React, { useState, createContext, useContext } from 'react';
import { Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Container, Snackbar, Alert } from '@mui/material';
import { LayoutDashboard, LineChart, BrainCircuit, Settings, TrendingUp, Briefcase, PieChart, Bot, Wallet, Calendar, ShieldAlert } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const drawerWidth = 240;

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
  { text: 'AI Chat', icon: <Bot size={20} />, path: '/chat' },
  { text: 'Strategy', icon: <Box sx={{ width: 20, height: 20, display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Code size={20} /></Box>, path: '/strategy' },
  { text: 'Paper Trading', icon: <Wallet size={20} />, path: '/paper-trading' },
  { text: 'Calendar', icon: <Calendar size={20} />, path: '/calendar' },
  { text: 'Sector Rotation', icon: <PieChart size={20} />, path: '/sectors' },
  { text: 'Settings', icon: <Settings size={20} />, path: '/settings' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' as any });

  const showNotification = (message: string, severity: 'success' | 'error' | 'info' | 'warning') => {
    setNotification({ open: true, message, severity });

    // Browser Native Notification
    if (Notification.permission === 'granted') {
      new Notification('TradeMind AI Alert', { body: message });
    }
  };

  useEffect(() => {
    if (Notification.permission !== 'granted' && Notification.permission !== 'denied') {
      Notification.requestPermission();
    }
  }, []);

  const handleClose = () => setNotification({ ...notification, open: false });

  return (
    <NotificationContext.Provider value={{ showNotification }}>
      <Box sx={{ display: 'flex' }}>
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, backgroundColor: '#0f172a', borderBottom: '1px solid #334155' }} elevation={0}>
          <Toolbar>
            <TrendingUp className="text-emerald-500 mr-2" />
            <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold' }}>
              TradeMind AI
            </Typography>
          </Toolbar>
        </AppBar>
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box', backgroundColor: '#0f172a', borderRight: '1px solid #334155', color: 'white' },
          }}
        >
          <Toolbar />
          <Box sx={{ overflow: 'auto', mt: 2 }}>
            <List>
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
                      mb: 1
                    }}
                  >
                    <ListItemIcon sx={{ color: 'slategray', minWidth: 40 }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText primary={item.text} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>
        <Box component="main" sx={{ flexGrow: 1, p: 3, backgroundColor: '#020617', minHeight: '100vh' }}>
          <Toolbar />
          <Container maxWidth="xl">
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
