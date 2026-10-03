import axios from 'axios';

// Empty base URL keeps the browser on the same origin; Vite proxies /api to FastAPI in development.
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const healthCheck = async () => {
  const resp = await api.get('/api/health');
  return resp.data;
};

export const getDashboardStats = async () => {
  const resp = await api.get('/api/dashboard/stats');
  return resp.data;
};

export const investigate = async (question) => {
  const resp = await api.post('/api/investigate', { question });
  return resp.data;
};

export const searchEvidence = async (query, params = {}) => {
  const resp = await api.post('/api/evidence/search', { query, ...params });
  return resp.data;
};

export const askEvidence = async (query, academic_year, criterion) => {
  const resp = await api.post('/api/evidence/ask', { query, academic_year, criterion });
  return resp.data;
};

export const getCriteria = async () => {
  const resp = await api.get('/api/criteria');
  return resp.data;
};

export const getCriteriaCoverage = async () => {
  const resp = await api.get('/api/criteria/coverage');
  return resp.data;
};

export const getEvidenceGaps = async () => {
  const resp = await api.get('/api/gaps');
  return resp.data;
};

export const getInvestigations = async () => {
  const resp = await api.get('/api/investigations');
  return resp.data;
};

export const getInvestigation = async (id) => {
  const resp = await api.get(`/api/investigations/${id}`);
  return resp.data;
};

export const getSteps = async (id) => {
  const resp = await api.get(`/api/investigations/${id}/steps`);
  return resp.data;
};

export const getEvidence = async (id) => {
  const resp = await api.get(`/api/investigations/${id}/evidence`);
  return resp.data;
};

export const getGraph = async (id) => {
  const resp = await api.get(`/api/investigations/${id}/graph`);
  return resp.data;
};

export const getMasterGraph = async () => {
  const resp = await api.get('/api/graph/master');
  return resp.data;
};

export const getReport = async (id) => {
  const resp = await api.get(`/api/investigations/${id}/report`);
  return resp.data;
};

export const getDocuments = async (params = {}) => {
  const resp = await api.get('/api/documents', { params });
  return resp.data;
};

export const getDocument = async (id) => {
  const resp = await api.get(`/api/documents/${id}`);
  return resp.data;
};

export const getDocumentPage = async (id, pageNum = 1) => {
  const resp = await api.get(`/api/documents/${id}/pages/${pageNum}`);
  return resp.data;
};

export const getDocumentFileUrl = (id) => {
  return `${API_BASE_URL}/api/documents/${id}/file`;
};

export const getAudit = async (params = {}) => {
  const resp = await api.get('/api/audit', { params });
  return resp.data;
};

export default api;
