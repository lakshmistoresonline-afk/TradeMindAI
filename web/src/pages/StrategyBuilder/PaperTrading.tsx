import { useState } from 'react';
import { Box, Typography, Paper, Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Card, CardContent } from '@mui/material';
import { Wallet, TrendingUp, ArrowUpRight } from 'lucide-react';

export default function PaperTrading() {
  const [portfolio] = useState<any>({
    cash_balance: 1000000.0,
    holdings: { 'RELIANCE': 10, 'TCS': 5 },
    total_pnl: 12450.50
  });

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>Institutional Paper Trading</Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle2">Virtual Capital</Typography>
                <Wallet size={20} />
              </Box>
              <Typography variant="h4" fontWeight="bold">₹{portfolio.cash_balance.toLocaleString()}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle2">Total Unrealized P&L</Typography>
                <TrendingUp size={20} className="text-emerald-500" />
              </Box>
              <Typography variant="h4" fontWeight="bold" color="primary">+₹{portfolio.total_pnl.toLocaleString()}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle2">Win Rate (Simulated)</Typography>
                <ArrowUpRight size={20} className="text-blue-500" />
              </Box>
              <Typography variant="h4" fontWeight="bold">68.5%</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Active Virtual Positions</Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell align="right">Qty</TableCell>
                <TableCell align="right">Avg Price</TableCell>
                <TableCell align="right">Current Price</TableCell>
                <TableCell align="right">P&L</TableCell>
                <TableCell align="center">Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>RELIANCE</TableCell>
                <TableCell align="right">10</TableCell>
                <TableCell align="right">₹2,450.00</TableCell>
                <TableCell align="right">₹2,510.45</TableCell>
                <TableCell align="right" sx={{ color: 'primary.main' }}>+₹604.50</TableCell>
                <TableCell align="center"><Chip size="small" label="PROFIT" color="success" /></TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>TCS</TableCell>
                <TableCell align="right">5</TableCell>
                <TableCell align="right">₹3,890.00</TableCell>
                <TableCell align="right">₹3,920.10</TableCell>
                <TableCell align="right" sx={{ color: 'primary.main' }}>+₹150.50</TableCell>
                <TableCell align="center"><Chip size="small" label="PROFIT" color="success" /></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
