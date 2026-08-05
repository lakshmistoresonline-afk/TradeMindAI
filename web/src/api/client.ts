import axios from 'axios';
import { auth } from '../core/firebase';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://trademind-api-m8jg.onrender.com/api/v1';

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
