import { Box, Typography, Paper, Grid, Divider, Table, TableHead, TableBody, TableCell, TableRow } from '@mui/material';
import { Cpu, TrendingUp, ShieldCheck } from 'lucide-react';

export default function FundamentalReport({ stock }: { stock: any }) {
  if (!stock) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Cpu size={20} className="text-emerald-500" /> Fundamental Research
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>PROFITABILITY & GROWTH</Typography>
            <Grid container spacing={3} sx={{ mt: 1 }}>
              <FundamentalMetric label="ROE" value={stock.roe ? `${(stock.roe * 100).toFixed(2)}%` : '---'} />
              <FundamentalMetric label="ROCE" value="24.5%" />
              <FundamentalMetric label="Debt to Equity" value={stock.debt_to_equity?.toFixed(2)} />
              <FundamentalMetric label="EPS (TTM)" value={`₹${stock.eps?.toFixed(2)}`} />
              <FundamentalMetric label="Revenue Growth" value="+18.4%" trend="up" />
              <FundamentalMetric label="Profit Growth" value="+22.1%" trend="up" />
            </Grid>

            <Divider sx={{ my: 3, opacity: 0.1 }} />

            <Typography variant="subtitle2" color="textSecondary" gutterBottom>INDUSTRY PEER RANKING</Typography>
            <Table size="small">
               <TableHead>
                  <TableRow>
                     <TableCell sx={{ fontSize: '0.7rem', color: 'text.secondary' }}>SYMBOL</TableCell>
                     <TableCell align="right" sx={{ fontSize: '0.7rem', color: 'text.secondary' }}>P/E</TableCell>
                     <TableCell align="right" sx={{ fontSize: '0.7rem', color: 'text.secondary' }}>ROE</TableCell>
                     <TableCell align="right" sx={{ fontSize: '0.7rem', color: 'text.secondary' }}>NET MARGIN</TableCell>
                  </TableRow>
               </TableHead>
               <TableBody>
                  <TableRow hover selected>
                     <TableCell sx={{ fontWeight: 'bold' }}>{stock.symbol}</TableCell>
                     <TableCell align="right">{stock.pe_ratio?.toFixed(1)}</TableCell>
                     <TableCell align="right">{(stock.roe * 100).toFixed(1)}%</TableCell>
                     <TableCell align="right">18.5%</TableCell>
                  </TableRow>
                  <TableRow hover>
                     <TableCell>PEER 1</TableCell>
                     <TableCell align="right">32.4</TableCell>
                     <TableCell align="right">16.2%</TableCell>
                     <TableCell align="right">14.8%</TableCell>
                  </TableRow>
                  <TableRow hover>
                     <TableCell>PEER 2</TableCell>
                     <TableCell align="right">28.1</TableCell>
                     <TableCell align="right">19.5%</TableCell>
                     <TableCell align="right">15.2%</TableCell>
                  </TableRow>
               </TableBody>
            </Table>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
           <Paper sx={{ p: 3, height: '100%', bgcolor: 'rgba(15, 23, 42, 0.3)' }}>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom>VALUATION AUDIT</Typography>
              <Box sx={{ mt: 3 }}>
                 <ValuationRow label="Intrinsic Value" value="₹2,720" />
                 <ValuationRow label="Current Price" value={`₹${stock.last_price?.toLocaleString()}`} />
                 <ValuationRow label="Margin of Safety" value="8.5%" />
              </Box>
              <Box sx={{ mt: 4, p: 2, bgcolor: 'rgba(16, 185, 129, 0.1)', borderRadius: 2, border: '1px solid #10b981' }}>
                  <Typography variant="caption" fontWeight="bold" color="primary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <ShieldCheck size={14} /> FINANCIAL STRENGTH
                  </Typography>
                  <Typography variant="h6" fontWeight="bold">STABLE</Typography>
              </Box>
           </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function FundamentalMetric({ label, value, trend }: any) {
  return (
    <Grid item xs={6} md={4}>
      <Typography variant="caption" color="textSecondary">{label}</Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="body1" fontWeight="bold">{value}</Typography>
        {trend === 'up' && <TrendingUp size={14} className="text-emerald-500" />}
      </Box>
    </Grid>
  );
}

function OwnershipItem({ label, value, trend }: any) {
  return (
    <Box>
       <Typography variant="caption" color="textSecondary">{label}</Typography>
       <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Typography variant="body2" fontWeight="bold">{value}</Typography>
          {trend === 'up' && <Box sx={{ width: 6, height: 6, bgcolor: '#10b981', borderRadius: '50%' }} />}
          {trend === 'down' && <Box sx={{ width: 6, height: 6, bgcolor: '#f43f5e', borderRadius: '50%' }} />}
       </Box>
    </Box>
  );
}

function ValuationRow({ label, value }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
      <Typography variant="body2" color="textSecondary">{label}</Typography>
      <Typography variant="body2" fontWeight="bold">{value}</Typography>
    </Box>
  );
}
