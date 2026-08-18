import axios from 'axios';

export const API_BASE_URL = 'https://trademind-api-production.up.railway.app/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer internal_demo_token'
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error Detected:', error.response?.data || error.message);

    // Master Redesign Rule: Do not return believable mock data in production.
    // Allow null/empty states so the UI can render '—' or 'Data unavailable'.

    if (error.config?.url?.includes('/opportunities')) {
       return { data: [] };
    }

    if (error.config?.url?.includes('/performance/summary')) {
       return { data: null };
    }

    if (error.config?.url?.includes('/performance/signals')) {
       return { data: [] };
    }

    if (error.config?.url?.includes('/calibration')) {
       return { data: { labels: [], win_rates: [] } };
    }

    if (error.config?.url?.includes('/stocks/')) return { data: [] };
    if (error.config?.url?.includes('/journal')) return { data: [] };
    if (error.config?.url?.includes('/deals')) return { data: [] };

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

export const getInstitutionalFlow = async () => {
  const response = await apiClient.get('/stocks/fii-dii');
  return response.data;
};

export const getStockDetail = async (symbol: string) => {
  const response = await apiClient.get(`/stocks/${symbol}`);
  return response.data;
};

export const getStockNews = async (symbol: string) => {
  const response = await apiClient.get(`/stocks/${symbol}/news`);
  return response.data;
};

export const getStockEarnings = async (symbol: string) => {
  const response = await apiClient.get(`/stocks/${symbol}/earnings`);
  return response.data;
};

export const getStockTimeline = async (symbol: string) => {
  const response = await apiClient.get(`/stocks/${symbol}/timeline`);
  return response.data;
};

export const triggerBatchAnalysis = async () => {
  const response = await apiClient.post('/analysis/trigger');
  return response.data;
};

export const triggerBacktest = async (symbol: string) => {
  const response = await apiClient.post(`/analysis/backtest/${symbol}`);
  return response.data;
};

export const getGlobalPerformance = async () => {
  const response = await apiClient.get('/analysis/backtest');
  return response.data;
};

export const getBacktestResults = async (symbol: string) => {
  const response = await apiClient.get(`/analysis/backtest/${symbol}`);
  return response.data;
};

export const getBacktestSignals = async (symbol: string) => {
  const response = await apiClient.get(`/analysis/backtest/${symbol}/signals`);
  return response.data;
};

export const getCalibrationData = async () => {
  const response = await apiClient.get('/analysis/calibration');
  return response.data;
};

export const getCorrelations = async (symbol: string) => {
  const response = await apiClient.get(`/analysis/correlation/${symbol}`);
  return response.data;
};

export const getMarketRegime = async () => {
  const response = await apiClient.get('/ios/regime');
  return response.data;
};

export const getMarketIntelligence = async (type: string = "CLOSING") => {
  const response = await apiClient.get(`/ios/intel?type=${type}`);
  return response.data;
};

export const getOpportunities = async () => {
  const response = await apiClient.get('/ios/opportunities');
  return response.data;
};

export const getKnowledgeGraphData = async (symbol: string) => {
  const response = await apiClient.get(`/ios/graph/${symbol}`);
  return response.data;
};

export const getDigitalTwin = async (symbol: string) => {
  const response = await apiClient.get(`/ios/twin/${symbol}`);
  return response.data;
};

export const getMTFAlignment = async (symbol: string) => {
  const response = await apiClient.get(`/ios/alignment/${symbol}`);
  return response.data;
};

export const getSimilarPatterns = async (symbol: string) => {
  const response = await apiClient.get(`/ios/similarity/${symbol}`);
  return response.data;
};

export const getResearchNotes = async (symbol: string) => {
  const response = await apiClient.get(`/ios/notes/${symbol}`);
  return response.data;
};

export const getBulkDeals = async (symbol?: string) => {
  const url = symbol ? `/ios/deals?symbol=${symbol}` : '/ios/deals';
  const response = await apiClient.get(url);
  return response.data;
};

export const saveResearchNote = async (note: any) => {
  const response = await apiClient.post('/ios/notes', note);
  return response.data;
};

export const getSystemEvaluation = async () => {
  const response = await apiClient.get('/admin/evaluation');
  return response.data;
};

export const getSystemLogs = async () => {
  const response = await apiClient.get('/admin/logs');
  return response.data;
};

export const getWorkspaces = async () => {
  const response = await apiClient.get('/ios/workspaces');
  return response.data;
};

export const saveWorkspace = async (workspace: any) => {
  const response = await apiClient.post('/ios/workspaces', workspace);
  return response.data;
};

export const getTradeJournal = async () => {
  const response = await apiClient.get('/ios/journal');
  return response.data;
};

export const addTradeToJournal = async (trade: any) => {
  const response = await apiClient.post('/ios/journal', trade);
  return response.data;
};

export const getPortfolioOptimizations = async () => {
  const response = await apiClient.get('/ios/portfolio/optimize');
  return response.data;
};

export const getPortfolioHealth = async () => {
  const response = await apiClient.get('/ios/portfolio/health');
  return response.data;
};

export const getPortfolioHedge = async () => {
  const response = await apiClient.get('/ios/portfolio/hedge');
  return response.data;
};

export const getAPIKeys = async () => {
  const response = await apiClient.get('/ios/api-keys');
  return response.data;
};

export const generateAPIKey = async () => {
  const response = await apiClient.post('/ios/api-keys');
  return response.data;
};

export const getEconomicCalendar = async () => {
  const response = await apiClient.get('/ios/calendar');
  return response.data;
};

export const chatWithAssistant = async (message: string) => {
  const response = await apiClient.post('/ai/chat', { message });
  return response.data.response;
};

export const getLiveSignalsAudit = async () => {
  const response = await apiClient.get('/ios/signals/live');
  return response.data;
};

export const getOptionChain = async (symbol: string) => {
  const response = await apiClient.get(`/stocks/${symbol}/option-chain`);
  return response.data;
};

export const getPerformanceSummary = async (startDate?: string, endDate?: string, timeframe?: string) => {
  let url = '/analysis/performance/summary';
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  if (timeframe) params.append('timeframe', timeframe);

  if (params.toString()) url += `?${params.toString()}`;

  const response = await apiClient.get(url);
  return response.data;
};

export const getPerformanceSignals = async (startDate?: string, endDate?: string, timeframe?: string, dataset?: string) => {
  let url = '/analysis/performance/signals';
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  if (timeframe) params.append('timeframe', timeframe);
  if (dataset) params.append('dataset', dataset);

  if (params.toString()) url += `?${params.toString()}`;

  const response = await apiClient.get(url);
  return response.data;
};

export const getDataHealth = async () => {
  const response = await apiClient.get('/admin/health');
  return response.data;
};

// Shadow Monitoring API (v2.2)
export const getShadowStatus = async () => {
  const response = await apiClient.get('/shadow/status');
  return response.data;
};

export const getShadowSummary = async () => {
  const response = await apiClient.get('/shadow/summary');
  return response.data;
};

export const getShadowActiveSignals = async () => {
  const response = await apiClient.get('/shadow/active-signals');
  return response.data;
};

export const getShadowPerformance = async () => {
  const response = await apiClient.get('/shadow/performance');
  return response.data;
};

export const getShadowUniverse = async () => {
  const response = await apiClient.get('/shadow/universe');
  return response.data;
};

export const getShadowRejections = async () => {
  const response = await apiClient.get('/shadow/rejections');
  return response.data;
};
