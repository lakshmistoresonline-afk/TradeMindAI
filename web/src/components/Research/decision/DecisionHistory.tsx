import { Box, Typography, Paper, Table, TableBody, TableCell, TableHead, TableRow, Chip } from '@mui/material';
import { History, Database } from 'lucide-react';

export default function DecisionHistory({ history }: { history?: any[] }) {
  if (!history || history.length === 0) return (
     <Box sx={{ mb: 4 }}>
        <Typography variant="h6" fontWeight={800} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <History size={20} className="text-blue-500" /> Decision History Audit
        </Typography>
        <Paper sx={{ p: 8, textAlign: 'center', bgcolor: 'rgba(15, 23, 42, 0.3)', border: '1px dashed #334155' }}>
           <History size={48} className="opacity-10" style={{ margin: '0 auto 16px' }} />
           <Typography color="textSecondary" sx={{ fontWeight: 600 }}>No Decision History Available</Typography>
           <Typography variant="caption" color="textSecondary">AI snapshots are recorded once daily at market close.</Typography>
        </Paper>
     </Box>
  );

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight={800} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <History size={20} className="text-blue-500" /> Decision History Audit
      </Typography>

      <Paper sx={{ p: 0, overflow: 'hidden', border: '1px solid #1e293b' }}>
        <Table size="small">
          <TableHead sx={{ bgcolor: 'rgba(255,255,255,0.02)' }}>
            <TableRow>
              <TableCell sx={{ pl: 3 }}>Date</TableCell>
              <TableCell>Rating</TableCell>
              <TableCell align="right">Conviction</TableCell>
              <TableCell>Key Thesis</TableCell>
              <TableCell align="center">Provenance</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {history.map((h, i) => (
              <TableRow key={i} hover>
                <TableCell sx={{ fontWeight: 900, pl: 3 }}>{new Date(h.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}</TableCell>
                <TableCell>
                   <Chip
                    label={h.rating || 'HOLD'}
                    size="small"
                    color={h.rating?.includes('BUY') ? 'primary' : h.rating?.includes('SELL') ? 'error' : 'default'}
                    sx={{ fontWeight: 900, height: 18, fontSize: '0.6rem' }}
                   />
                </TableCell>
                <TableCell align="right" sx={{ fontWeight: 800, fontFamily: 'JetBrains Mono' }}>{h.conviction || 50}%</TableCell>
                <TableCell>
                   <Typography variant="caption" color="textSecondary" sx={{ display: '-webkit-box', WebkitLineClamp: 1, WebkitBoxOrient: 'vertical', overflow: 'hidden', fontWeight: 500 }}>
                      {h.thesis || h.desc}
                   </Typography>
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="Historical Snapshot v2.0">
                     <Database size={14} className="text-slategray opacity-50" />
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}

import { Tooltip } from '@mui/material';
