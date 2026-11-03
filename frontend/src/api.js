const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

async function request(path) {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Error ${res.status}`)
  }
  return res.json()
}

export const api = {
  health: () => request('/api/health'),
  brands: () => request('/api/brands'),
  models: (brandId) => request(`/api/brands/${brandId}/models`),
  years: (modelId) => request(`/api/models/${modelId}/years`),
  engines: (yearId) => request(`/api/years/${yearId}/engines`),
  vehicle: (engineId) => request(`/api/engines/${engineId}`),
}
