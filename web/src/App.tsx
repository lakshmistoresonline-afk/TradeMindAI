import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Box, Typography, ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Market from './pages/Market'
import Analysis from './pages/Analysis'

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
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/market" element={<Market />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/settings" element={<Box p={4}><Typography>Settings coming soon...</Typography></Box>} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  )
}

export default App
