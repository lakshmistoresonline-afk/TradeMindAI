import React, { useState, useEffect, createContext, useContext } from 'react';
import { Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Container, Snackbar, Alert, Stack, Divider } from '@mui/material';
import { LayoutDashboard, LineChart, BrainCircuit, Settings, TrendingUp, PieChart, Bot, Wallet, Calendar, Code, Trophy, Star, Book, ShieldCheck, Home, Activity, Zap } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMediaQuery, useTheme, IconButton, BottomNavigation, BottomNavigationAction, Paper as MuiPaper } from '@mui/material';
import { Menu as MenuIcon } from 'lucide-react';
import CommandPalette from './CommandPalette';
import { API_BASE_URL } from '../api/client';

const drawerWidth = 240;

// Notification Context
export const NotificationContext = createContext({
  showNotification: (_message: string, _severity: 'success' | 'error' | 'info' | 'warning') => {}
});

export const useNotification = () => useContext(NotificationContext);

const menuGroups = [
  {
    title: 'MARKET',
    items: [
      { text: 'Command Center', icon: <LayoutDashboard size={18} />, path: '/' },
      { text: 'Market Pulse', icon: <LineChart size={18} />, path: '/market' },
      { text: 'Macro Calendar', icon: <Calendar size={18} />, path: '/calendar' },
      { text: 'Sector Rotation', icon: <PieChart size={18} />, path: '/sectors' },
    ]
  },
  {
    title: 'INTELLIGENCE',
    items: [
      { text: 'Opportunity Scanner', icon: <Trophy size={18} />, path: '/ranking' },
      { text: 'Stock Intelligence', icon: <BrainCircuit size={18} />, path: '/analysis' },
      { text: 'Research Hub', icon: <Book size={18} />, path: '/research' },
      { text: 'AI Copilot', icon: <Bot size={18} />, path: '/chat' },
    ]
  },
  {
    title: 'PORTFOLIO',
    items: [
      { text: 'Overview', icon: <Wallet size={18} />, path: '/portfolio' },
      { text: 'Risk Guard', icon: <ShieldCheck size={18} />, path: '/risk' },
      { text: 'Stress Test', icon: <Activity size={18} />, path: '/stress-test' },
    ]
  },
  {
    title: 'TRADING',
    items: [
      { text: 'Strategy Lab', icon: <Code size={18} />, path: '/strategy' },
      { text: 'Signal Audit', icon: <Star size={18} />, path: '/paper-trading' },
      { text: 'Trade Journal', icon: <Book size={18} />, path: '/journal' },
    ]
  },
  {
    title: 'SYSTEM',
    items: [
      { text: 'Data Health', icon: <Activity size={18} />, path: '/admin' },
      { text: 'Settings', icon: <Settings size={18} />, path: '/settings' },
    ]
  }
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' as any });
  const [pinnedStocks] = useState<string[]>(['RELIANCE', 'TCS', 'HDFCBANK']);

  useEffect(() => {
    // Vision 2.2: Real-time Forensic Signal Stream
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
            <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 800, mr: 3, display: { xs: 'none', sm: 'block' }, letterSpacing: -0.5 }}>
              TRADEMIND AI
            </Typography>

            {!isMobile && (
              <Stack direction="row" spacing={3} sx={{ flexGrow: 1, ml: 4 }}>
                 <StatusIndicator label="SYSTEM" status="OPTIMAL" icon={<Activity size={14} />} color="#10b981" />
                 <StatusIndicator label="AI QUOTA" status="STABLE" icon={<Zap size={14} />} color="#3b82f6" />
              </Stack>
            )}

            {!isMobile && (
               <Stack direction="row" spacing={2} alignItems="center">
                  <Box sx={{ bgcolor: 'rgba(255,255,255,0.03)', px: 2, py: 0.75, borderRadius: 1, border: '1px solid #1e293b' }}>
                     <Typography variant="caption" sx={{ fontWeight: 900, color: 'primary.main', fontFamily: 'JetBrains Mono', letterSpacing: 1 }}>
                        NIFTY 24,560.15 (+0.6%)
                     </Typography>
                  </Box>
                  <Box sx={{ bgcolor: 'rgba(255,255,255,0.05)', px: 1.5, py: 0.5, borderRadius: 1, border: '1px solid #334155' }}>
                     <Typography variant="caption" sx={{ fontWeight: 800, color: 'text.secondary', fontFamily: 'JetBrains Mono' }}>
                        {new Date().toLocaleDateString(undefined, { month: 'short', day: 'numeric' }).toUpperCase()}
                     </Typography>
                  </Box>
               </Stack>
            )}
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
                    sx={{ p: 2, pb: 1, color: 'slategray', fontWeight: 800, letterSpacing: 1.5, display: 'block', fontSize: '0.65rem' }}
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
                        py: 0.5
                      }}
                    >
                      <ListItemIcon sx={{ color: 'slategray', minWidth: 32 }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.text}
                        primaryTypographyProps={{
                          variant: 'body2',
                          fontWeight: location.pathname === item.path ? 800 : 500,
                          fontSize: '0.8rem'
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
                ))}
                <Divider sx={{ mx: 2, my: 1, opacity: 0.05 }} />
              </List>
            ))}

            <List subheader={<Typography variant="caption" sx={{ p: 2, color: 'slategray', fontWeight: 800, letterSpacing: 1, fontSize: '0.65rem' }}>PINNED</Typography>}>
               {pinnedStocks.map(symbol => (
                 <ListItem key={symbol} disablePadding>
                    <ListItemButton
                      onClick={() => navigate('/analysis', { state: { symbol } })}
                      sx={{ mx: 1, borderRadius: 1, mb: 0.5 }}
                    >
                       <ListItemIcon sx={{ color: 'primary.main', minWidth: 32 }}><Star size={16} /></ListItemIcon>
                       <ListItemText primary={symbol} primaryTypographyProps={{ variant: 'body2', fontWeight: 800 }} />
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
          <Alert onClose={handleClose} severity={notification.severity} sx={{ width: '100%', borderRadius: 1, fontWeight: 700 }}>
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
              <BottomNavigationAction label="Home" value="/" icon={<Home size={20} />} />
              <BottomNavigationAction label="Markets" value="/market" icon={<LineChart size={20} />} />
              <BottomNavigationAction label="Signals" value="/ranking" icon={<Trophy size={20} />} />
              <BottomNavigationAction label="Portfolio" value="/portfolio" icon={<Wallet size={20} />} />
              <BottomNavigationAction label="AI" value="/chat" icon={<Bot size={20} />} />
            </BottomNavigation>
          </MuiPaper>
        )}
      </Box>
    </NotificationContext.Provider>
  );
}

function StatusIndicator({ label, status, icon, color }: any) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, px: 2, py: 0.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 1, border: '1px solid rgba(255,255,255,0.05)' }}>
       <Box sx={{ color }}>{icon}</Box>
       <Box>
          <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800, display: 'block', fontSize: '0.6rem', lineHeight: 1 }}>{label}</Typography>
          <Typography variant="caption" sx={{ color, fontWeight: 900, fontSize: '0.65rem' }}>{status}</Typography>
       </Box>
    </Box>
  );
}
