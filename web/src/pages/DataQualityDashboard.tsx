import { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Grid, Paper, Stack, Chip,
  CircularProgress, alpha, LinearProgress
} from '@mui/material';
import {
  ShieldCheck, AlertTriangle, Database, Fingerprint
} from 'lucide-react';
import { apiClient } from '../api/client';

export default function DataQualityDashboard() {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchReport = useCallback(async () => {
    try {
      const res = await apiClient.get('/shadow/integrity/report');
      setReport(res.data);
    } catch (err) {
      console.error("Integrity report fetch failed", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 900 }}>DATA QUALITY & INTEGRITY <Chip label="FORENSIC" color="secondary" size="small" /></Typography>
        <Chip
          label={report?.status || 'UNKNOWN'}
          color={report?.status === 'PASS' ? 'success' : 'warning'}
          sx={{ fontWeight: 900, px: 2 }}
          icon={report?.status === 'PASS' ? <ShieldCheck size={16}/> : <AlertTriangle size={16}/>}
        />
      </Box>

      <Grid container spacing={3}>
        {/* Population Overview */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <SectionHeader icon={<Database size={18} />} title="SIGNAL POPULATION" />
            <Stack spacing={2} sx={{ mt: 3 }}>
               <DataMetric label="TOTAL SIGNALS" value={report?.population?.total_signals} />
               <DataMetric label="VERIFIED OUTCOMES" value={report?.population?.verified_outcomes} color="#10b981" />
               <DataMetric label="ACTIVE SIGNALS" value={report?.population?.active_signals} color="#00D1FF" />
               <DataMetric label="UNVERIFIED HISTORY" value={report?.population?.unverified_historical} color="slategray" />
            </Stack>
          </Paper>
        </Grid>

        {/* Traceability Coverage */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <SectionHeader icon={<Fingerprint size={18} />} title="TRACEABILITY & COVERAGE" />
            <Grid container spacing={4} sx={{ mt: 2 }}>
               <Grid item xs={12} md={6}>
                  <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray' }}>PREDICTION LINKAGE</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                     <Typography variant="h4" fontWeight={900}>{report?.integrity_metrics?.prediction_linkage_pct}%</Typography>
                     <LinearProgress variant="determinate" value={report?.integrity_metrics?.prediction_linkage_pct} sx={{ flexGrow: 1, height: 8, borderRadius: 4 }} />
                  </Box>
               </Grid>
               <Grid item xs={12} md={6}>
                  <Typography variant="caption" sx={{ fontWeight: 900, color: 'slategray' }}>PROVENANCE COVERAGE</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                     <Typography variant="h4" fontWeight={900}>{report?.integrity_metrics?.provenance_coverage_pct}%</Typography>
                     <LinearProgress variant="determinate" value={report?.integrity_metrics?.provenance_coverage_pct} color="secondary" sx={{ flexGrow: 1, height: 8, borderRadius: 4 }} />
                  </Box>
               </Grid>
            </Grid>
          </Paper>

          {/* Forensic Anomalies */}
          <Paper sx={{ p: 3, mt: 3, bgcolor: alpha('#ef4444', 0.02), border: '1px solid rgba(239, 68, 68, 0.1)' }}>
            <SectionHeader icon={<AlertTriangle size={18} />} title="FORENSIC ANOMALIES" />
            <Grid container spacing={4} sx={{ mt: 1 }}>
               <Grid item xs={6} md={3}>
                  <Typography variant="caption" display="block" color="slategray" fontWeight={800}>LOOK-AHEAD VIOLATIONS</Typography>
                  <Typography variant="h6" fontWeight={950} color={report?.integrity_metrics?.lookahead_violation_count > 0 ? 'error' : 'success'}>
                    {report?.integrity_metrics?.lookahead_violation_count}
                  </Typography>
               </Grid>
               <Grid item xs={6} md={3}>
                  <Typography variant="caption" display="block" color="slategray" fontWeight={800}>STALE DATA STOCKS</Typography>
                  <Typography variant="h6" fontWeight={950} color={report?.integrity_metrics?.stale_data_stock_count > 10 ? 'warning' : 'success'}>
                    {report?.integrity_metrics?.stale_data_stock_count}
                  </Typography>
               </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function SectionHeader({ icon, title }: any) {
  return (
    <Stack direction="row" spacing={1.5} alignItems="center">
      <Box sx={{ color: 'primary.main' }}>{icon}</Box>
      <Typography variant="caption" sx={{ fontWeight: 950, letterSpacing: 1.5, color: 'slategray' }}>{title}</Typography>
    </Stack>
  );
}

function DataMetric({ label, value, color }: any) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
       <Typography variant="caption" sx={{ fontWeight: 800 }}>{label}</Typography>
       <Typography variant="h6" sx={{ fontWeight: 950, color: color || 'white', fontFamily: 'JetBrains Mono' }}>{value}</Typography>
    </Box>
  );
}
