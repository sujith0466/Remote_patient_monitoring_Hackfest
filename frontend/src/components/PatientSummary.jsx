import React from 'react'
import MiniTrend from './MiniTrend'

export default function PatientSummary({ patients = [], trends = {} }){
  if(!patients.length) return <p className="text-sm text-gray-500">No patients</p>

  return (
    <ul className="space-y-3">
      {patients.map((p) => {
        const trend = trends[p.id]
        const hr = p.heartRate ?? (p.latest && p.latest.heart_rate) ?? null
        const temperature = p.temperature ?? (p.latest && p.latest.temperature) ?? null
        const spo2 = p.spo2 ?? (p.latest && p.latest.spo2) ?? null
        const atRisk = (spo2 !== null && spo2 < 90) || (temperature !== null && temperature >= 38) || (hr !== null && hr > 100)
        return (
          <li key={p.id} className="border p-3 rounded flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div>
                <div className="text-sm font-semibold">{p.name}</div>
                <div className="text-xs text-gray-600">Room: {p.room} • {p.age ? `${p.age} yrs` : 'Age N/A'} • {p.sex || 'Sex N/A'}</div>
                <div className="text-sm mt-1">HR: {hr ?? '—'} bpm • Temp: {temperature ?? '—'}°C • SpO₂: {spo2 ?? '—'}%</div>
                {p.notes ? <div className="text-xs text-gray-500 mt-1">Notes: {p.notes}</div> : null}
              </div>
              <div>
                {trend ? (
                  <MiniTrend labels={trend.timestamps} data={trend.heartRate} color={atRisk ? '#ef4444' : '#3b82f6'} />
                ) : null}
              </div>
            </div>

            <div className="text-right">
              <div className={`text-sm font-medium ${ atRisk ? 'text-red-700' : 'text-green-700' }`}>
                { atRisk ? 'At Risk' : 'Stable' }
              </div>
              <div className="text-xs text-gray-500 mt-1">Trend: <span className="font-medium">{trend ? 'Recent HR' : 'No trend'}</span></div>
            </div>
          </li>
        )
      })}
    </ul>
  )
}
