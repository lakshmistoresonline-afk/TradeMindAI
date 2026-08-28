import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableHead, TableRow, Chip, TableContainer } from '@mui/material';
import { getEconomicCalendar } from '../../api/client';

export default function MacroCalendar() {
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    getEconomicCalendar().then(setEvents);
  }, []);

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>Macro Calendar</Typography>

      <Paper sx={{ p: 0, overflow: 'hidden' }}>
        <TableContainer component={Box}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ pl: 3 }}>TIME</TableCell>
                <TableCell>COUNTRY</TableCell>
                <TableCell>EVENT</TableCell>
                <TableCell align="center">IMPACT</TableCell>
                <TableCell align="right">FORECAST</TableCell>
                <TableCell align="right">ACTUAL</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {events.map((e, i) => (
                <TableRow key={i} hover>
                  <TableCell sx={{ pl: 3, color: 'text.secondary', fontWeight: 'bold' }}>{e.time}</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>{e.country}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>{e.event}</TableCell>
                  <TableCell align="center">
                    <Chip
                      label={e.impact}
                      size="small"
                      color={e.impact === 'CRITICAL' ? 'error' : e.impact === 'HIGH' ? 'warning' : 'default'}
                      sx={{ fontWeight: 'bold', fontSize: '0.65rem' }}
                    />
                  </TableCell>
                  <TableCell align="right">{e.forecast}</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold' }}>{e.actual}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
