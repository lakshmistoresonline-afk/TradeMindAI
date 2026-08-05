import { useEffect, useState } from 'react';
import { Box, Typography, Paper, Tabs, Tab, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';
import { Trophy, TrendingUp, DollarSign, Zap } from 'lucide-react';
import { getStocks } from '../api/client';

export default function Ranking() {
  const [tab, setTab] = useState(0);
  const [stocks, setStocks] = useState<any[]>([]);

  useEffect(() => {
    getStocks().then(setStocks);
  }, []);

  const getRankedData = () => {
    switch (tab) {
      case 0: return [...stocks].sort((a,b) => (b.ai_investment_score || 0) - (a.ai_investment_score || 0));
      case 1: return [...stocks].sort((a,b) => (b.change_pct || 0) - (a.change_pct || 0));
      case 2: return [...stocks].sort((a,b) => (a.pe_ratio || 999) - (b.pe_ratio || 999));
      default: return stocks;
    }
  };

  const data = getRankedData().slice(0, 10);

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 4 }}>
         <Trophy size={32} className="text-amber-500" />
         <Typography variant="h4" sx={{ fontWeight: 'bold' }}>AI Ranking Engine</Typography>
      </Box>

      <Paper sx={{ p: 0, overflow: 'hidden' }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ px: 2, pt: 2, borderBottom: '1px solid #334155' }}>
           <Tab label="Top AI Confidence" icon={<Zap size={16} />} iconPosition="start" />
           <Tab label="Best Momentum" icon={<TrendingUp size={16} />} iconPosition="start" />
           <Tab label="Value Leaders" icon={<DollarSign size={16} />} iconPosition="start" />
        </Tabs>

        <TableContainer>
           <Table>
              <TableHead>
                 <TableRow>
                    <TableCell align="center">RANK</TableCell>
                    <TableCell>SYMBOL</TableCell>
                    <TableCell align="right">AI SCORE</TableCell>
                    <TableCell align="right">CHANGE %</TableCell>
                    <TableCell align="right">P/E RATIO</TableCell>
                    <TableCell align="center">INVESTMENT GRADE</TableCell>
                 </TableRow>
              </TableHead>
              <TableBody>
                 {data.map((s, i) => (
                   <TableRow key={s.symbol} hover>
                      <TableCell align="center">
                         {i === 0 ? <Typography variant="h5">🥇</Typography> : i === 1 ? <Typography variant="h5">🥈</Typography> : i === 2 ? <Typography variant="h5">🥉</Typography> : i+1}
                      </TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>{s.symbol}</TableCell>
                      <TableCell align="right">
                         <Typography color="primary" fontWeight="bold">{s.ai_investment_score || '--'}</Typography>
                      </TableCell>
                      <TableCell align="right" sx={{ color: s.change_pct >= 0 ? 'primary.main' : 'error.main' }}>
                         {s.change_pct?.toFixed(2)}%
                      </TableCell>
                      <TableCell align="right">{s.pe_ratio?.toFixed(1) || '--'}</TableCell>
                      <TableCell align="center">
                         <Chip label={s.ai_investment_grade || 'B'} color="primary" size="small" variant="outlined" sx={{ fontWeight: 'bold' }} />
                      </TableCell>
                   </TableRow>
                 ))}
              </TableBody>
           </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
