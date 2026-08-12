import React, { useState, useEffect, createContext, useContext } from 'react';
import { Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Container, Snackbar, Alert, Stack, Divider, Button } from '@mui/material';
import { LineChart, Wallet, History, Bot, Star, Activity, Zap, X, TrendingUp, Settings } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMediaQuery, useTheme, IconButton, BottomNavigation, BottomNavigationAction, Paper as MuiPaper, Fab } from '@mui/material';
import { Menu as MenuIcon } from 'lucide-react';
import CommandPalette from './CommandPalette';
import AICopilot from '../pages/AICopilot';
import { API_BASE_URL, getMarketStats } from '../api/client';

const drawerWidth = 240;

// Notification Context
export const NotificationContext = createContext({
  showNotification: (_message: string, _severity: 'success' | 'error' | 'info' | 'warning') => {}
});

export const useNotification = () => useContext(NotificationContext);

const primaryMenu = [
  { text: 'SIGNALS', icon: <Zap size={20} />, path: '/' },
  { text: 'MARKET', icon: <LineChart size={20} />, path: '/market' },
  { text: 'PORTFOLIO', icon: <Wallet size={20} />, path: '/portfolio' },
  { text: 'HISTORY', icon: <History size={20} />, path: '/history' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [copilotOpen, setCopilotOpen] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' as any });
  const [marketBrief, setMarketBrief] = useState<any>(null);
  const [pinnedStocks] = useState<string[]>(['RELIANCE', 'TCS', 'HDFCBANK']);

  useEffect(() => {
    getMarketStats().then(data => {
       const nifty = data?.['NIFTY 50'];
       if (nifty) setMarketBrief(nifty);
    }).catch(() => {});
  }, []);

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
                        NIFTY {marketBrief ? `${marketBrief.value.toLocaleString()} (${marketBrief.change >= 0 ? '+' : ''}${marketBrief.change}%)` : '24,560.15 (+0.6%)'}
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
          <Box sx={{ overflow: 'auto', mt: 4 }}>
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

            <Divider sx={{ mx: 2, my: 3, opacity: 0.1 }} />

            <List subheader={<Typography variant="caption" sx={{ p: 2, color: 'slategray', fontWeight: 800, letterSpacing: 1.5, fontSize: '0.65rem' }}>FAVORITES</Typography>}>
               {pinnedStocks.map(symbol => (
                 <ListItem key={symbol} disablePadding>
                    <ListItemButton
                      onClick={() => navigate('/analysis', { state: { symbol } })}
                      sx={{ mx: 1.5, borderRadius: 1, mb: 1 }}
                    >
                       <ListItemIcon sx={{ color: 'primary.main', minWidth: 32 }}><Star size={16} /></ListItemIcon>
                       <ListItemText primary={symbol} primaryTypographyProps={{ variant: 'body2', fontWeight: 800 }} />
                    </ListItemButton>
                 </ListItem>
               ))}
            </List>

            <Box sx={{ mt: 'auto', pb: 2 }}>
               <Divider sx={{ mx: 2, mb: 2, opacity: 0.05 }} />
               <List>
                  <ListItem disablePadding>
                     <ListItemButton onClick={() => navigate('/admin')} sx={{ mx: 1.5, borderRadius: 1 }}>
                        <ListItemIcon sx={{ color: 'slategray', minWidth: 32 }}><Activity size={18} /></ListItemIcon>
                        <ListItemText primary="Data Health" primaryTypographyProps={{ variant: 'caption', fontWeight: 800 }} />
                     </ListItemButton>
                  </ListItem>
                  <ListItem disablePadding>
                     <ListItemButton onClick={() => navigate('/settings')} sx={{ mx: 1.5, borderRadius: 1 }}>
                        <ListItemIcon sx={{ color: 'slategray', minWidth: 32 }}><Settings size={18} /></ListItemIcon>
                        <ListItemText primary="Settings" primaryTypographyProps={{ variant: 'caption', fontWeight: 800 }} />
                     </ListItemButton>
                  </ListItem>
               </List>

               <Box sx={{ px: 2, mt: 2 }}>
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
          </Box>
        </Drawer>

        {/* Global AI Copilot Drawer */}
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
              <AICopilot isDrawer />
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
              value={location.pathname === '/' ? '/' : `/${location.pathname.split('/')[1]}`}
              onChange={(_, newValue) => navigate(newValue)}
              sx={{ bgcolor: '#0f172a', borderTop: '1px solid #1e293b' }}
            >
              <BottomNavigationAction label="Signals" value="/" icon={<Zap size={20} />} />
              <BottomNavigationAction label="Market" value="/market" icon={<LineChart size={20} />} />
              <BottomNavigationAction label="Portfolio" value="/portfolio" icon={<Wallet size={20} />} />
              <BottomNavigationAction label="History" value="/history" icon={<History size={20} />} />
            </BottomNavigation>
          </MuiPaper>
        )}

        {/* Global Floating Copilot Action */}
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
