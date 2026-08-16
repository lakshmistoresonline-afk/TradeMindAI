import React, { useState, useEffect, createContext, useContext } from 'react';
import { Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Container, Snackbar, Alert, Stack, Divider, Button, Chip, Menu, MenuItem, IconButton, Avatar, alpha, Paper } from '@mui/material';
import {
  LayoutDashboard,
  Zap,
  History,
  Search,
  Bot,
  Settings,
  LogOut,
  Activity,
  Menu as MenuIcon,
  ChevronDown,
  X,
  TrendingUp,
  LineChart,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMediaQuery, useTheme, Fab } from '@mui/material';
import CommandPalette from './CommandPalette';
import AICopilot from '../pages/AICopilot';
import { API_BASE_URL, getMarketStats } from '../api/client';

const drawerWidth = 260;

// Notification Context
export const NotificationContext = createContext({
  showNotification: (_message: string, _severity: 'success' | 'error' | 'info' | 'warning') => {},
  setCopilotContext: (_context: any) => {}
});

export const useNotification = () => useContext(NotificationContext);

const menuItems = [
  { text: 'TERMINAL', icon: <LayoutDashboard size={20} />, path: '/' },
  { text: 'EQUITY SIGNALS', icon: <Activity size={20} />, path: '/signals/equity' },
  { text: 'FUTURES SIGNALS', icon: <TrendingUp size={20} />, path: '/signals/futures' },
  { text: 'OPTIONS SIGNALS', icon: <Zap size={20} />, path: '/signals/options' },
  { text: 'AUDIT ARCHIVE', icon: <History size={20} />, path: '/history' },
  { text: 'LABORATORY', icon: <Search size={20} />, path: '/analysis' },
  { text: 'MARKET PULSE', icon: <LineChart size={20} />, path: '/market' },
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
  const [marketStats, setMarketStats] = useState<any>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  useEffect(() => {
    getMarketStats().then(data => {
       if (data) setMarketStats(data);
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

  const handleProfileClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileClose = () => {
    setAnchorEl(null);
  };

  const currentPath = location.pathname + location.search;

  return (
    <NotificationContext.Provider value={{ showNotification, setCopilotContext }}>
      <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#020617' }}>
        <CommandPalette />
        <AppBar
          position="fixed"
          sx={{
            zIndex: (theme) => theme.zIndex.drawer + 1,
            backgroundColor: 'rgba(7, 10, 15, 0.8)',
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
                <Box sx={{ bgcolor: 'primary.main', color: '#000', px: 1, borderRadius: 0.5, fontSize: '0.8rem', fontWeight: 900 }}>TM</Box>
                TRADEMIND AI
                <Chip
                  label="LIVE"
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

              {!isMobile && marketStats && (
                <Stack direction="row" spacing={4} sx={{ ml: 6 }}>
                   <MarketTickerCompact label="NIFTY" stats={marketStats['NIFTY 50']} />
                   <MarketTickerCompact label="BNIFTY" stats={marketStats['BANK NIFTY']} />
                   <MarketTickerCompact label="VIX" stats={marketStats['India VIX']} />
                </Stack>
              )}
            </Stack>

            <Stack direction="row" spacing={2} alignItems="center">
              {!isMobile && (
                <Stack direction="row" spacing={1} sx={{ mr: 4 }}>
                   <HeaderStatus label="SYSTEM" value="OPTIMIZED" color="#10b981" />
                   <HeaderStatus label="AUDIT" value="ACTIVE" color="#00D1FF" />
                </Stack>
              )}

              <IconButton onClick={handleProfileClick} sx={{ p: 0.5, border: '1px solid rgba(255,255,255,0.08)', borderRadius: 1 }}>
                <Avatar sx={{ width: 28, height: 28, bgcolor: 'secondary.main', fontSize: '0.7rem', fontWeight: 900, borderRadius: 0.5 }}>SR</Avatar>
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
                  <Typography variant="subtitle2" sx={{ fontWeight: 950, color: '#fff' }}>TradeMind Pro</Typography>
                  <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 700 }}>Alpha Tier Node: 7421</Typography>
                </Box>
                <Divider sx={{ opacity: 0.05 }} />
                <MenuItem onClick={() => { handleProfileClose(); navigate('/settings'); }} sx={{ py: 1.5 }}>
                  <ListItemIcon><Settings size={18} color="slategray" /></ListItemIcon>
                  <ListItemText primary="Terminal Settings" primaryTypographyProps={{ variant: 'body2', fontWeight: 800, color: 'slategray' }} />
                </MenuItem>
                <MenuItem onClick={() => { handleProfileClose(); navigate('/admin'); }} sx={{ py: 1.5 }}>
                  <ListItemIcon><Activity size={18} color="slategray" /></ListItemIcon>
                  <ListItemText primary="System Status" primaryTypographyProps={{ variant: 'body2', fontWeight: 800, color: 'slategray' }} />
                </MenuItem>
                <Divider sx={{ opacity: 0.05 }} />
                <MenuItem onClick={handleProfileClose} sx={{ color: 'error.main', py: 1.5 }}>
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
               {menuItems.map((item) => (
                 <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                    <ListItemButton
                      onClick={() => { navigate(item.path); if (isMobile) setDrawerOpen(false); }}
                      selected={currentPath === item.path || (location.pathname.startsWith(item.path))}
                      sx={{
                        borderRadius: 1,
                        py: 1.4,
                        '&.Mui-selected': {
                          backgroundColor: alpha('#00D1FF', 0.08),
                          color: 'primary.main',
                          '& .MuiListItemIcon-root': { color: 'primary.main' },
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
            </List>

            <Box sx={{ mt: 'auto', p: 3, borderTop: '1px solid rgba(255,255,255,0.05)' }}>
               <Paper sx={{ p: 2, bgcolor: alpha('#7C3AED', 0.05), border: '1px solid rgba(124, 58, 237, 0.1)', borderRadius: 1 }}>
                  <Typography variant="caption" sx={{ fontWeight: 900, color: 'secondary.main', display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                     <Bot size={14} /> AI CORE V2.2
                  </Typography>
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={() => setCopilotOpen(true)}
                    sx={{
                      borderRadius: 0.5,
                      bgcolor: 'secondary.main',
                      color: '#fff',
                      fontWeight: 950,
                      fontSize: '0.7rem',
                      '&:hover': { bgcolor: alpha('#7C3AED', 0.8) }
                    }}
                  >
                    INITIATE CONTEXT
                  </Button>
               </Paper>
            </Box>
          </Box>
        </Drawer>

        <Drawer
          anchor="right"
          open={copilotOpen}
          onClose={() => setCopilotOpen(false)}
          sx={{ [`& .MuiDrawer-paper`]: { width: { xs: '100%', sm: 500 }, backgroundColor: '#020617', borderLeft: '1px solid rgba(255,255,255,0.1)', backgroundImage: 'none' } }}
        >
           <Box sx={{ p: 2.5, borderBottom: '1px solid rgba(255,255,255,0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', bgcolor: '#070a0f' }}>
              <Stack direction="row" spacing={2} alignItems="center">
                 <Box sx={{ bgcolor: alpha('#10b981', 0.1), p: 1, borderRadius: 0.5 }}>
                    <Bot size={20} color="#10b981" />
                 </Box>
                 <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 950, letterSpacing: -0.5, color: '#fff' }}>SYSTEM ANALYST</Typography>
                    <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 800 }}>MULTI-AGENT CONSENSUS ACTIVE</Typography>
                 </Box>
              </Stack>
              <IconButton onClick={() => setCopilotOpen(false)} sx={{ color: 'slategray' }}><X size={20} /></IconButton>
           </Box>
           <Box sx={{ height: 'calc(100% - 80px)' }}>
              <AICopilot isDrawer stockContext={copilotContext} />
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

        {!isMobile && (
           <Fab
             color="primary"
             onClick={() => setCopilotOpen(true)}
             sx={{
                position: 'fixed',
                bottom: 40,
                right: 40,
                zIndex: 1000,
                width: 60,
                height: 60,
                boxShadow: '0 0 30px rgba(0, 209, 255, 0.3)',
                '&:hover': { transform: 'scale(1.05) rotate(5deg)' },
                transition: '0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
                borderRadius: 1.5,
                bgcolor: '#00D1FF'
             }}
           >
             <Bot size={28} color="#000" />
           </Fab>
        )}
      </Box>
    </NotificationContext.Provider>
  );
}

function MarketTickerCompact({ label, stats }: any) {
  if (!stats) return null;
  const isPositive = stats.change >= 0;
  return (
    <Box sx={{ borderLeft: '1px solid rgba(255,255,255,0.08)', pl: 2 }}>
      <Typography variant="caption" sx={{ color: 'slategray', fontWeight: 900, display: 'block', fontSize: '0.55rem', mb: 0.2 }}>{label}</Typography>
      <Stack direction="row" spacing={1.5} alignItems="center">
        <Typography sx={{ fontWeight: 900, fontFamily: 'JetBrains Mono', fontSize: '0.8rem', color: '#fff' }}>{stats.value.toLocaleString()}</Typography>
        <Stack direction="row" alignItems="center" spacing={0.2}>
          {isPositive ? <ArrowUpRight size={10} color="#10b981" /> : <ArrowDownRight size={10} color="#ef4444" />}
          <Typography sx={{ color: isPositive ? '#10b981' : '#ef4444', fontWeight: 950, fontSize: '0.65rem' }}>
            {stats.change}%
          </Typography>
        </Stack>
      </Stack>
    </Box>
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
