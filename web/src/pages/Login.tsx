import { useState } from 'react';
import { Box, Typography, TextField, Button, Stack, Link, InputAdornment, IconButton, Paper } from '@mui/material';
import { TrendingUp, Eye, EyeOff, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword, sendPasswordResetEmail } from 'firebase/auth';
import { auth } from '../core/firebase';

/**
 * TradeMind AI Premium Login (Institutional V2.2)
 * High-performance split-pane layout with forensic security overrides.
 */
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
      // Secure error mapping (Anti-Enumeration)
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
      gridTemplateColumns: { xs: '1fr', md: '1.2fr 1fr' },
      background: 'radial-gradient(circle at top right, #0f172a, #020617)',
      color: '#f8fafc'
    }}>
      {/* LEFT AREA: PRIMARY BRANDING & POSITIONING */}
      <Box sx={{
        display: { xs: 'none', md: 'flex' },
        flexDirection: 'column',
        justifyContent: 'center',
        px: 10,
        position: 'relative',
        borderRight: '1px solid rgba(255, 255, 255, 0.05)',
        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(2, 6, 23, 0.9))'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 4 }}>
          <TrendingUp size={48} className="text-emerald-500" />
          <Typography variant="h3" fontWeight="950" sx={{ tracking: '-0.04em', color: '#fff' }}>
            TradeMind AI
          </Typography>
        </Box>
        <Typography variant="h4" fontWeight="800" sx={{ mb: 3, color: '#e2e8f0', maxWidth: 600 }}>
          Evidence-Driven Market Signal Intelligence
        </Typography>
        <Typography variant="body1" sx={{ color: '#94a3b8', lineHeight: 1.8, maxWidth: 520, mb: 8, fontSize: '1.1rem' }}>
          Access validated market signals, bitwise forensic evidence, lifecycle status, and historical signal intelligence. Built for professional market analysis.
        </Typography>

        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          p: 3,
          borderRadius: 1,
          bgcolor: 'rgba(16, 185, 129, 0.05)',
          border: '1px solid rgba(16, 185, 129, 0.1)',
          maxWidth: 520
        }}>
          <ShieldCheck size={24} className="text-emerald-400 flex-shrink-0" />
          <Typography variant="body2" sx={{ color: '#a7f3d0', fontWeight: 600 }}>
            TradeMind AI provides market signal intelligence, and NOT brokerage, trade execution, or investment guarantees. REAL_TRADING remains permanently inactive.
          </Typography>
        </Box>
      </Box>

      {/* RIGHT AREA: CLEAN AUTHENTICATION INTERFACE */}
      <Box sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: { xs: 3, sm: 6, md: 8 }
      }}>
        {/* Mobile branding header */}
        <Box sx={{ display: { xs: 'flex', md: 'none' }, alignItems: 'center', gap: 1.5, mb: 6 }}>
          <TrendingUp size={32} className="text-emerald-500" />
          <Typography variant="h5" fontWeight="900" sx={{ color: '#fff', letterSpacing: -0.5 }}>
            TradeMind AI
          </Typography>
        </Box>

        <Paper elevation={0} sx={{
          p: { xs: 4, sm: 6 },
          width: '100%',
          maxWidth: 480,
          borderRadius: 2,
          bgcolor: 'rgba(30, 41, 59, 0.4)',
          border: '1px solid rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(16px)'
        }}>
          <Typography variant="h4" fontWeight="900" sx={{ mb: 1, color: '#fff', letterSpacing: -1 }}>
            {isSignUp ? 'Create Account' : 'Welcome Back'}
          </Typography>
          <Typography variant="body1" sx={{ mb: 6, color: '#94a3b8', fontWeight: 500 }}>
            {isSignUp ? 'Register to explore validated signal intelligence.' : 'Sign in to continue to TradeMind AI.'}
          </Typography>

          {error && (
            <Box sx={{ p: 2, mb: 4, borderRadius: 1, bgcolor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              <Typography color="#f87171" variant="body2" sx={{ fontWeight: 600 }}>
                {error}
              </Typography>
            </Box>
          )}

          {infoMessage && (
            <Box sx={{ p: 2, mb: 4, borderRadius: 1, bgcolor: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
              <Typography color="#60a5fa" variant="body2" sx={{ fontWeight: 600 }}>
                {infoMessage}
              </Typography>
            </Box>
          )}

          <form onSubmit={handleLogin} noValidate>
            <Stack spacing={4}>
              <TextField
                fullWidth
                label="Email Address"
                variant="outlined"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                InputLabelProps={{ shrink: true, style: { color: '#ffffff', fontWeight: 800, fontSize: '0.9rem', marginBottom: '8px' } }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: '#fff',
                    fontWeight: 600,
                    bgcolor: 'rgba(15, 23, 42, 0.5)',
                    '& fieldset': { borderColor: 'rgba(255,255,255,0.1)', borderWidth: 2 },
                    '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.3)' },
                    '&.Mui-focused fieldset': { borderColor: '#10b981' },
                  },
                  '& .MuiInputLabel-root': {
                    color: '#fff !important',
                    transform: 'translate(0, -24px) scale(1)',
                    pointerEvents: 'none'
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
                InputLabelProps={{ shrink: true, style: { color: '#ffffff', fontWeight: 800, fontSize: '0.9rem', marginBottom: '8px' } }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        onMouseDown={(e) => e.preventDefault()}
                        edge="end"
                        sx={{ color: '#ffffff' }}
                      >
                        {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                      </IconButton>
                    </InputAdornment>
                  )
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: '#fff',
                    fontWeight: 600,
                    bgcolor: 'rgba(15, 23, 42, 0.5)',
                    '& fieldset': { borderColor: 'rgba(255,255,255,0.1)', borderWidth: 2 },
                    '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.3)' },
                    '&.Mui-focused fieldset': { borderColor: '#10b981' },
                  },
                  '& .MuiInputLabel-root': {
                    color: '#fff !important',
                    transform: 'translate(0, -24px) scale(1)',
                    pointerEvents: 'none'
                  }
                }}
              />

              {!isSignUp && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: -2 }}>
                  <Link
                    component="button"
                    type="button"
                    variant="body2"
                    onClick={handleForgotPassword}
                    underline="hover"
                    sx={{ color: '#94a3b8', fontWeight: 700, fontSize: '0.85rem', '&:hover': { color: '#10b981' } }}
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
                  py: 2,
                  fontWeight: '900',
                  textTransform: 'none',
                  fontSize: '1.1rem',
                  bgcolor: '#10b981',
                  color: '#020617',
                  borderRadius: 1,
                  boxShadow: '0 4px 14px 0 rgba(16, 185, 129, 0.39)',
                  '&:hover': { bgcolor: '#059669', transform: 'translateY(-1px)' },
                  '&.Mui-disabled': { bgcolor: 'rgba(16, 185, 129, 0.3)', color: 'rgba(2, 6, 23, 0.5)' }
                }}
              >
                {loading ? 'Processing...' : isSignUp ? 'Create Account' : 'Sign In'}
              </Button>
            </Stack>
          </form>

          <Box sx={{ mt: 6, textAlign: 'center' }}>
            <Typography variant="body2" sx={{ color: '#94a3b8', fontWeight: 600 }}>
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
                sx={{ fontWeight: '800', color: '#10b981', '&:hover': { color: '#059669' }, ml: 0.5 }}
              >
                {isSignUp ? 'Sign In' : 'Create Account'}
              </Link>
            </Typography>
          </Box>
        </Paper>

        {/* Mobile risk notice */}
        <Box sx={{ display: { xs: 'block', md: 'none' }, mt: 6, px: 4, textAlign: 'center' }}>
          <Typography variant="caption" sx={{ color: '#475569', lineHeight: 1.6, display: 'block', fontWeight: 500 }}>
            TradeMind AI provides market signal intelligence, and NOT brokerage, trade execution, or investment guarantees. REAL_TRADING remains inactive.
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
