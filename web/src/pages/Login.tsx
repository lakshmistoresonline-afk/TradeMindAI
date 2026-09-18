import { useState } from 'react';
import { Box, Typography, TextField, Button, Stack, Link, InputAdornment, IconButton, Paper } from '@mui/material';
import { TrendingUp, LogIn, Eye, EyeOff, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword, sendPasswordResetEmail } from 'firebase/auth';
import { auth } from '../core/firebase';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [infoMessage, setInfoMessage] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const validateForm = () => {
    if (!email.trim()) {
      setError('Email address is required.');
      return false;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError('Please enter a valid email address.');
      return false;
    }
    if (!password) {
      setError('Password is required.');
      return false;
    }
    return true;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setInfoMessage('');

    if (!validateForm()) return;

    setLoading(true);
    try {
      if (isSignUp) {
        await createUserWithEmailAndPassword(auth, email.trim(), password);
      } else {
        await signInWithEmailAndPassword(auth, email.trim(), password);
      }
      navigate('/dashboard');
    } catch (err: any) {
      console.error(err);
      const code = err?.code || '';
      if (code === 'auth/wrong-password' || code === 'auth/user-not-found' || code === 'auth/invalid-credential') {
        setError('Email or password is incorrect.');
      } else if (code === 'auth/invalid-email') {
        setError('Please enter a valid email address.');
      } else if (code === 'auth/email-already-in-use') {
        setError('An account with this email address already exists.');
      } else if (code === 'auth/weak-password') {
        setError('Password should be at least 6 characters.');
      } else if (code === 'auth/network-request-failed') {
        setError('Unable to connect. Please check your connection and try again.');
      } else if (code === 'auth/too-many-requests') {
        setError('Too many attempts. Please wait a moment and try again.');
      } else {
        setError('Unable to sign in. Please check your credentials and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async () => {
    setError('');
    setInfoMessage('');
    if (!email.trim()) {
      setError('Please enter your email address first to reset your password.');
      return;
    }
    try {
      await sendPasswordResetEmail(auth, email.trim());
      setInfoMessage('If an account exists for this email, password recovery instructions have been sent.');
    } catch (err: any) {
      console.error(err);
      setError('Unable to send password reset email. Please try again later.');
    }
  };

  return (
    <Box sx={{
      minHeight: '100vh',
      display: 'grid',
      gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
      background: 'radial-gradient(circle at top right, #0f172a, #020617)',
      color: '#f8fafc'
    }}>
      {/* LEFT AREA: PRIMARY BRAND AREA */}
      <Box sx={{
        display: { xs: 'none', md: 'flex' },
        flexDirection: 'column',
        justifyContent: 'center',
        px: 8,
        position: 'relative',
        borderRight: '1px solid rgba(255, 255, 255, 0.05)',
        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(2, 6, 23, 0.9))'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <TrendingUp size={40} className="text-emerald-500" />
          <Typography variant="h4" fontWeight="800" sx={{ tracking: '-0.02em', color: '#fff' }}>
            TradeMind AI
          </Typography>
        </Box>
        <Typography variant="h5" fontWeight="600" sx={{ mb: 2, color: '#e2e8f0' }}>
          Evidence-Driven Market Signal Intelligence
        </Typography>
        <Typography variant="body1" sx={{ color: '#94a3b8', lineHeight: 1.7, maxWidth: 480, mb: 6 }}>
          Access validated market signals, evidence, lifecycle status, and historical signal intelligence. Built for professional market analysis.
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, p: 2, borderRadius: 2, bgcolor: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.1)', maxWidth: 480 }}>
          <ShieldCheck size={20} className="text-emerald-400 flex-shrink-0" />
          <Typography variant="caption" sx={{ color: '#a7f3d0' }}>
            TradeMind AI provides market signal intelligence, and NOT brokerage, trade execution, or investment guarantees. Real trading remains inactive.
          </Typography>
        </Box>
      </Box>

      {/* RIGHT AREA: CLEAN AUTHENTICATION CARD */}
      <Box sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: { xs: 3, sm: 6, md: 8 }
      }}>
        {/* Mobile-only branding header */}
        <Box sx={{ display: { xs: 'flex', md: 'none' }, alignItems: 'center', gap: 1.5, mb: 4 }}>
          <TrendingUp size={32} className="text-emerald-500" />
          <Typography variant="h5" fontWeight="800" sx={{ color: '#fff' }}>
            TradeMind AI
          </Typography>
        </Box>

        <Paper elevation={0} sx={{
          p: { xs: 4, sm: 5 },
          width: '100%',
          maxWidth: 440,
          borderRadius: 3,
          bgcolor: 'rgba(30, 41, 59, 0.4)',
          border: '1px solid rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(12px)'
        }}>
          <Typography variant="h5" fontWeight="700" sx={{ mb: 1, color: '#fff' }}>
            {isSignUp ? 'Create Account' : 'Welcome Back'}
          </Typography>
          <Typography variant="body2" sx={{ mb: 4, color: '#94a3b8' }}>
            {isSignUp ? 'Register to explore validated signal intelligence.' : 'Sign in to continue to TradeMind AI.'}
          </Typography>

          {error && (
            <Box sx={{ p: 1.5, mb: 3, borderRadius: 1.5, bgcolor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              <Typography color="#f87171" variant="body2" sx={{ fontWeight: 500 }}>
                {error}
              </Typography>
            </Box>
          )}

          {infoMessage && (
            <Box sx={{ p: 1.5, mb: 3, borderRadius: 1.5, bgcolor: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
              <Typography color="#60a5fa" variant="body2" sx={{ fontWeight: 500 }}>
                {infoMessage}
              </Typography>
            </Box>
          )}

          <form onSubmit={handleLogin} noValidate>
            <Stack spacing={3}>
              <TextField
                fullWidth
                label="Email Address"
                variant="outlined"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                InputLabelProps={{ style: { color: '#94a3b8' } }}
                inputProps={{ 'aria-label': 'Email Address' }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: '#fff',
                    '& fieldset': { borderColor: 'rgba(255,255,255,0.1)' },
                    '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
                    '&.Mui-focused fieldset': { borderColor: '#10b981' },
                  }
                }}
              />
              <TextField
                fullWidth
                label="Password"
                variant="outlined"
                type={showPassword ? 'text' : 'password'}
                autoComplete={isSignUp ? 'new-password' : 'current-password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                InputLabelProps={{ style: { color: '#94a3b8' } }}
                inputProps={{ 'aria-label': 'Password' }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        onMouseDown={(e) => e.preventDefault()}
                        edge="end"
                        style={{ color: '#94a3b8' }}
                        aria-label={showPassword ? 'Hide password' : 'Show password'}
                      >
                        {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                      </IconButton>
                    </InputAdornment>
                  )
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: '#fff',
                    '& fieldset': { borderColor: 'rgba(255,255,255,0.1)' },
                    '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
                    '&.Mui-focused fieldset': { borderColor: '#10b981' },
                  }
                }}
              />

              {!isSignUp && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: -1 }}>
                  <Link
                    component="button"
                    type="button"
                    variant="body2"
                    onClick={handleForgotPassword}
                    underline="hover"
                    sx={{ color: '#94a3b8', fontSize: '0.85rem', '&:hover': { color: '#10b981' } }}
                  >
                    Forgot Password?
                  </Link>
                </Box>
              )}

              <Button
                fullWidth
                size="large"
                variant="contained"
                type="submit"
                disabled={loading}
                sx={{
                  py: 1.5,
                  fontWeight: '700',
                  textTransform: 'none',
                  fontSize: '1rem',
                  bgcolor: '#10b981',
                  color: '#020617',
                  '&:hover': { bgcolor: '#059669' },
                  '&.Mui-disabled': { bgcolor: 'rgba(16, 185, 129, 0.3)', color: 'rgba(2, 6, 23, 0.5)' }
                }}
              >
                {loading ? 'Signing in…' : isSignUp ? 'Create Account' : 'Sign In'}
              </Button>
            </Stack>
          </form>

          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography variant="body2" sx={{ color: '#94a3b8' }}>
              {isSignUp ? 'Already have an account?' : "Don't have an account?"}{' '}
              <Link
                component="button"
                type="button"
                onClick={() => {
                  setIsSignUp(!isSignUp);
                  setError('');
                  setInfoMessage('');
                }}
                underline="hover"
                sx={{ fontWeight: '700', color: '#10b981', '&:hover': { color: '#059669' }, ml: 0.5 }}
              >
                {isSignUp ? 'Sign In' : 'Create Account'}
              </Link>
            </Typography>
          </Box>
        </Paper>

        {/* Mobile risk notice */}
        <Box sx={{ display: { xs: 'block', md: 'none' }, mt: 4, px: 3, textAlign: 'center' }}>
          <Typography variant="caption" sx={{ color: '#64748b', lineHeight: 1.5, display: 'block' }}>
            TradeMind AI provides market signal intelligence, and NOT brokerage, trade execution, or investment guarantees. Real trading remains inactive.
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
