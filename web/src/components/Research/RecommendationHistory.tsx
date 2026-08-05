import { Box, Typography, Paper, Grid, Table, TableBody, TableCell, TableHead, TableRow, Chip } from '@mui/material';
import { History, CheckCircle, XCircle } from 'lucide-react';

export default function RecommendationHistory({ history }: { history: any[] }) {
  if (!history || history.length === 0) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <History size={20} className="text-blue-500" /> AI Recommendation Audit
      </Typography>

      <Paper sx={{ p: 0, overflow: 'hidden' }}>
        <Table size="small">
          <TableHead sx={{ bgcolor: 'rgba(255,255,255,0.02)' }}>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Rating</TableCell>
              <TableCell>Confidence</TableCell>
              <TableCell align="right">Outcome (30D)</TableCell>
              <TableCell align="center">Accuracy</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {history.map((h, i) => (
              <TableRow key={i} hover>
                <TableCell>{h.date}</TableCell>
                <TableCell><Chip label={h.rating} size="small" color={h.rating === 'BUY' ? 'primary' : 'default'} sx={{ fontWeight: 'bold' }} /></TableCell>
                <TableCell>{h.confidence}%</TableCell>
                <TableCell align="right" sx={{ color: h.outcome > 0 ? 'primary.main' : 'error.main', fontWeight: 'bold' }}>
                   {h.outcome > 0 ? '+' : ''}{h.outcome}%
                </TableCell>
                <TableCell align="center">
                  {h.accuracy === 'HIT' ? <CheckCircle size={16} className="text-emerald-500" /> : <XCircle size={16} className="text-rose-500" />}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}
