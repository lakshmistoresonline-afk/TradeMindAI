import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import Layout from './components/Layout'
import DashboardTerminal from './pages/DashboardTerminal'
import EquityScanner from './pages/EquityScanner'
import EquitySignals from './pages/EquitySignals'
import SignalHistory from './pages/SignalHistory'
import SignalDetail from './pages/SignalDetail'
import MarketOverview from './pages/MarketOverview'
import Accuracy from './pages/Accuracy'
import Research from './pages/Research'
import SystemStatus from './pages/SystemStatus'
import Methodology from './pages/Methodology'
import Login from './pages/Login'
import Settings from './pages/Settings'

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#00D1FF' },
    secondary: { main: '#7C3AED' },
    background: { default: '#020617', paper: '#0f172a' },
    success: { main: '#10b981' },
    error: { main: '#ef4444' },
    warning: { main: '#f59e0b' },
    text: { primary: '#f8fafc', secondary: '#94a3b8' },
  },
  typography: {
    fontFamily: '"Inter", "JetBrains Mono", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontWeight: 900, letterSpacing: '-0.02em' },
    h2: { fontWeight: 900, letterSpacing: '-0.01em' },
    h3: { fontWeight: 900, letterSpacing: '-0.01em' },
    h4: { fontWeight: 800, letterSpacing: '-0.01em' },
    h5: { fontWeight: 800 },
    h6: { fontWeight: 700, letterSpacing: 0.5 },
    subtitle1: { fontWeight: 700 },
    subtitle2: { fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase', fontSize: '0.75rem' },
    body1: { fontSize: '0.925rem', lineHeight: 1.6 },
    body2: { fontSize: '0.825rem', lineHeight: 1.6 },
    caption: { fontWeight: 600, letterSpacing: '0.05em' },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#020617',
          "&::-webkit-scrollbar, & *::-webkit-scrollbar": { width: 8, height: 8 },
          "&::-webkit-scrollbar-thumb, & *::-webkit-scrollbar-thumb": { borderRadius: 8, backgroundColor: "#111821" },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none', backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 8 },
      },
    },
    MuiButton: {
      styleOverrides: { root: { textTransform: 'none', fontWeight: 700, borderRadius: 6 } }
    },
    MuiTableCell: {
      styleOverrides: {
        root: { borderBottom: '1px solid rgba(255,255,255,0.03)', padding: '12px 16px' },
        head: { fontWeight: 800, color: '#64748b', fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.1em' }
      }
    }
  },
}) as any;

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={
            <Layout>
              <Routes>
                <Route path="/" element={<DashboardTerminal />} />
                <Route path="/scanner" element={<EquityScanner />} />

                <Route path="/signals" element={<Navigate to="/signals/active" replace />} />
                <Route path="/signals/active" element={<EquitySignals />} />
                <Route path="/signals/history" element={<SignalHistory />} />
                <Route path="/signals/:id" element={<SignalDetail />} />

                <Route path="/watchlist" element={<Navigate to="/scanner" replace />} />

                <Route path="/market" element={<Navigate to="/market/overview" replace />} />
                <Route path="/market/overview" element={<MarketOverview />} />

                <Route path="/accuracy" element={<Accuracy />} />
                <Route path="/research" element={<Research />} />

                <Route path="/status" element={<SystemStatus />} />
                <Route path="/methodology" element={<Methodology />} />

                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Layout>
          } />
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App
