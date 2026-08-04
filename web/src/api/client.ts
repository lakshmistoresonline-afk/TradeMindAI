import axios from 'axios';

const API_BASE_URL = 'https://trademind-api-euba.onrender.com/api/v1';

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

export const getStockDetail = async (symbol: str) => {
  const response = await apiClient.get(`/stocks/${symbol}`);
  return response.data;
};
