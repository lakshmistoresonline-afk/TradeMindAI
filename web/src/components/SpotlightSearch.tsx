import { useState, useEffect } from 'react';
import { Dialog, DialogContent, Box, InputBase, Typography, Stack, Chip, Divider, alpha } from '@mui/material';
import { Search, Zap, LayoutDashboard, TrendingUp, ShieldCheck, FileText, User, ArrowRight, CornerDownLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { MONO_FONT, COLORS } from '../theme/institutionalTheme';

const QUICK_STOCKS = [
  { symbol: 'LT', name: 'Larsen & Toubro Limited', price: '₹3,876.20' },
  { symbol: 'TATAMOTORS', name: 'Tata Motors Limited', price: '₹968.45' },
  { symbol: 'TCS', name: 'Tata Consultancy Services Limited', price: '₹2,082.00' },
  { symbol: 'RELIANCE', name: 'Reliance Industries Limited', price: '₹1,226.00' },
  { symbol: 'INFY', name: 'Infosys Limited', price: '₹1,000.20' },
  { symbol: 'HDFCBANK', name: 'HDFC Bank Limited', price: '₹735.60' },
  { symbol: 'ICICIBANK', name: 'ICICI Bank Limited', price: '₹1,326.80' },
  { symbol: 'SBIN', name: 'State Bank of India', price: '₹983.00' },
  { symbol: 'M&M', name: 'Mahindra & Mahindra Limited', price: '₹3,035.00' },
  { symbol: 'MARUTI', name: 'Maruti Suzuki India Limited', price: '₹12,065.00' },
  { symbol: 'SUNPHARMA', name: 'Sun Pharmaceutical Industries Limited', price: '₹1,852.20' }
];

const PAGES_NAV = [
  { label: 'Executive Dashboard', path: '/dashboard', icon: <LayoutDashboard size={18} color={COLORS.cyan} /> },
  { label: 'Signal Operations Terminal', path: '/signals', icon: <Zap size={18} color={COLORS.green} /> },
  { label: 'Performance Track Record', path: '/performance', icon: <TrendingUp size={18} color={COLORS.purple} /> },
  { label: 'Pricing & Subscription Tiers', path: '/pricing', icon: <FileText size={18} color={COLORS.cyan} /> },
  { label: 'Trust Center & Audit Integrity', path: '/trust', icon: <ShieldCheck size={18} color={COLORS.green} /> },
  { label: 'Account & Settings', path: '/account', icon: <User size={18} color={COLORS.slateText} /> }
];

interface SpotlightSearchProps {
  open?: boolean;
  onClose?: () => void;
}

export default function SpotlightSearch({ open: externalOpen, onClose: externalOnClose }: SpotlightSearchProps) {
  const navigate = useNavigate();
  const [internalOpen, setInternalOpen] = useState(false);
  const [query, setQuery] = useState('');

  const isOpen = externalOpen !== undefined ? externalOpen : internalOpen;

  const handleClose = () => {
    if (externalOnClose) externalOnClose();
    else setInternalOpen(false);
    setQuery('');
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setInternalOpen(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const filteredStocks = QUICK_STOCKS.filter(s =>
    s.symbol.toLowerCase().includes(query.toLowerCase()) ||
    s.name.toLowerCase().includes(query.toLowerCase())
  );

  const filteredPages = PAGES_NAV.filter(p =>
    p.label.toLowerCase().includes(query.toLowerCase()) ||
    p.path.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (path: string) => {
    navigate(path);
    handleClose();
  };

  return (
    <Dialog
      open={isOpen}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          bgcolor: 'rgba(15, 23, 42, 0.95)',
          border: `1px solid ${COLORS.borderCyan}`,
          borderRadius: 3,
          backdropFilter: 'blur(20px)',
          boxShadow: '0 25px 50px -12px rgba(0, 209, 255, 0.25)',
          overflow: 'hidden',
        }
      }}
    >
      <DialogContent sx={{ p: 0 }}>
        {/* Input Bar */}
        <Box sx={{
          p: 2.5,
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          borderBottom: `1px solid ${COLORS.borderLight}`,
          bgcolor: 'rgba(2, 6, 23, 0.6)'
        }}>
          <Search size={22} color={COLORS.cyan} />
          <InputBase
            autoFocus
            placeholder="Search stocks, signals, pages... (Ctrl + K)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            sx={{
              flex: 1,
              color: '#fff',
              fontSize: '1rem',
              fontWeight: 700,
              fontFamily: MONO_FONT
            }}
          />
          <Chip label="ESC" size="small" sx={{ bgcolor: 'rgba(255,255,255,0.08)', color: COLORS.slateText, fontWeight: 900, fontFamily: MONO_FONT }} />
        </Box>

        {/* Results Stream */}
        <Box sx={{ p: 2, maxHeight: 420, overflowY: 'auto' }}>
          {/* Stocks Section */}
          {filteredStocks.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="caption" sx={{ px: 1.5, mb: 1, display: 'block', fontWeight: 950, color: COLORS.slateMuted, letterSpacing: 1.5, fontFamily: MONO_FONT }}>
                EQUITY STOCKS & SIGNALS
              </Typography>
              <Stack spacing={0.5}>
                {filteredStocks.map(s => (
                  <Box
                    key={s.symbol}
                    onClick={() => handleSelect(`/signals`)}
                    sx={{
                      p: 1.5,
                      borderRadius: 1.5,
                      display: 'flex',
                      justify: 'space-between',
                      alignItems: 'center',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease-in-out',
                      '&:hover': { bgcolor: alpha(COLORS.cyan, 0.1), border: `1px solid ${COLORS.borderCyan}` }
                    }}
                  >
                    <Stack direction="row" spacing={1.5} alignItems="center">
                      <Chip label={s.symbol} size="small" sx={{ bgcolor: alpha(COLORS.cyan, 0.15), color: COLORS.cyan, fontWeight: 950, fontFamily: MONO_FONT }} />
                      <Typography variant="body2" sx={{ fontWeight: 700, color: '#fff' }}>{s.name}</Typography>
                    </Stack>
                    <Stack direction="row" spacing={1.5} alignItems="center">
                      <Typography variant="caption" sx={{ fontWeight: 950, color: COLORS.green, fontFamily: MONO_FONT }}>{s.price}</Typography>
                      <CornerDownLeft size={14} color={COLORS.slateMuted} />
                    </Stack>
                  </Box>
                ))}
              </Stack>
            </Box>
          )}

          {/* Pages Section */}
          {filteredPages.length > 0 && (
            <Box sx={{ mb: 1 }}>
              <Typography variant="caption" sx={{ px: 1.5, mb: 1, display: 'block', fontWeight: 950, color: COLORS.slateMuted, letterSpacing: 1.5, fontFamily: MONO_FONT }}>
                NAVIGATION & PAGES
              </Typography>
              <Stack spacing={0.5}>
                {filteredPages.map(p => (
                  <Box
                    key={p.path}
                    onClick={() => handleSelect(p.path)}
                    sx={{
                      p: 1.5,
                      borderRadius: 1.5,
                      display: 'flex',
                      justify: 'space-between',
                      alignItems: 'center',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease-in-out',
                      '&:hover': { bgcolor: alpha(COLORS.purple, 0.1), border: `1px solid ${COLORS.borderPurple}` }
                    }}
                  >
                    <Stack direction="row" spacing={1.5} alignItems="center">
                      {p.icon}
                      <Typography variant="body2" sx={{ fontWeight: 800, color: '#fff' }}>{p.label}</Typography>
                    </Stack>
                    <ArrowRight size={14} color={COLORS.slateMuted} />
                  </Box>
                ))}
              </Stack>
            </Box>
          )}

          {filteredStocks.length === 0 && filteredPages.length === 0 && (
            <Box sx={{ py: 6, textAlign: 'center' }}>
              <Typography variant="body2" sx={{ color: COLORS.slateMuted, fontWeight: 800 }}>
                No matching stocks or commands found for "{query}".
              </Typography>
            </Box>
          )}
        </Box>

        <Divider sx={{ opacity: 0.08 }} />
        <Box sx={{ p: 1.5, px: 2.5, bgcolor: 'rgba(2, 6, 23, 0.8)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="caption" sx={{ color: COLORS.slateMuted, fontWeight: 700, fontSize: '0.65rem' }}>
            Tip: Press <span style={{ color: COLORS.cyan, fontWeight: 900 }}>Ctrl + K</span> anywhere to open Spotlight Search
          </Typography>
          <Typography variant="caption" sx={{ color: COLORS.purple, fontWeight: 950, fontFamily: MONO_FONT, fontSize: '0.65rem' }}>
            TRADEMIND V3.3
          </Typography>
        </Box>
      </DialogContent>
    </Dialog>
  );
}
