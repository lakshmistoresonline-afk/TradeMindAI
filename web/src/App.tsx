import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import Layout from './components/Layout'
import SignalsDashboard from './pages/SignalsDashboard'
import MarketDashboard from './pages/MarketDashboard'
import PortfolioDashboard from './pages/PortfolioDashboard'
import HistoryDashboard from './pages/HistoryDashboard'
import StockIntelligence from './pages/StockIntelligence'
import Settings from './pages/Settings'
import Login from './pages/Login'
import SystemControl from './pages/SystemControl'
import StrategyBuilder from './pages/StrategyBuilder/StrategyBuilderPage'

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#10b981', // Emerald 500
    },
    background: {
      default: '#020617',
      paper: '#0f172a',
    },
    text: {
      primary: '#f8fafc',
      secondary: '#94a3b8',
    },
  },
  typography: {
    fontFamily: '"Inter", "JetBrains Mono", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontWeight: 900 },
    h4: { fontWeight: 800 },
    h6: { fontWeight: 700, letterSpacing: 0.5 },
    subtitle2: { fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase', fontSize: '0.75rem' },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid #1e293b',
          borderRadius: 8,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 6,
        }
      }
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(255,255,255,0.05)',
          padding: '8px 16px',
        },
        head: {
          fontWeight: 700,
          color: '#94a3b8',
          fontSize: '0.65rem',
          textTransform: 'uppercase',
          letterSpacing: 1,
        }
      }
    }
  },
})

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
                <Route path="/" element={<SignalsDashboard />} />
                <Route path="/market" element={<MarketDashboard />} />
                <Route path="/portfolio" element={<PortfolioDashboard />} />
                <Route path="/history" element={<HistoryDashboard />} />

                {/* Contextual / Advanced */}
                <Route path="/analysis" element={<StockIntelligence />} />
                <Route path="/strategy" element={<StrategyBuilder />} />
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
