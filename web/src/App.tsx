import React, { lazy, Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline, Box, CircularProgress } from '@mui/material'
import Layout from './components/Layout'
import ScrollToTop from './components/ScrollToTop'
import { AuthProvider, useAuth } from './hooks/useAuth'

// Lazy-loaded Route Components for Optimal Code Splitting
const Landing = lazy(() => import('./pages/Landing'))
const Login = lazy(() => import('./pages/Login'))
const EquitySignals = lazy(() => import('./pages/EquitySignals'))
const SignalDetail = lazy(() => import('./pages/SignalDetail'))
const Performance = lazy(() => import('./pages/Performance'))
const SystemStatus = lazy(() => import('./pages/SystemStatus'))
const Methodology = lazy(() => import('./pages/Methodology'))
const Trust = lazy(() => import('./pages/Trust'))
const Evidence = lazy(() => import('./pages/Evidence'))
const Pricing = lazy(() => import('./pages/Pricing'))
const RiskDisclosure = lazy(() => import('./pages/RiskDisclosure'))
const Terms = lazy(() => import('./pages/Terms'))
const Privacy = lazy(() => import('./pages/Privacy'))
const Checkout = lazy(() => import('./pages/Checkout'))
const Account = lazy(() => import('./pages/Account'))
const UserDashboard = lazy(() => import('./pages/UserDashboard'))
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'))
const AdminSignals = lazy(() => import('./pages/AdminSignals'))
const AdminDataFeeds = lazy(() => import('./pages/AdminDataFeeds'))

const PageFallback = () => (
  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
    <CircularProgress size={32} sx={{ color: '#00D1FF' }} />
  </Box>
)

const AuthGuard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <PageFallback />;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

const AdminGuard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAdmin, loading } = useAuth();
  if (loading) return <PageFallback />;
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
        html: {
          overflowY: 'scroll !important',
          scrollBehavior: 'smooth',
        },
        body: {
          backgroundColor: '#020617',
          color: '#f8fafc',
          overflowX: 'hidden',
          "&::-webkit-scrollbar, & *::-webkit-scrollbar": { width: 8, height: 8 },
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
          <ScrollToTop />
          <Suspense fallback={<PageFallback />}>
            <Routes>
              {/* PUBLIC MARKETING & LANDING ROUTES */}
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />

              {/* PUBLIC RESEARCH & PERFORMANCE PAGES */}
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
          </Suspense>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
