import { Box, Typography, Paper, Table, TableBody, TableCell, TableHead, TableRow, Chip } from '@mui/material';
import { History, CheckCircle } from 'lucide-react';

export default function RecommendationHistory({ history }: { history: any[] }) {
  if (!history || history.length === 0) return (
     <Box sx={{ mb: 4 }}>
        <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <History size={20} className="text-blue-500" /> AI Recommendation Audit
        </Typography>
        <Paper sx={{ p: 4, textAlign: 'center' }}><Typography color="textSecondary">No historical ratings found.</Typography></Paper>
     </Box>
  );

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
              <TableCell>Thesis Summary</TableCell>
              <TableCell align="center">Source</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {history.map((h, i) => (
              <TableRow key={i} hover>
                <TableCell sx={{ fontWeight: 'bold' }}>{new Date(h.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</TableCell>
                <TableCell>
                   <Chip
                    label={h.title.split(': ')[1] || h.title}
                    size="small"
                    color={h.title.includes('AAA') || h.title.includes('A') ? 'primary' : 'default'}
                    sx={{ fontWeight: 'bold' }}
                   />
                </TableCell>
                <TableCell>
                   <Typography variant="caption" color="textSecondary" sx={{ display: '-webkit-box', WebkitLineClamp: 1, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                      {h.desc}
                   </Typography>
                </TableCell>
                <TableCell align="center">
                  <CheckCircle size={16} className="text-emerald-500" />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}
