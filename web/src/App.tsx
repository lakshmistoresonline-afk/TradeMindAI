import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import Layout from './components/Layout'
// v1.5_SIGNAL_ONLY_LOCKED
import EquitySignals from './pages/EquitySignals'
import SignalDetail from './pages/SignalDetail'
import Performance from './pages/Performance'
import SystemStatus from './pages/SystemStatus'
import Login from './pages/Login'
import Landing from './pages/Landing'
import Methodology from './pages/Methodology'
import Trust from './pages/Trust'
import Evidence from './pages/Evidence'
import Pricing from './pages/Pricing'
import RiskDisclosure from './pages/RiskDisclosure'
import Terms from './pages/Terms'
import Privacy from './pages/Privacy'
import Checkout from './pages/Checkout'
import Account from './pages/Account'
import UserDashboard from './pages/UserDashboard'
import AdminDashboard from './pages/AdminDashboard'
import AdminSignals from './pages/AdminSignals'
import AdminDataFeeds from './pages/AdminDataFeeds'
import { AuthProvider, useAuth } from './hooks/useAuth'

const AuthGuard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

const AdminGuard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAdmin, loading } = useAuth();
  if (loading) return null;
  if (!user || !isAdmin) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
};

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#00D1FF', light: '#38bdf8', dark: '#0284c7' },
    secondary: { main: '#7C3AED', light: '#a855f7', dark: '#6d28d9' },
    background: { default: '#020617', paper: '#0f172a' },
    success: { main: '#10b981', light: '#34d399', dark: '#059669' },
    error: { main: '#f43f5e', light: '#fb7185', dark: '#e11d48' },
    warning: { main: '#f59e0b', light: '#fbbf24', dark: '#d97706' },
    text: { primary: '#f8fafc', secondary: '#94a3b8' },
  },
  typography: {
    fontFamily: '"Inter", "JetBrains Mono", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontWeight: 950, letterSpacing: '-0.025em' },
    h2: { fontWeight: 950, letterSpacing: '-0.02em' },
    h3: { fontWeight: 900, letterSpacing: '-0.015em' },
    h4: { fontWeight: 900, letterSpacing: '-0.01em' },
    h5: { fontWeight: 800, letterSpacing: '-0.005em' },
    h6: { fontWeight: 800, letterSpacing: 0.2 },
    subtitle1: { fontWeight: 700 },
    subtitle2: { fontWeight: 700, letterSpacing: 0.8, textTransform: 'uppercase', fontSize: '0.75rem' },
    body1: { fontSize: '0.925rem', lineHeight: 1.6 },
    body2: { fontSize: '0.825rem', lineHeight: 1.6 },
    caption: { fontWeight: 600, letterSpacing: '0.04em' },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#020617',
          color: '#f8fafc',
          "&::-webkit-scrollbar, & *::-webkit-scrollbar": { width: 6, height: 6 },
          "&::-webkit-scrollbar-thumb, & *::-webkit-scrollbar-thumb": { borderRadius: 4, backgroundColor: "#1e293b" },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: 'rgba(15, 23, 42, 0.85)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: 12
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 800,
          borderRadius: 8,
          transition: 'all 0.2s ease-in-out'
        }
      }
    },
    MuiTableCell: {
      styleOverrides: {
        root: { borderBottom: '1px solid rgba(255,255,255,0.04)', padding: '14px 18px' },
        head: { fontWeight: 800, color: '#64748b', fontSize: '0.675rem', textTransform: 'uppercase', letterSpacing: '0.08em' }
      }
    },
    MuiChip: {
      styleOverrides: {
        root: { fontWeight: 800, borderRadius: 6 }
      }
    }
  },
}) as any;

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            {/* PUBLIC MARKETING & LANDING ROUTES */}
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />

            {/* PUBLIC RESEARCH & PERFORMANCE PAGES (Accessible without signing in) */}
            <Route path="/performance" element={<Layout><Performance /></Layout>} />
            <Route path="/accuracy" element={<Navigate to="/performance" replace />} />
            <Route path="/trust" element={<Layout><Trust /></Layout>} />
            <Route path="/methodology" element={<Layout><Methodology /></Layout>} />
            <Route path="/how-it-works" element={<Layout><Methodology /></Layout>} />
            <Route path="/evidence" element={<Layout><Evidence /></Layout>} />
            <Route path="/pricing" element={<Layout><Pricing /></Layout>} />
            <Route path="/faq" element={<Layout><Pricing /></Layout>} />
            <Route path="/risk-disclosure" element={<RiskDisclosure />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="/terms" element={<Terms />} />

            {/* PROTECTED APPLICATION ROUTES (Wrapped inside AuthGuard) */}
            <Route path="/*" element={
              <AuthGuard>
                <Layout>
                  <Routes>
                    {/* User Experience (Consumer Signals & Application Pages) */}
                    <Route path="/dashboard" element={<UserDashboard />} />
                    <Route path="/signals" element={<EquitySignals />} />
                    <Route path="/signals/:id" element={<SignalDetail />} />
                    <Route path="/account" element={<Account />} />
                    <Route path="/checkout/:planId" element={<Checkout />} />

                    {/* Admin Experience (Guarded) */}
                    <Route path="/admin/*" element={
                      <AdminGuard>
                        <Routes>
                          <Route path="dashboard" element={<AdminDashboard />} />
                          <Route path="signals" element={<AdminSignals />} />
                          <Route path="data" element={<AdminDataFeeds />} />
                          <Route path="status" element={<SystemStatus />} />
                          <Route path="*" element={<Navigate to="dashboard" replace />} />
                        </Routes>
                      </AdminGuard>
                    } />

                    <Route path="/status" element={<Navigate to="/admin/status" replace />} />

                    {/* Fallback to Dashboard */}
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </Layout>
              </AuthGuard>
            } />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
