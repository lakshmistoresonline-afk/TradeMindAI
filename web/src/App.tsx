import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Market from './pages/Market'
import Analysis from './pages/Analysis'
import Settings from './pages/Settings'
import Portfolio from './pages/Portfolio'
import ResearchWorkspace from './pages/ResearchWorkspace'
import Login from './pages/Login'
import SectorRotation from './pages/SectorRotation'
import AIChat from './pages/AIChat'
import MarketTreemap from './pages/MarketIntel/MarketTreemap'
import MarketHeatmap from './pages/MarketIntel/MarketHeatmap'
import StrategyBuilder from './pages/StrategyBuilder/StrategyBuilder'
import PaperTrading from './pages/StrategyBuilder/PaperTrading'
import EconomicCalendar from './pages/Calendar/EconomicCalendar'
import Journal from './pages/Journal'
import Ranking from './pages/Ranking'
import Admin from './pages/Admin'
import StressTest from './pages/MarketIntel/StressTest'
import OptionsVisualizer from './pages/Options/OptionsVisualizer'

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
                <Route path="/" element={<Dashboard />} />
                <Route path="/market" element={<Market />} />
                <Route path="/treemap" element={<MarketTreemap />} />
                <Route path="/heatmap" element={<MarketHeatmap />} />
                <Route path="/portfolio" element={<Portfolio />} />
                <Route path="/research" element={<ResearchWorkspace />} />
                <Route path="/stress-test" element={<StressTest />} />
                <Route path="/analysis" element={<Analysis />} />
                <Route path="/chat" element={<AIChat />} />
                <Route path="/options" element={<OptionsVisualizer />} />
                <Route path="/strategy" element={<StrategyBuilder />} />
                <Route path="/paper-trading" element={<PaperTrading />} />
                <Route path="/journal" element={<Journal />} />
                <Route path="/calendar" element={<EconomicCalendar />} />
                <Route path="/ranking" element={<Ranking />} />
                <Route path="/admin" element={<Admin />} />
                <Route path="/sectors" element={<SectorRotation />} />
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
