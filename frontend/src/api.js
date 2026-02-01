// frontend/src/api.js

const API_BASE = "" // same-origin (Vite proxy / Flask dev server)

// -----------------------------
// Token helpers
// -----------------------------
export function setAuthToken(token) {
  if (token) {
    localStorage.setItem("carewatch_token", token)
  } else {
    localStorage.removeItem("carewatch_token")
  }
}

export function getAuthToken() {
  return localStorage.getItem("carewatch_token")
}

function authHeaders() {
  const token = getAuthToken()
  return token ? { Authorization: `Token ${token}` } : {}
}

// -----------------------------
// Auth / User
// -----------------------------
export async function fetchMe() {
  const res = await fetch(`${API_BASE}/users/me`, {
    headers: {
      ...authHeaders()
    }
  })

  if (!res.ok) {
    throw new Error("Not authenticated")
  }

  return res.json()
}

// -----------------------------
// Patients
// -----------------------------
export async function fetchPatients() {
  const res = await fetch(`${API_BASE}/patients/`)
  if (!res.ok) throw new Error("Failed to fetch patients")
  return res.json()
}

export async function updatePatient(patientId, data) {
  const res = await fetch(`${API_BASE}/patients/${patientId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders()
    },
    body: JSON.stringify(data)
  })

  if (!res.ok) throw new Error("Failed to update patient")
  return res.json()
}

// -----------------------------
// Vitals
// -----------------------------
export async function fetchVitals(limit = 100) {
  const res = await fetch(`${API_BASE}/patients/vitals?limit=${limit}`)
  if (!res.ok) throw new Error("Failed to fetch vitals")
  return res.json()
}

export async function fetchPatientLatestVital(patientId) {
  const res = await fetch(`${API_BASE}/patients/${patientId}/vitals?limit=1`)
  if (!res.ok) return null
  const data = await res.json()
  return data[0] || null
}

// -----------------------------
// Alerts
// -----------------------------
export async function fetchAlerts({ role } = {}) {
  const qs = role ? `?role=${role}` : ""
  const res = await fetch(`${API_BASE}/alerts/${qs}`)
  if (!res.ok) throw new Error("Failed to fetch alerts")
  return res.json()
}

export async function fetchEscalatedAlerts() {
  const res = await fetch(`${API_BASE}/alerts/escalated`, {
    headers: {
      ...authHeaders()
    }
  })

  if (!res.ok) throw new Error("Failed to fetch escalated alerts")
  return res.json()
}

export async function escalateAlert(alertId, nurseId) {
  const res = await fetch(`${API_BASE}/alerts/${alertId}/escalate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ escalated_by: nurseId })
  })

  if (!res.ok) throw new Error("Failed to escalate alert")
  return res.json()
}
