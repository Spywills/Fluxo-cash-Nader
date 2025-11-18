import axios from 'axios';

// Usar variável de ambiente ou fallback para desenvolvimento local
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token JWT em todas as requisições
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para tratar erros de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token inválido ou expirado
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Log da URL da API (apenas em desenvolvimento)
if (import.meta.env.DEV) {
  console.log('🔗 API URL:', API_BASE);
}

// Clients
export const getClients = () => api.get('/clients');
export const getClient = (id) => api.get(`/clients/${id}`);
export const createClient = (data) => api.post('/clients', data);
export const updateClient = (id, data) => api.put(`/clients/${id}`, data);
export const updateClientNotes = (id, notes) => api.put(`/clients/${id}/notes`, { notes });
export const deleteClient = (id) => api.delete(`/clients/${id}`);

// Balance
export const getClientBalance = (id) => api.get(`/clients/${id}/balance`);
export const getGlobalBalance = () => api.get('/global-balance');

// Withdrawals
export const createWithdrawal = (clientId, data) => api.post(`/clients/${clientId}/withdrawals`, data);
export const getWithdrawals = (clientId) => api.get(`/clients/${clientId}/withdrawals`);
export const getGlobalWithdrawals = () => api.get('/global-withdrawals');
export const updateWithdrawal = (clientId, withdrawalId, data) => api.put(`/clients/${clientId}/withdrawals/${withdrawalId}`, data);
export const deleteWithdrawal = (clientId, withdrawalId) => api.delete(`/clients/${clientId}/withdrawals/${withdrawalId}`);

// Bank Simulation (NEW)
export const getBankSimulationGlobal = () => api.get('/bank-simulation/global');
export const getBankSimulationWithdrawals = () => api.get('/bank-simulation/withdrawals');

// History
export const getClientHistory = (clientId, period = 'all') => api.get(`/clients/${clientId}/history?period=${period}`);
export const getGlobalHistory = (period = 'all') => api.get(`/bank/global/history?period=${period}`);

// Proofs (Comprovantes)
export const uploadProof = (clientId, file, description = '') => {
  const formData = new FormData();
  formData.append('file', file);
  if (description) {
    formData.append('description', description);
  }
  
  return api.post(`/proofs/clients/${clientId}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getClientProofs = (clientId) => api.get(`/proofs/clients/${clientId}`);
export const deleteProof = (proofId) => api.delete(`/proofs/${proofId}`);

// Health
export const healthCheck = () => api.get('/health');

// Auth
export const login = (username, password) => api.post('/auth/login', { username, password });
export const register = (username, email, password, full_name) => api.post('/auth/register', { username, email, password, full_name });
export const getMe = () => api.get('/auth/me');
export const logout = () => api.post('/auth/logout');

export default api;
