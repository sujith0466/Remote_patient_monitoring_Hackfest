import React, { useState } from 'react'
import { updatePatient } from '../api'

export default function PatientVitalsList({ patients = [], onUpdated }) {
  const role = localStorage.getItem("carewatch_role") // ✅ simple & reliable
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState({})

  if (!patients.length)
    return <p className="text-sm text-gray-500">No patients</p>

  const startEdit = (p) => {
    setEditingId(p.id)
    setForm({
      age: p.age || '',
      sex: p.sex || '',
      room: p.room || '',
      weight_kg: p.weight_kg || '',
      notes: p.notes || ''
    })
  }

  const cancelEdit = () => {
    setEditingId(null)
    setForm({})
  }

  const save = async (id) => {
    try {
      await updatePatient(id, form)
      if (typeof onUpdated === 'function') onUpdated()
      window.dispatchEvent(new Event('patients:updated'))
      cancelEdit()
    } catch {
      alert('Failed to save patient details')
    }
  }

  return (
    <ul className="space-y-3">
      {patients.map((p) => (
        <li key={p.id} className="border p-3 rounded flex items-center justify-between">
          <div>
            <div className="text-sm font-semibold">{p.name}</div>
            <div className="text-xs text-gray-600">
              Room: {p.room} • {p.age ? `${p.age} yrs` : 'Age N/A'} • {p.sex || 'Sex N/A'}
            </div>
            <div className="text-sm mt-1">
              HR: {p.heartRate ?? '—'} bpm • Temp: {p.temperature ?? '—'}°C • SpO₂: {p.spo2 ?? '—'}%
            </div>
            {p.notes && (
              <div className="text-xs text-gray-500 mt-1">Notes: {p.notes}</div>
            )}
          </div>

          <div className="text-right space-y-2">
            {editingId === p.id ? (
              <div className="space-y-2 text-left">
                <div className="flex space-x-2">
                  <input className="border px-2 py-1 text-sm" placeholder="age"
                    value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} />
                  <input className="border px-2 py-1 text-sm" placeholder="sex"
                    value={form.sex} onChange={(e) => setForm({ ...form, sex: e.target.value })} />
                </div>
                <div className="flex space-x-2">
                  <input className="border px-2 py-1 text-sm" placeholder="room"
                    value={form.room} onChange={(e) => setForm({ ...form, room: e.target.value })} />
                  <input className="border px-2 py-1 text-sm" placeholder="weight"
                    value={form.weight_kg} onChange={(e) => setForm({ ...form, weight_kg: e.target.value })} />
                </div>
                <textarea className="border w-full px-2 py-1 text-sm" placeholder="notes"
                  value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
                <div className="flex space-x-2">
                  <button className="bg-blue-600 text-white px-2 py-1 rounded text-sm"
                    onClick={() => save(p.id)}>Save</button>
                  <button className="bg-gray-200 px-2 py-1 rounded text-sm"
                    onClick={cancelEdit}>Cancel</button>
                </div>
              </div>
            ) : (
              <div>
                {(p.spo2 < 90 || p.temperature >= 38 || p.heartRate > 100) ? (
                  <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">Needs Attention</span>
                ) : (
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Stable</span>
                )}

                <div className="mt-2">
                  {(role === 'nurse' || role === 'doctor') ? (
                    <button className="text-sm text-blue-600 hover:underline"
                      onClick={() => startEdit(p)}>Edit Details</button>
                  ) : (
                    <button className="text-sm text-gray-400" disabled>Login to edit</button>
                  )}
                </div>
              </div>
            )}
          </div>
        </li>
      ))}
    </ul>
  )
}
