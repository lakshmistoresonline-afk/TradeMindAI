import { useState, useEffect } from 'react';
import { Box, Typography, Paper, List, ListItem, Chip, Stack, Divider, CircularProgress } from '@mui/material';
import { Info } from 'lucide-react';
import { getEconomicCalendar } from '../../api/client';

export default function EconomicCalendar() {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getEconomicCalendar()
      .then(setEvents)
      .finally(() => setLoading(false));
  }, []);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
         <Typography variant="h4" sx={{ fontWeight: 'bold' }}>Global Economic Calendar</Typography>
         <Chip label="Real-time Macro Feed" color="primary" variant="outlined" />
      </Box>

      <Paper sx={{ p: 0 }}>
        {loading ? (
          <Box sx={{ p: 4, textAlign: 'center' }}><CircularProgress /></Box>
        ) : (
          <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
            {events.map((event, index) => (
              <Box key={index}>
                <ListItem sx={{ py: 2 }}>
                   <Grid container alignItems="center" spacing={2}>
                      <Grid item xs={2} md={1}>
                         <Typography variant="body2" fontWeight="bold">{event.time}</Typography>
                      </Grid>
                      <Grid item xs={2} md={1}>
                         <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <img src={`https://flagcdn.com/w20/${event.country.toLowerCase()}.png`} width="20" alt={event.country} />
                            <Typography variant="body2">{event.country}</Typography>
                         </Box>
                      </Grid>
                      <Grid item xs={5} md={6}>
                         <Typography variant="body2" fontWeight="bold">{event.event}</Typography>
                      </Grid>
                      <Grid item xs={3} md={2}>
                         <Chip
                          label={event.impact}
                          size="small"
                          color={event.impact === 'CRITICAL' ? 'error' : event.impact === 'HIGH' ? 'warning' : 'info'}
                          sx={{ fontSize: '0.65rem', height: 20, fontWeight: 'bold' }}
                         />
                      </Grid>
                      <Grid item xs={12} md={2}>
                         <Stack direction="row" spacing={2} sx={{ mt: { xs: 1, md: 0 } }}>
                            <Box>
                               <Typography variant="caption" color="textSecondary" display="block">Forecast</Typography>
                               <Typography variant="body2" sx={{ fontWeight: 500 }}>{event.forecast}</Typography>
                            </Box>
                            <Box>
                               <Typography variant="caption" color="textSecondary" display="block">Actual</Typography>
                               <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'primary.main' }}>{event.actual}</Typography>
                            </Box>
                         </Stack>
                      </Grid>
                   </Grid>
                </ListItem>
                {index < events.length - 1 && <Divider sx={{ opacity: 0.1 }} />}
              </Box>
            ))}
          </List>
        )}
      </Paper>

      <Box sx={{ mt: 4, p: 3, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
         <Info size={20} className="text-blue-400" />
         <Typography variant="body2" color="textSecondary">
            Macro-economic events are weighted by the **AI Risk Agent** to adjust stock-level conviction scores in real-time.
         </Typography>
      </Box>
    </Box>
  );
}

import { Grid } from '@mui/material';
