import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import Layout from './components/Layout'
import DashboardTerminal from './pages/DashboardTerminal'
import MarketDashboard from './pages/MarketDashboard'
import PortfolioDashboard from './pages/PortfolioDashboard'
import HistoryDashboard from './pages/HistoryDashboard'
import StockIntelligence from './pages/StockIntelligence'
import Settings from './pages/Settings'
import Login from './pages/Login'
import SystemControl from './pages/SystemControl'
import EquitySignals from './pages/EquitySignals'
import FuturesSignals from './pages/FuturesSignals'
import OptionsSignals from './pages/OptionsSignals'
import ShadowMonitor from './pages/ShadowMonitor'

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00D1FF', // Electric Cyan
    },
    secondary: {
      main: '#7C3AED', // AI Violet
    },
    background: {
      default: '#020617',
      paper: '#0f172a',
    },
    success: {
      main: '#10b981', // Emerald
    },
    error: {
      main: '#ef4444', // Red
    },
    warning: {
      main: '#f59e0b', // Amber
    },
    text: {
      primary: '#f8fafc',
      secondary: '#94a3b8',
    },
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
          scrollbarColor: "#111821 #070A0F",
          "&::-webkit-scrollbar, & *::-webkit-scrollbar": {
            width: 8,
            height: 8,
          },
          "&::-webkit-scrollbar-thumb, & *::-webkit-scrollbar-thumb": {
            borderRadius: 8,
            backgroundColor: "#111821",
            border: "2px solid #070A0F",
          },
          "&::-webkit-scrollbar-thumb:focus, & *::-webkit-scrollbar-thumb:focus": {
            backgroundColor: "#1e293b",
          },
          "&::-webkit-scrollbar-thumb:active, & *::-webkit-scrollbar-thumb:active": {
            backgroundColor: "#1e293b",
          },
          "&::-webkit-scrollbar-thumb:hover, & *::-webkit-scrollbar-thumb:hover": {
            backgroundColor: "#1e293b",
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#0f172a',
          border: '1px solid rgba(255,255,255,0.05)',
          borderRadius: 8,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 700,
          borderRadius: 6,
          padding: '8px 16px',
        }
      }
    },
    MuiTab: {
      styleOverrides: {
        root: {
          fontWeight: 800,
          fontSize: '0.75rem',
          letterSpacing: '0.05em',
        }
      }
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(255,255,255,0.03)',
          padding: '12px 16px',
        },
        head: {
          fontWeight: 800,
          color: '#64748b',
          fontSize: '0.65rem',
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          backgroundColor: '#0f172a',
        }
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
                <Route path="/signals" element={<Navigate to="/signals/equity" replace />} />
                <Route path="/signals/equity" element={<EquitySignals />} />
                <Route path="/signals/futures" element={<FuturesSignals />} />
                <Route path="/signals/options" element={<OptionsSignals />} />

                <Route path="/market" element={<MarketDashboard />} />
                <Route path="/portfolio" element={<PortfolioDashboard />} />
                <Route path="/history" element={<HistoryDashboard />} />

                {/* Contextual / Advanced */}
                <Route path="/analysis" element={<StockIntelligence />} />
                <Route path="/shadow" element={<ShadowMonitor />} />
                <Route path="/admin" element={<SystemControl />} />
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
