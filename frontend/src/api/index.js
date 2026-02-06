// frontend/src/api/index.js
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000';

// Centralized API client factory
export const createApi = (accessToken = null, apiToken = null) => {

  async function fetchJSON(url, opts = {}) {
    const headers = opts.headers ? { ...opts.headers } : {};

    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    } else if (apiToken) {
      headers['Authorization'] = `Token ${apiToken}`;
    }

    const res = await fetch(url, { ...opts, headers });
    if (!res.ok) {
      // Attempt to parse JSON error, fallback to text
      let errorData = { message: `Request failed ${res.status}` };
      try {
        errorData = await res.json();
      } catch {
        errorData.message = await res.text();
      }
      throw new Error(errorData.msg || errorData.message);
    }
    return res.json();
  }

  // Auth / User (specific for JWT login, others will use generic fetchJSON)
  async function login(email, password) {
    return fetchJSON(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
  }

  async function refreshToken(currentRefreshToken) {
    return fetchJSON(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${currentRefreshToken}`
      }
    });
  }

  async function register(name, email, password, role) {
    return fetchJSON(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password, role })
    });
  }

  // Legacy API token login (for DevAuth)
  async function legacyLogin(userId) {
    return fetchJSON(`${API_BASE}/users/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    });
  }

  // Fetch current user (works with both JWT and API token via backend)
  async function fetchMe() {
    return fetchJSON(`${API_BASE}/users/me`);
  }

  // Patients
  async function fetchPatients() {
    return fetchJSON(`${API_BASE}/patients`);
  }

  async function getPatient(patientId) {
    return fetchJSON(`${API_BASE}/patients/${patientId}`);
  }

  async function updatePatient(patientId, data) {
    return fetchJSON(`${API_BASE}/patients/${patientId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  }

  // Vitals
  async function fetchVitals(limit = 100) {
    const data = await fetchJSON(`${API_BASE}/patients/vitals?limit=${limit}`);
    // data is list of vitals sorted desc; convert to series aggregated by time (simple approach: take last N samples)
    const items = data.slice().reverse(); // ascending
    const timestamps = items.map(i => new Date(i.timestamp).toLocaleTimeString());
    const heartRate = items.map(i => i.heart_rate);
    const temperature = items.map(i => i.temperature);
    const spo2 = items.map(i => i.spo2);
    return { timestamps, heartRate, temperature, spo2 };
  }

  async function fetchPatientVitals(patientId, limit = 100) {
    return fetchJSON(`${API_BASE}/patients/${patientId}/vitals?limit=${limit}`);
  }

  async function submitVitals(patientId, heart_rate, temperature, spo2) {
    return fetchJSON(`${API_BASE}/patients/${patientId}/vitals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ heart_rate, temperature, spo2 })
    });
  }

  // Alerts
  async function fetchAlerts({ role } = {}) {
    const q = role ? `?role=${role}` : '';
    return fetchJSON(`${API_BASE}/alerts${q}`);
  }

  async function fetchEscalatedAlerts() {
    return fetchJSON(`${API_BASE}/alerts/escalated`);
  }

  async function escalateAlert(alertId) {
    return fetchJSON(`${API_BASE}/alerts/${alertId}/escalate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}) // Backend determines escalated_by
    });
  }

  async function reviewAlert(alertId) {
    return fetchJSON(`${API_BASE}/alerts/${alertId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
  }

  async function closeAlert(alertId) {
    return fetchJSON(`${API_BASE}/alerts/${alertId}/close`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
  }

  // Notes
  async function fetchPatientNotes(patientId) {
    return fetchJSON(`${API_BASE}/patients/${patientId}/notes`);
  }

  async function addPatientNote(patientId, content) {
    return fetchJSON(`${API_BASE}/patients/${patientId}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    });
  }

  async function deletePatientNote(patientId, noteId) {
    return fetchJSON(`${API_BASE}/patients/${patientId}/notes/${noteId}`, {
      method: 'DELETE'
    });
  }

  // Analytics
  async function getPatientRiskScore(patientId) {
    return fetchJSON(`${API_BASE}/analytics/patients/${patientId}/risk`);
  }

  async function getPatientVitalTrends(patientId, vitalType, hours = 24, interval = 60) {
    return fetchJSON(`${API_BASE}/analytics/patients/${patientId}/trends/${vitalType}?hours=${hours}&interval=${interval}`);
  }

  async function getDashboardSummary() {
    return fetchJSON(`${API_BASE}/analytics/dashboard/summary`);
  }


  return {
    login,
    refreshToken,
    register,
    legacyLogin,
    fetchMe,
    fetchPatients,
    getPatient,
    updatePatient,
    fetchVitals,
    fetchPatientVitals,
    submitVitals,
    fetchAlerts,
    fetchEscalatedAlerts,
    escalateAlert,
    reviewAlert,
    closeAlert,
    fetchPatientNotes,
    addPatientNote,
    deletePatientNote,
    getPatientRiskScore,
    getPatientVitalTrends,
    getDashboardSummary,
  };
};