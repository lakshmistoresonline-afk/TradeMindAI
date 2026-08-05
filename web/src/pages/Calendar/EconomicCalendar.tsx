import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Chip, Stack, List, ListItem, ListItemText, Divider, Alert } from '@mui/material';
import { Calendar, Clock, Globe, Info } from 'lucide-react';

const mockEvents = [
  { time: '11:00 AM', country: 'IN', event: 'RBI Monetary Policy Meeting', impact: 'CRITICAL', forecast: '6.50%', actual: '---' },
  { time: '2:30 PM', country: 'EU', event: 'ECB Press Conference', impact: 'HIGH', forecast: '---', actual: '---' },
  { time: '6:00 PM', country: 'US', event: 'Non-Farm Payrolls', impact: 'CRITICAL', forecast: '185K', actual: '---' },
  { time: 'All Day', country: 'IN', event: 'TCS Quarterly Results', impact: 'MEDIUM', forecast: '₹12.4 EPS', actual: '---' },
];

export default function EconomicCalendar() {
  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" fontWeight="bold">Economic Calendar</Typography>
        <Stack direction="row" spacing={1}>
          <Chip icon={<Globe size={14} />} label="Global" variant="outlined" />
          <Chip icon={<Info size={14} />} label="Market Hours: 09:15 - 15:30 IST" />
        </Stack>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 0 }}>
            <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
              {mockEvents.map((event, index) => (
                <Box key={index}>
                  <ListItem sx={{ py: 2 }}>
                    <Stack direction="row" spacing={3} alignItems="center" sx={{ width: '100%' }}>
                      <Box sx={{ minWidth: 80 }}>
                        <Typography variant="subtitle2" color="textSecondary">{event.time}</Typography>
                      </Box>
                      <Box sx={{ minWidth: 40 }}>
                        <Typography variant="h6">{event.country}</Typography>
                      </Box>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle1" fontWeight="bold">{event.event}</Typography>
                      </Box>
                      <Box sx={{ textAlign: 'right', minWidth: 100 }}>
                        <Chip
                          label={event.impact}
                          size="small"
                          color={event.impact === 'CRITICAL' ? 'error' : event.impact === 'HIGH' ? 'warning' : 'default'}
                          sx={{ fontWeight: 'bold', fontSize: '0.7rem' }}
                        />
                      </Box>
                    </Stack>
                  </ListItem>
                  <Divider />
                </Box>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>AI Market Outlook</Typography>
            <Alert icon={<Info size={18} />} severity="warning" sx={{ mb: 2 }}>
              High volatility expected during RBI policy hours.
            </Alert>
            <Typography variant="body2" color="textSecondary" sx={{ lineHeight: 1.6 }}>
              The consensus suggests no rate hike today, but the commentary on inflation will be key. Institutional positioning shows high hedging in Bank Nifty options.
            </Typography>
          </Paper>

          <Paper sx={{ p: 3 }}>
             <Typography variant="h6" gutterBottom>Upcoming Holidays</Typography>
             <Typography variant="body2">Aug 15 - Independence Day (Closed)</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

import { Grid } from '@mui/material';
