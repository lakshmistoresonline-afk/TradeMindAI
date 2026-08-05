import { useState } from 'react';
import { Box, Paper, Typography, TextField, Button, Stack, Link, Alert } from '@mui/material';
import { TrendingUp, LogIn } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate login - Bypassing real Firebase Auth for now
    navigate('/');
  };

  return (
    <Box sx={{
      height: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(circle at top right, #0f172a, #020617)'
    }}>
      <Paper sx={{ p: 5, width: '100%', maxWidth: 400, textAlign: 'center', borderRadius: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 4 }}>
          <TrendingUp size={32} className="text-emerald-500" />
          <Typography variant="h5" fontWeight="bold">TradeMind AI</Typography>
        </Box>

        <Typography variant="h6" gutterBottom>Welcome Back</Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 4 }}>
          Login to access your institutional AI insights.
        </Typography>

        <form onSubmit={handleLogin}>
          <Stack spacing={3}>
            <TextField
              fullWidth
              label="Email Address"
              variant="outlined"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              variant="outlined"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button
              fullWidth
              size="large"
              variant="contained"
              type="submit"
              startIcon={<LogIn size={18} />}
              sx={{ py: 1.5, fontWeight: 'bold' }}
            >
              Sign In
            </Button>
          </Stack>
        </form>

        <Box sx={{ mt: 4 }}>
          <Typography variant="body2" color="textSecondary">
            Don't have an account? <Link href="#" underline="hover" color="primary">Create one</Link>
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
}
