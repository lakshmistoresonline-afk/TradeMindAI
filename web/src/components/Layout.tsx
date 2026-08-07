import React, { useState, createContext, useContext, useEffect } from 'react';
import { Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Container, Snackbar, Alert, Stack, Chip, Divider } from '@mui/material';
import { LayoutDashboard, LineChart, BrainCircuit, Settings, TrendingUp, PieChart, Bot, Wallet, Calendar, Code, Monitor, Trophy, Star, Book, ShieldCheck, Home } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMediaQuery, useTheme, IconButton, BottomNavigation, BottomNavigationAction, Paper as MuiPaper } from '@mui/material';
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

const menuGroups = [
  {
    title: 'MARKET RADAR',
    items: [
      { text: 'Dashboard', icon: <LayoutDashboard size={18} />, path: '/' },
      { text: 'Live Pulse', icon: <LineChart size={18} />, path: '/market' },
      { text: 'Global Macro', icon: <Calendar size={18} />, path: '/calendar' },
      { text: 'Sector Map', icon: <PieChart size={18} />, path: '/sectors' },
    ]
  },
  {
    title: 'INTELLIGENCE HUB',
    items: [
      { text: 'Stock Forensic', icon: <BrainCircuit size={18} />, path: '/analysis' },
      { text: 'Alpha Scanner', icon: <Trophy size={18} />, path: '/ranking' },
      { text: 'Research Lab', icon: <Book size={18} />, path: '/research' },
      { text: 'AI Chat', icon: <Bot size={18} />, path: '/chat' },
    ]
  },
  {
    title: 'STRATEGY & EXECUTION',
    items: [
      { text: 'Paper Trading', icon: <Wallet size={18} />, path: '/paper-trading' },
      { text: 'Strategy Lab', icon: <Code size={18} />, path: '/strategy' },
      { text: 'Trade Journal', icon: <Book size={18} />, path: '/journal' },
    ]
  },
  {
    title: 'TERMINAL SETTINGS',
    items: [
      { text: 'Control Center', icon: <ShieldCheck size={18} />, path: '/admin' },
      { text: 'Settings', icon: <Settings size={18} />, path: '/settings' },
    ]
  }
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
            <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold', mr: 2, display: { xs: 'none', sm: 'block' } }}>
              TradeMind AI
            </Typography>

            {!isMobile && (
              <Box sx={{ bgcolor: 'rgba(255,255,255,0.05)', px: 1.5, py: 0.5, borderRadius: 1, border: '1px solid #334155' }}>
                <Typography variant="caption" sx={{ fontWeight: 'bold', color: 'primary.main', display: 'flex', alignItems: 'center', gap: 0.5 }}>
                   <Calendar size={12} /> {new Date().toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                </Typography>
              </Box>
            )}

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
            {menuGroups.map((group) => (
              <List
                key={group.title}
                subheader={
                  <Typography
                    variant="caption"
                    sx={{ p: 2, pb: 1, color: 'slategray', fontWeight: 700, letterSpacing: 1.2, display: 'block' }}
                  >
                    {group.title}
                  </Typography>
                }
              >
                {group.items.map((item) => (
                  <ListItem key={item.text} disablePadding>
                    <ListItemButton
                      onClick={() => navigate(item.path)}
                      selected={location.pathname === item.path}
                      sx={{
                        '&.Mui-selected': { backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#10b981' },
                        '&.Mui-selected .MuiListItemIcon-root': { color: '#10b981' },
                        mx: 1,
                        borderRadius: 1,
                        mb: 0.5,
                        py: 0.75
                      }}
                    >
                      <ListItemIcon sx={{ color: 'slategray', minWidth: 36 }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.text}
                        primaryTypographyProps={{
                          variant: 'body2',
                          fontWeight: location.pathname === item.path ? 700 : 500,
                          fontSize: '0.825rem'
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
                ))}
                <Divider sx={{ mx: 2, my: 1, opacity: 0.05 }} />
              </List>
            ))}

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

        {isMobile && (
          <MuiPaper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 1200 }} elevation={3}>
            <BottomNavigation
              showLabels
              value={location.pathname}
              onChange={(_, newValue) => navigate(newValue)}
              sx={{ bgcolor: '#0f172a', borderTop: '1px solid #1e293b' }}
            >
              <BottomNavigationAction label="Market" value="/" icon={<Home size={20} />} />
              <BottomNavigationAction label="Forensic" value="/analysis" icon={<BrainCircuit size={20} />} />
              <BottomNavigationAction label="Pulse" value="/market" icon={<LineChart size={20} />} />
              <BottomNavigationAction label="Chat" value="/chat" icon={<Bot size={20} />} />
            </BottomNavigation>
          </MuiPaper>
        )}
      </Box>
    </NotificationContext.Provider>
  );
}
