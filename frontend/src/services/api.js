import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export default api;
