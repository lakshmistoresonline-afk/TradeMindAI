import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Avatar, CircularProgress } from '@mui/material';
import { Share2, Users, Building, Globe } from 'lucide-react';
import { getKnowledgeGraphData } from '../../api/client';

export default function KnowledgeGraph({ symbol }: { symbol: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getKnowledgeGraphData(symbol).then(res => {
      setData(res);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [symbol]);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress /></Box>;
  if (!data) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Share2 size={20} className="text-blue-400" /> AI Knowledge Graph: {symbol}
      </Typography>

      <Paper sx={{ p: 4, bgcolor: 'rgba(15, 23, 42, 0.3)', border: '1px solid #334155' }}>
         <Box sx={{ display: 'flex', justifyContent: 'center', mb: 6 }}>
            <Avatar sx={{ width: 80, height: 80, bgcolor: 'primary.main', color: 'black', fontWeight: 'bold', fontSize: '1.5rem' }}>{symbol}</Avatar>
         </Box>

         <Grid container spacing={4}>
            {data.nodes.filter((n: any) => n.id !== symbol).map((node: any, i: number) => (
              <Grid item xs={6} md={2.4} key={i}>
                 <Box sx={{ textAlign: 'center', p: 2, border: '1px solid #334155', borderRadius: 2, '&:hover': { bgcolor: 'rgba(16, 185, 129, 0.05)', borderColor: 'primary.main' }, transition: '0.2s' }}>
                    <Box sx={{ display: 'inline-flex', p: 1, bgcolor: 'rgba(255,255,255,0.05)', borderRadius: '50%', mb: 1, color: 'primary.main' }}>
                       {node.type === 'SECTOR' ? <Globe size={14} /> : node.type === 'COMPETITOR' ? <Building size={14} /> : <Users size={14} />}
                    </Box>
                    <Typography variant="caption" color="textSecondary" display="block">{node.type}</Typography>
                    <Typography variant="body2" fontWeight="bold">{node.label}</Typography>
                 </Box>
              </Grid>
            ))}
         </Grid>

         <Box sx={{ mt: 4, p: 2, bgcolor: 'rgba(255,255,255,0.02)', borderRadius: 2, textAlign: 'center' }}>
            <Typography variant="caption" color="textSecondary">
               This graph visualizes the semantic relationships for {symbol} in the {data.metadata.sector} sector.
            </Typography>
         </Box>
      </Paper>
    </Box>
  );
}
