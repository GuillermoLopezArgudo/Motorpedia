const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })
  const text = await res.text()
  let data = null
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = text
    }
  }
  if (!res.ok) {
    let message = `Error ${res.status}`
    if (typeof data?.detail === 'string') message = data.detail
    else if (Array.isArray(data?.detail)) message = data.detail.map((d) => d.msg).join(', ')
    else if (typeof data === 'string' && data) message = data
    throw new Error(message)
  }
  if (res.status === 204) return null
  return data
}

export const api = {
  health: () => request('/api/health'),
  bootstrap: () => request('/api/bootstrap', { method: 'POST', body: '{}' }),
  brands: () => request('/api/brands'),
  brandCatalog: () => request('/api/brands/catalog'),
  importBrands: (names) =>
    request('/api/brands/import', { method: 'POST', body: JSON.stringify({ names }) }),
  createBrand: (name) =>
    request('/api/brands', { method: 'POST', body: JSON.stringify({ name }) }),
  models: (brandId) => request(`/api/brands/${brandId}/models`),
  createModel: (brandId, name) =>
    request(`/api/brands/${brandId}/models`, {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),
  years: (modelId) => request(`/api/models/${modelId}/years`),
  createYear: (modelId, year) =>
    request(`/api/models/${modelId}/years`, {
      method: 'POST',
      body: JSON.stringify({ year: Number(year) }),
    }),
  engines: (yearId) => request(`/api/years/${yearId}/engines`),
  createEngine: (yearId, payload) =>
    request(`/api/years/${yearId}/engines`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  vehicle: (engineId) => request(`/api/engines/${engineId}`),
  updateEngine: (engineId, payload) =>
    request(`/api/engines/${engineId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  saveSheet: (engineId, payload) =>
    request(`/api/engines/${engineId}/sheet`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
  workshop: (engineId) => request(`/api/engines/${engineId}/workshop`),
  workshopFull: (engineId) => request(`/api/engines/${engineId}/workshop/full`),
  categoryItems: (engineId, slug) =>
    request(`/api/engines/${engineId}/categories/${slug}/items`),
  createWorkshopItem: (engineId, slug, payload) =>
    request(`/api/engines/${engineId}/categories/${slug}/items`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  vehiclesCatalog: () => request('/api/vehicles/catalog'),
  importVehicles: (payload = {}) =>
    request('/api/vehicles/import', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  seedContent: () =>
    request('/api/vehicles/seed-content', { method: 'POST', body: '{}' }),
}
