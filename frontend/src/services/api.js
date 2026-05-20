import axios from 'axios'

/** Base URL from `frontend/.env` → `VITE_API_URL` (see `.env.example`). */
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL,
})
export const getStats = () => api.get('/api/stats')
export const getDatasets = () => api.get('/api/datasets')
export const uploadDataset = (formData) =>
  api.post('/api/upload-dataset', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
export const getContacts = (id) => api.get(`/api/datasets/${id}/contacts`)
export const deleteDataset = (id) => api.delete(`/api/datasets/${id}`)

export const getCampaigns = () => api.get('/api/campaigns')
export const getCampaign = (id) => api.get(`/api/campaigns/${id}`)
export const sendCampaign = (id) => api.post(`/api/campaigns/${id}/send`)
export const getCampaignLogs = (id) => api.get(`/api/campaigns/${id}/logs`)
export const deleteCampaign = (id) => api.delete(`/api/campaigns/${id}`)

export const sendChat = (prompt, options = {}) =>
  api.post(
    '/api/chat',
    { prompt, skip_clarification: options.skipClarification ?? false },
    { timeout: 240000 },
  )
export const getChatHistory = () => api.get('/api/chat/history')

export default api
