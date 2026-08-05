import axios from 'axios';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'https://trademind-api-m8jg.onrender.com/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getStocks = async () => {
  const response = await apiClient.get('/stocks');
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

export const triggerBatchAnalysis = async () => {
  const response = await apiClient.post('/analysis/trigger');
  return response.data;
};

export const triggerBacktest = async (symbol: string) => {
  const response = await apiClient.post(`/analysis/backtest/${symbol}`);
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

export const getMarketRegime = async () => {
  const response = await apiClient.get('/ios/regime');
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

export const getResearchNotes = async (symbol: string) => {
  const response = await apiClient.get(`/ios/notes/${symbol}`);
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

export const getWorkspaces = async () => {
  const response = await apiClient.get('/ios/workspaces');
  return response.data;
};

export const saveWorkspace = async (workspace: any) => {
  const response = await apiClient.post('/ios/workspaces', workspace);
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

export const chatWithAssistant = async (message: string) => {
  const response = await apiClient.post('/ai/chat', { message });
  return response.data.response;
};
