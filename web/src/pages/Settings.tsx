import { Box, Typography, Paper, Switch, List, ListItem, ListItemText, ListItemSecondaryAction, Divider, Button, TextField, Grid, Card, CardContent, ListItemIcon, Chip } from '@mui/material';
import { Save, Bell, Shield, Moon, Globe, Smartphone, LogOut, Key, Code } from 'lucide-react';
import { useState, useEffect } from 'react';
import { getAPIKeys, generateAPIKey } from '../api/client';

export default function Settings() {
  const [devices] = useState<any[]>([
    { id: 'dev-1', name: 'Windows Workstation', location: 'Mumbai, IN', current: true },
    { id: 'dev-2', name: 'iPhone 15 Pro', location: 'Mumbai, IN', current: false },
  ]);

  const [apiKeys, setApiKeys] = useState<any[]>([]);

  useEffect(() => {
     getAPIKeys().then(setApiKeys);
  }, []);

  const handleGenerateKey = async () => {
     const newKey = await generateAPIKey();
     setApiKeys([...apiKeys, newKey]);
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>Enterprise Settings</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ mb: 3 }}>
            <List subheader={<Typography variant="h6" sx={{ p: 2, pb: 0 }}>General Configuration</Typography>}>
              <ListItem>
                <ListItemIcon><Moon size={20} /></ListItemIcon>
                <ListItemText primary="Dark Mode" secondary="Switch between dark and light themes" />
                <ListItemSecondaryAction>
                  <Switch checked />
                </ListItemSecondaryAction>
              </ListItem>
              <Divider variant="inset" component="li" />
              <ListItem>
                <ListItemIcon><Bell size={20} /></ListItemIcon>
                <ListItemText primary="Push Notifications" secondary="Get alerts for AI BUY/SELL signals" />
                <ListItemSecondaryAction>
                  <Switch checked />
                </ListItemSecondaryAction>
              </ListItem>
              <Divider variant="inset" component="li" />
              <ListItem>
                <ListItemIcon><Globe size={20} /></ListItemIcon>
                <ListItemText primary="Auto-Refresh Data" secondary="Refresh market stats every 60 seconds" />
                <ListItemSecondaryAction>
                  <Switch />
                </ListItemSecondaryAction>
              </ListItem>
            </List>
          </Paper>

          {/* Module 24.8: Device Registration & Management */}
          <Paper sx={{ mb: 3 }}>
             <List subheader={<Typography variant="h6" sx={{ p: 2, pb: 0 }}>Security & Authorized Devices</Typography>}>
                {devices.map((dev) => (
                  <Box key={dev.id}>
                    <ListItem>
                       <ListItemIcon><Smartphone size={20} /></ListItemIcon>
                       <ListItemText
                        primary={dev.name}
                        secondary={dev.location}
                        primaryTypographyProps={{ fontWeight: 'bold' }}
                       />
                       <Box sx={{ mr: 2 }}>
                          {dev.current && <Chip label="CURRENT" size="small" color="primary" sx={{ fontSize: '0.6rem' }} />}
                       </Box>
                       <Button size="small" color="error" startIcon={<LogOut size={14} />}>Revoke</Button>
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </Box>
                ))}
                <ListItem sx={{ p: 2 }}>
                   <Button variant="outlined" fullWidth startIcon={<Key size={18} />}>Enable Two-Factor Authentication</Button>
                </ListItem>
             </List>
          </Paper>

          <Paper sx={{ mb: 3 }}>
             <List subheader={<Typography variant="h6" sx={{ p: 2, pb: 0 }}>Programmatic Access (API Keys)</Typography>}>
                {apiKeys.map((key) => (
                  <Box key={key.id}>
                    <ListItem>
                       <ListItemIcon><Code size={20} /></ListItemIcon>
                       <ListItemText
                        primary={key.name}
                        secondary={`Created: ${new Date(key.created_at).toLocaleDateString()}`}
                       />
                       <Typography variant="body2" sx={{ mr: 2, fontFamily: 'monospace', bgcolor: 'rgba(255,255,255,0.05)', p: 0.5, borderRadius: 1 }}>{key.key_prefix}</Typography>
                       <Button size="small" color="error">Delete</Button>
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </Box>
                ))}
                <ListItem sx={{ p: 2 }}>
                   <Button variant="contained" fullWidth onClick={handleGenerateKey}>Generate New API Key</Button>
                </ListItem>
             </List>
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>API & Integration</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 2 }}>
              <TextField
                fullWidth
                label="Groq API Key"
                type="password"
                placeholder="gsk_xxxxxxxxxxxxxxxxxxxx"
                variant="outlined"
                helperText="Used for multi-agent institutional analysis"
              />
              <TextField
                fullWidth
                label="Environment Mode"
                value="Enterprise AI-IOS v2.0"
                variant="outlined"
                disabled
              />
              <Button variant="contained" startIcon={<Save size={18} />} sx={{ alignSelf: 'flex-start' }}>
                Save Changes
              </Button>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ backgroundColor: 'rgba(16, 185, 129, 0.05)', border: '1px solid #10b981', mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, color: '#10b981' }}>
                <Shield size={20} />
                <Typography variant="subtitle1" fontWeight="bold">Account Security</Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ lineHeight: 1.6 }}>
                TradeMind AI follows the **Security-First Architecture**. Your session is encrypted using industry-standard JWT and your data remains private within your personal Firestore instance.
              </Typography>
            </CardContent>
          </Card>

          <Paper sx={{ p: 3 }}>
             <Typography variant="subtitle2" color="textSecondary" gutterBottom>DATA USAGE</Typography>
             <Box sx={{ mt: 2 }}>
                <UsageRow label="Cloud Storage" value="12.4 MB" />
                <UsageRow label="Daily API Calls" value="142 / 1000" />
                <UsageRow label="ML Models Active" value="100" />
             </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function UsageRow({ label, value }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
       <Typography variant="caption">{label}</Typography>
       <Typography variant="caption" fontWeight="bold">{value}</Typography>
    </Box>
  );
}
