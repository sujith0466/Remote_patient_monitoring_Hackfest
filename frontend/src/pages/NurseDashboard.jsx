import React, { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import VitalsChart from '../components/VitalsChart'
import ParameterCharts from '../components/ParameterCharts'
import AlertList from '../components/AlertList'
import PatientVitalsList from '../components/PatientVitalsList'
import {
  fetchVitals,
  fetchPatients,
  fetchAlerts,
  fetchPatientLatestVital,
  escalateAlert
} from '../api'

export default function NurseDashboard(){
  const [vitalsData, setVitalsData] = useState({ timestamps: [], heartRate: [], temperature: [], spo2: [] })
  const [patients, setPatients] = useState([])
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load(){
      setLoading(true)
      try{
        const [vitals, patientsList, alertsList] = await Promise.all([
          fetchVitals(30),
          fetchPatients(),
          fetchAlerts({ role: 'nurse' }) // ✅ explicit nurse role
        ])

        const patientsWithVitals = await Promise.all(
          patientsList.map(async (p) => {
            const latest = await fetchPatientLatestVital(p.id)
            return { ...p, latest }
          })
        )

        setVitalsData(vitals)
        setPatients(patientsWithVitals)
        setAlerts(alertsList)
      }catch(err){
        console.error('Failed to load nurse data', err)
      }finally{ setLoading(false) }
    }

    load()
  }, [])

  const handleEscalate = async (id) => {
    try{
      const res = await escalateAlert(id, 1) // demo nurse id
      const updated = res.alert || res

      setAlerts((prev) =>
        prev.map(a => a.id === id ? { ...a, ...updated } : a)
      )
    }catch(err){
      console.error('Failed to escalate', err)
    }
  }

  return (
    <Layout role="Nurse">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <div className="bg-white p-4 rounded shadow mb-4">
            <h2 className="text-lg font-semibold mb-2">Live Vitals</h2>
            <VitalsChart data={vitalsData} />
            <ParameterCharts data={vitalsData} />
          </div>

          <div className="bg-white p-4 rounded shadow">
            <h2 className="text-lg font-semibold mb-2">Patients</h2>
            <PatientVitalsList
              patients={patients}
              onUpdated={async () => {
                try{
                  const patientsList = await fetchPatients()
                  const patientsWithVitals = await Promise.all(
                    patientsList.map(async (p) => {
                      const latest = await fetchPatientLatestVital(p.id)
                      return { ...p, latest }
                    })
                  )
                  setPatients(patientsWithVitals)
                }catch(e){
                  console.error('Failed to reload patients', e)
                }
              }}
            />
          </div>
        </div>

        <div>
          <div className="bg-white p-4 rounded shadow">
            <h2 className="text-lg font-semibold mb-2">Alerts</h2>
            {loading
              ? <p className="text-sm text-gray-500">Loading...</p>
              : <AlertList alerts={alerts} showEscalate onEscalate={handleEscalate} />
            }
          </div>
        </div>
      </div>
    </Layout>
  )
}
