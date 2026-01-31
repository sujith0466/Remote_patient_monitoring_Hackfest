import React, { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import AlertList from '../components/AlertList'
import PatientSummary from '../components/PatientSummary'
import { fetchEscalatedAlerts, fetchPatients, fetchVitals } from '../api'

export default function DoctorDashboard(){
  const [alerts, setAlerts] = useState([])
  const [patients, setPatients] = useState([])
  const [trends, setTrends] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load(){
      setLoading(true)
      try{
        const [alertsRes, patientsRes, vitalsRes] = await Promise.all([
          fetchEscalatedAlerts(),
          fetchPatients(),
          fetchVitals(200)
        ])

        setAlerts(alertsRes)
        setPatients(patientsRes)

        // build simple trends per patient using the vitals list (we received as an aggregated series; fetch raw vitals endpoint if more detail needed)
        // Approach: fetch /vitals returned series merged across patients; for simplicity, build empty or reuse aggregated series
        // TODO: refine with patient-specific vitals endpoint
        setTrends({})
      }catch(err){
        console.error('Failed to load doctor data', err)
      }finally{ setLoading(false) }
    }

    load()
  }, [])

  return (
    <Layout role="Doctor">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-white p-4 rounded shadow">
          <h2 className="text-lg font-semibold mb-2">Escalated Alerts</h2>
          <p className="text-sm text-gray-600 mb-3">Doctors see only escalated critical alerts and a summarized trend.</p>
          {loading ? <p className="text-sm text-gray-500">Loading...</p> : <AlertList alerts={alerts} />}
        </div>

        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-lg font-semibold mb-2">Patient Summary</h2>
          <PatientSummary patients={patients} trends={trends} />
        </div>
      </div>
    </Layout>
  )
}
