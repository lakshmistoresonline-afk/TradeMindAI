import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Increased to 60s for Render Free Tier cold starts
  headers: {
    'Content-Type': 'application/json'
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error Detected:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const getStocks = async (limit: number = 300) => {
  const response = await apiClient.get(`/stocks/?limit=${limit}`);
  return response.data;
};

export const getMarketStats = async () => {
  const response = await apiClient.get('/stocks/market-stats');
  return response.data;
};

export const getDataHealth = async () => {
  const response = await apiClient.get('/system/health/');
  return response.data;
};

// Canonical Equity Intelligence API (Phase 35)
export const getEquitySignals = async (params: any = {}) => {
  try {
    const response = await apiClient.get('/equity/signals', { params, timeout: 10000 });
    return Array.isArray(response.data) ? response.data : [];
  } catch (err) {
    console.warn('Equity signals REST API fallback (using Firestore Mirror):', err);
    return [];
  }
};

export const getEquitySignalDetail = async (id: string) => {
  try {
    const response = await apiClient.get(`/equity/signals/${id}`);
    return response.data;
  } catch (err) {
    return null;
  }
};

export const getEquitySignalForensics = async (id: string) => {
  try {
    const response = await apiClient.get(`/equity/signals/${id}/forensics`);
    return response.data;
  } catch (err) {
    return null;
  }
};

export const getEquityPerformance = async () => {
  try {
    const response = await apiClient.get('/equity/performance', { timeout: 15000 });
    return response.data;
  } catch (err) {
    console.error('Equity performance fetch failed:', err);
    return { sample_size: 0, wins: 0, losses: 0, win_rate: 0.0, profit_factor: 0.0, expectancy: 0.0, net_pnl: 0.0, brier_score: 0.0 };
  }
};

export const getEquityAccuracy = async () => {
  try {
    const response = await apiClient.get('/equity/accuracy', { timeout: 15000 });
    return response.data;
  } catch (err) {
    console.error('Equity accuracy fetch failed:', err);
    return {
      horizons: {
        SHORT: { sample_size: 0, auc: 0.0, win_rate: 0.0, brier: 0.0, logloss: 0.0, ece: 0.0 },
        SWING: { sample_size: 0, auc: 0.0, win_rate: 0.0, brier: 0.0, logloss: 0.0, ece: 0.0 },
        LONG:  { sample_size: 0, auc: 0.0, win_rate: 0.0, brier: 0.0, logloss: 0.0, ece: 0.0 }
      },
      verified_benchmark: { n: 0, win_rate: 0.0, profit_factor: 0.0, net_pnl: 0.0 }
    };
  }
};

export const getEquityMarketState = async () => {
  try {
    const response = await apiClient.get('/equity/market', { timeout: 10000 });
    return response.data;
  } catch (err) {
    return { regime: "UNKNOWN", risk_mode: "UNKNOWN", sentiment_score: 0.0, volatility_index: 0.0 };
  }
};

export const getEquityHistory = async (params: any = {}) => {
  try {
    const response = await apiClient.get('/equity/history', { params, timeout: 20000 });
    return response.data;
  } catch (err) {
    return { records: [], total: 0, summary: { total: 0, target_hits: 0, stop_losses: 0, expired: 0 } };
  }
};

export const getUserSubscription = async () => {
  try {
    const response = await apiClient.get('/user/subscription');
    return response.data;
  } catch (err) {
    return { plan_id: 'FREE', status: 'ACTIVE' };
  }
};

export const getUserReferrals = async () => {
  try {
    const response = await apiClient.get('/user/referrals');
    return Array.isArray(response.data) ? response.data : [];
  } catch (err) {
    return [];
  }
};

// --- OBSOLETE / DEPRECATED ENDPOINTS (Satisfying legacy components) ---
export const getPortfolioOptimizations = async (..._args: any[]) => ([]);
export const getResearchNotes = async (..._args: any[]) => ([]);
export const getShadowAnalytics = async () => {
  const response = await apiClient.get('/admin/shadow-analytics');
  return response.data;
};

export const saveResearchNote = async (..._args: any[]) => ({});
export const getStockNews = async (..._args: any[]) => ([]);
export const getStockTimeline = async (..._args: any[]) => ([]);
export const getSimilarPatterns = async (..._args: any[]) => ([]);
export const getStockEarnings = async (..._args: any[]) => ([]);
export const getInstitutionalFlow = async (..._args: any[]) => ({});
export const getBulkDeals = async (..._args: any[]) => ([]);
export const getKnowledgeGraphData = async (..._args: any[]) => ({});
export const getCorrelations = async (..._args: any[]) => ([]);
export const getPortfolioHedge = async (..._args: any[]) => ({});
export const getMTFAlignment = async (..._args: any[]) => ({});
export const getOptionChain = async (..._args: any[]) => ({});
export const getGlobalPerformance = async (..._args: any[]) => ([]);
export const getMarketRegime = async (..._args: any[]) => ({});
export const getMarketIntelligence = async (..._args: any[]) => ({});
export const getOpportunities = async (..._args: any[]) => ([]);
export const getTradeJournal = async (..._args: any[]) => ([]);
export const getPortfolioHealth = async (..._args: any[]) => ({});
export const getAPIKeys = async (..._args: any[]) => ([]);
export const generateAPIKey = async (..._args: any[]) => ({});
export const getShadowSignals = async (..._args: any[]) => ({ signals: [] });
export const getPerformanceSummary = async (..._args: any[]) => ({});
export const getPerformanceSignals = async (..._args: any[]) => ([]);
export const getCalibrationData = async (..._args: any[]) => ({});
export const chatWithAssistant = async (..._args: any[]) => ({ response: "Assistant disabled." });
