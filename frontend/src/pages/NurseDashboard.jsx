import React, { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import VitalsChart from '../components/VitalsChart'
import ParameterCharts from '../components/ParameterCharts'
import AlertList from '../components/AlertList'
import PatientVitalsList from '../components/PatientVitalsList'
import { useAuth } from '../context/AuthContext' // Import useAuth
import { Link } from 'react-router-dom';


export default function NurseDashboard(){
  const { api } = useAuth(); // Access the API client from AuthContext
  const [vitalsData, setVitalsData] = useState({ timestamps: [], heartRate: [], temperature: [], spo2: [] })
  const [patients, setPatients] = useState([])
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadNurseData = async () => {
    setLoading(true)
    setError(null)
    try{
      const [vitals, patientsList, alertsList] = await Promise.all([
        api.fetchVitals(30),
        api.fetchPatients(),
        api.fetchAlerts({ role: 'nurse' }) // ✅ explicit nurse role
      ])

      const patientsWithVitalsAndRisk = await Promise.all(
        patientsList.map(async (p) => {
          const latest = await api.fetchPatientLatestVital(p.id)
          const risk = await api.getPatientRiskScore(p.id);
          return { ...p, latest, riskScore: risk.risk_score }
        })
      )

      setVitalsData(vitals)
      setPatients(patientsWithVitalsAndRisk)
      setAlerts(alertsList)
    }catch(err){
      console.error('Failed to load nurse data', err)
      setError('Unable to load nurse data. Please check the backend and your network connection.')
    }finally{ setLoading(false) }
  }

  useEffect(() => {
    loadNurseData();
  }, [api]) // Add api to dependency array


  const handleEscalate = async (id) => {
    try{
      const res = await api.escalateAlert(id) // use api.escalateAlert
      const updated = res.alert || res

      setAlerts((prev) =>
        prev.map(a => a.id === id ? { ...a, ...updated } : a)
      )
    }catch(err){
      console.error('Failed to escalate', err)
      setError('Failed to escalate alert. Make sure you are logged in as a nurse or that demo nurse user exists.')
    }
  }

  return (
    <Layout role="Nurse">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <div className="bg-white p-4 rounded shadow mb-4 dark:bg-gray-800 dark:text-gray-200">
            <h2 className="text-lg font-semibold mb-2">Live Vitals Overview</h2>
            <VitalsChart data={vitalsData} />
            <ParameterCharts data={vitalsData} />
          </div>

          <div className="bg-white p-4 rounded shadow dark:bg-gray-800 dark:text-gray-200">
            <h2 className="text-lg font-semibold mb-2">Patients Overview</h2>
            {loading && <p>Loading patients...</p>}
            {error && <p className="text-red-600">{error}</p>}
            {!loading && !error && (
              <ul className="space-y-3">
                {patients.map((p) => (
                  <li key={p.id} className="border p-3 rounded flex justify-between items-center dark:border-gray-700">
                    <div>
                      <Link to={`/patients/${p.id}`} className="text-blue-600 hover:underline font-semibold dark:text-blue-400">
                        {p.name}
                      </Link>
                      <div className="text-xs text-gray-600 dark:text-gray-400">
                        Room: {p.room} • Age: {p.age} • Sex: {p.sex}
                      </div>
                      <div className="text-sm mt-1">
                        HR: {p.latest?.heart_rate ?? '—'} bpm • Temp: {p.latest?.temperature ?? '—'}°C • SpO₂: {p.latest?.spo2 ?? '—'}%
                      </div>
                    </div>
                    <div>
                      <span className={`text-sm font-medium ${p.riskScore > 5 ? 'text-red-700' : 'text-green-700'}`}>
                        Risk: {p.riskScore}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
            {/* The full PatientVitalsList component might be too detailed for an overview,
                but keeping it here for now if needed. It also has edit functionality. */}
            {/* <PatientVitalsList
              patients={patients}
              onUpdated={loadNurseData}
            /> */}
          </div>
        </div>

        <div>
          <div className="bg-white p-4 rounded shadow dark:bg-gray-800 dark:text-gray-200">
            <h2 className="text-lg font-semibold mb-2">Active Alerts</h2>
            {loading && <p className="text-sm text-gray-500">Loading...</p>}
            {error && !loading && (
              <p className="text-sm text-red-600 mb-2">{error}</p>
            )}
            {!loading && !error && (
              <AlertList alerts={alerts} showEscalate onEscalate={handleEscalate} />
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}
