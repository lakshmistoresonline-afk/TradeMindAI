import React from 'react';
import { Box, AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Container } from '@mui/material';
import { LayoutDashboard, LineChart, BrainCircuit, Settings, TrendingUp } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: <LayoutDashboard size={20} />, path: '/' },
  { text: 'Market', icon: <LineChart size={20} />, path: '/market' },
  { text: 'AI Analysis', icon: <BrainCircuit size={20} />, path: '/analysis' },
  { text: 'Settings', icon: <Settings size={20} />, path: '/settings' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
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
    </Box>
  );
}
