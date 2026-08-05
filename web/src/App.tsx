import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Market from './pages/Market'
import Analysis from './pages/Analysis'
import Settings from './pages/Settings'
import Portfolio from './pages/Portfolio'
import Login from './pages/Login'
import SectorRotation from './pages/SectorRotation'
import AIChat from './pages/AIChat'
import MarketTreemap from './pages/MarketIntel/MarketTreemap'
import MarketHeatmap from './pages/MarketIntel/MarketHeatmap'
import StrategyBuilder from './pages/StrategyBuilder/StrategyBuilder'
import PaperTrading from './pages/StrategyBuilder/PaperTrading'
import EconomicCalendar from './pages/Calendar/EconomicCalendar'
import StressTest from './pages/MarketIntel/StressTest'

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
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid #334155',
        },
      },
    },
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
                <Route path="/analysis" element={<Analysis />} />
                <Route path="/chat" element={<AIChat />} />
                <Route path="/options" element={<OptionsVisualizer />} />
                <Route path="/strategy" element={<StrategyBuilder />} />
                <Route path="/paper-trading" element={<PaperTrading />} />
                <Route path="/calendar" element={<EconomicCalendar />} />
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
