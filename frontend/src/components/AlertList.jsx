import React, { useState, useEffect } from 'react'

export default function AlertList({ alerts = [], showEscalate = false, onEscalate }){
  const [escalatedIds, setEscalatedIds] = useState(() => alerts.filter(a => a.escalated).map(a => a.id))

  useEffect(() => {
    setEscalatedIds(alerts.filter(a => a.escalated).map(a => a.id))
  }, [alerts])

  if(!alerts.length) return <p className="text-sm text-gray-500">No alerts</p>
  return (
    <ul className="space-y-3">
      {alerts.map((a) => {
        const isCritical = a.alertLevel === 'critical' || a.severity === 'critical'
        const isEscalated = escalatedIds.includes(a.id)
        return (
          <li key={a.id} className="border p-3 rounded flex justify-between items-start">
            <div>
              <div className="flex items-center space-x-2">
                <div className="text-sm font-semibold">{a.title || a.message}</div>
                {isCritical && <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">Critical</span>}
                {((a.alertLevel === 'warning') || (a.severity === 'warning')) && <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded">Warning</span>}
              </div>
              <div className="text-xs text-gray-600">{a.time || a.created_at} — Patient: {a.patientId || a.patient_id}</div>
              <div className="text-sm mt-1">{a.details || a.message}</div>
            </div>
            <div>
              {isEscalated ? (
                <span className="text-sm text-green-700 font-semibold">Escalated</span>
              ) : (
                showEscalate && isCritical && (
                  <button
                    onClick={() => {
                      setEscalatedIds((s) => [...s, a.id])
                      onEscalate && onEscalate(a.id)
                    }}
                    className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded"
                  >
                    Escalate
                  </button>
                )
              )}
            </div>
          </li>
        )
      })}
    </ul>
  )
}
