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
  const response = await apiClient.get('/equity/signals', { params, timeout: 10000 });
  return Array.isArray(response.data) ? response.data : [];
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
    const response = await apiClient.get('/equity/performance', { timeout: 10000 });
    if (response.data && response.data.verified_benchmark && response.data.verified_benchmark.n > 0) {
      return response.data;
    }
    throw new Error("Empty performance response");
  } catch (err) {
    console.warn('Equity performance REST API fallback to static /performance.json:', err);
    try {
      const fallbackRes = await fetch('/performance.json');
      const data = await fallbackRes.json();
      return data || { verified_benchmark: { n: 0, win_rate: 0, profit_factor: 0, net_pnl: 0 }, horizons: {} };
    } catch (fallbackErr) {
      console.error('Failed to load static performance.json:', fallbackErr);
      return { verified_benchmark: { n: 0, win_rate: 0, profit_factor: 0, net_pnl: 0 }, horizons: {} };
    }
  }
};

export const getEquityAccuracy = async () => {
  try {
    const response = await apiClient.get('/equity/accuracy', { timeout: 10000 });
    if (response.data && response.data.verified_benchmark && response.data.verified_benchmark.n > 0) {
      return response.data;
    }
    throw new Error("Empty accuracy response");
  } catch (err) {
    console.warn('Equity accuracy REST API fallback to static /performance.json:', err);
    try {
      const fallbackRes = await fetch('/performance.json');
      const data = await fallbackRes.json();
      return data || { verified_benchmark: { n: 0, win_rate: 0, profit_factor: 0, net_pnl: 0 }, horizons: {} };
    } catch (fallbackErr) {
      console.error('Failed to load static performance.json:', fallbackErr);
      return { verified_benchmark: { n: 0, win_rate: 0, profit_factor: 0, net_pnl: 0 }, horizons: {} };
    }
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
    const response = await apiClient.get('/equity/history', { params, timeout: 10000 });
    if (response.data && Array.isArray(response.data.records) && response.data.records.length > 0) {
      return response.data;
    }
    throw new Error("Empty history response");
  } catch (err) {
    console.warn('Equity history REST API fallback to static /signals_history.json:', err);
    try {
      const fallbackRes = await fetch('/signals_history.json');
      const data = await fallbackRes.json();
      return data || { records: [], total: 0, summary: { total: 0, target_hits: 0, stop_losses: 0, expired: 0 } };
    } catch (fallbackErr) {
      console.error('Failed to load static signals_history.json:', fallbackErr);
      return { records: [], total: 0, summary: { total: 0, target_hits: 0, stop_losses: 0, expired: 0 } };
    }
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
