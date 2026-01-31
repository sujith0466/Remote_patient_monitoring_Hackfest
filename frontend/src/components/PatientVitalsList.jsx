import React from 'react'

export default function PatientVitalsList({ patients = [] }){
  if(!patients.length) return <p className="text-sm text-gray-500">No patients</p>

  return (
    <ul className="space-y-3">
      {patients.map((p) => (
        <li key={p.id} className="border p-3 rounded flex items-center justify-between">
          <div>
            <div className="text-sm font-semibold">{p.name}</div>
            <div className="text-xs text-gray-600">Last seen {p.lastSeen}</div>
            <div className="text-sm mt-1">HR: {p.heartRate} bpm • Temp: {p.temperature}°C • SpO₂: {p.spo2}%</div>
          </div>
          <div>
            { (p.spo2 < 90 || p.temperature >= 38.0 || p.heartRate > 100) ? (
              <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">Needs Attention</span>
            ) : (
              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Stable</span>
            )}
          </div>
        </li>
      ))}
    </ul>
  )
}
