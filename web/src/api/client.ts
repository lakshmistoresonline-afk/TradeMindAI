import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://trademind-api-m8jg.onrender.com/api/v1';

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
  const response = await apiClient.get('/equity/signals', { params });
  return response.data;
};

export const getEquitySignalDetail = async (id: string) => {
  const response = await apiClient.get(`/equity/signals/${id}`);
  return response.data;
};

export const getEquityPerformance = async () => {
  const response = await apiClient.get('/equity/performance');
  return response.data;
};

export const getEquityAccuracy = async () => {
  const response = await apiClient.get('/equity/accuracy');
  return response.data;
};

export const getEquityMarketState = async () => {
  const response = await apiClient.get('/equity/market');
  return response.data;
};

export const getEquityHistory = async (params: any = {}) => {
  const response = await apiClient.get('/equity/history', { params });
  return response.data;
};

// User Personalization API (Phase 15)
export const getUserCharts = async () => (await apiClient.get('/user/charts')).data;
export const saveUserChart = async (data: any) => (await apiClient.post('/user/charts', data)).data;
export const getUserReports = async () => (await apiClient.get('/user/reports')).data;
export const getWatchlist = async () => (await apiClient.get('/user/watchlist')).data;
export const addToWatchlist = async (symbol: string) => (await apiClient.post(`/user/watchlist/${symbol}`)).data;
export const getUserSubscription = async () => (await apiClient.get('/user/subscription')).data;
export const getUserReferrals = async () => (await apiClient.get('/user/referrals')).data;

// --- OBSOLETE / DEPRECATED ENDPOINTS (Satisfying legacy components) ---
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
export const getPortfolioOptimizations = async (..._args: any[]) => ([]);
export const getGlobalPerformance = async (..._args: any[]) => ([]);
export const getResearchNotes = async (..._args: any[]) => ([]);
export const saveResearchNote = async (..._args: any[]) => ({});
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
