const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

async function fetchJSON(url, opts) {
  const res = await fetch(url, opts)
  if (!res.ok) {
    const txt = await res.text()
    throw new Error(`Request failed ${res.status}: ${txt}`)
  }
  return res.json()
}

export async function fetchVitals(limit = 50) {
  const data = await fetchJSON(`${API_BASE}/vitals?limit=${limit}`)
  // data is list of vitals sorted desc; convert to series aggregated by time (simple approach: take last N samples)
  const items = data.slice().reverse() // ascending
  const timestamps = items.map(i => new Date(i.timestamp).toLocaleTimeString())
  const heartRate = items.map(i => i.heart_rate)
  const temperature = items.map(i => i.temperature)
  const spo2 = items.map(i => i.spo2)
  return { timestamps, heartRate, temperature, spo2 }
}

export async function fetchPatients() {
  return fetchJSON(`${API_BASE}/patients`)
}

export async function fetchPatientLatestVital(patientId) {
  const data = await fetchJSON(`${API_BASE}/patients/${patientId}/vitals?limit=1`)
  return data && data.length ? data[0] : null
}

export async function fetchAlerts({ role } = {}) {
  const q = role ? `?role=${role}` : ''
  return fetchJSON(`${API_BASE}/alerts${q}`)
}

export async function fetchEscalatedAlerts() {
  // include role=doctor so basic role check (query param) allows access when no headers are present
  return fetchJSON(`${API_BASE}/alerts/escalated?role=doctor`)
}

export async function escalateAlert(alertId, escalated_by) {
  const body = JSON.stringify({ escalated_by })
  return fetchJSON(`${API_BASE}/alerts/${alertId}/escalate`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body })
}
