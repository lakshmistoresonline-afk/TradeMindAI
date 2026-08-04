import { Box, Typography, Paper, Switch, List, ListItem, ListItemText, ListItemSecondaryAction, Divider, Button, TextField } from '@mui/material';
import { Save, Bell, Shield, Moon, Globe } from 'lucide-react';

export default function Settings() {
  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>Settings</Typography>

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

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>API & Integration</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 2 }}>
              <TextField
                fullWidth
                label="Groq API Key"
                type="password"
                placeholder="gsk_xxxxxxxxxxxxxxxxxxxx"
                variant="outlined"
                helperText="Stored in your local environment"
              />
              <TextField
                fullWidth
                label="Firebase Project ID"
                value="com-webcraft-trademindai-c8f75"
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
          <Card sx={{ backgroundColor: 'rgba(16, 185, 129, 0.05)', border: '1px solid #10b981' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, color: '#10b981' }}>
                <Shield size={20} />
                <Typography variant="subtitle1" fontWeight="bold">Account Security</Typography>
              </Box>
              <Typography variant="body2" color="textSecondary">
                Your data is stored securely in your private Google Cloud instance. No trading data is shared with 3rd parties.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

import { Grid, Card, CardContent, ListItemIcon } from '@mui/material';
