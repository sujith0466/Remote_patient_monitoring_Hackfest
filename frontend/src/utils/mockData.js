export const sampleVitals = {
  timestamps: ['10:00', '10:05', '10:10', '10:15', '10:20'],
  heartRate: [72, 75, 78, 80, 77],
  temperature: [36.6, 36.7, 36.8, 37.0, 36.9],
  spo2: [98, 97, 96, 95, 96]
}

export const samplePatients = [
  { id: 'p1', name: 'Patient A', heartRate: 78, temperature: 38.1, spo2: 97, lastSeen: '10:21' },
  { id: 'p2', name: 'Patient B', heartRate: 65, temperature: 36.8, spo2: 88, lastSeen: '10:18' },
  { id: 'p3', name: 'Patient C', heartRate: 82, temperature: 37.0, spo2: 95, lastSeen: '10:15' }
]

export const sampleAlerts = [
  { id: 'a1', title: 'High Temp: Patient A', patientId: 'p1', time: '10:21', details: 'Temp 38.1°C — rule-based threshold exceeded', alertLevel: 'critical', escalated: false },
  { id: 'a2', title: 'Low SpO₂: Patient B', patientId: 'p2', time: '10:18', details: 'SpO₂ 88% — rule-based threshold exceeded', alertLevel: 'critical', escalated: true },
  { id: 'a3', title: 'Mild Temp: Patient C', patientId: 'p3', time: '10:12', details: 'Temp 37.8°C — near threshold', alertLevel: 'warning', escalated: false }
]

export const samplePatientTrends = {
  p1: {
    timestamps: ['09:50','10:00','10:10','10:20','10:30'],
    heartRate: [74,76,78,77,78],
    temperature: [37.5,37.8,38.0,38.1,38.1],
    spo2: [98,97,97,97,97]
  },
  p2: {
    timestamps: ['09:50','10:00','10:10','10:20','10:30'],
    heartRate: [70,68,66,65,65],
    temperature: [36.7,36.8,36.8,36.8,36.8],
    spo2: [96,94,91,89,88]
  },
  p3: {
    timestamps: ['09:50','10:00','10:10','10:20','10:30'],
    heartRate: [80,81,82,82,82],
    temperature: [36.9,37.0,37.1,37.0,37.0],
    spo2: [97,96,96,95,95]
  }
}

export const escalatedAlerts = sampleAlerts.filter(a => a.escalated)


