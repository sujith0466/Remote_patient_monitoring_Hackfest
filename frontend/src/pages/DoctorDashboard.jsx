import React, { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import AlertList from '../components/AlertList'
import PatientSummary from '../components/PatientSummary'
import { useAuth } from '../context/AuthContext' // Import useAuth
import { Link } from 'react-router-dom';


export default function DoctorDashboard(){
  const { api } = useAuth(); // Access the API client from AuthContext
  const [alerts, setAlerts] = useState([])
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadDoctorData = async () => {
    setLoading(true)
    setError(null)
    try{
      const [alertsRes, patientsRes] = await Promise.all([
        api.fetchEscalatedAlerts(),
        api.fetchPatients(),
      ]);

      const patientsWithRisk = await Promise.all(
        patientsRes.map(async (p) => {
          const risk = await api.getPatientRiskScore(p.id);
          return { ...p, riskScore: risk.risk_score }
        })
      )

      setAlerts(alertsRes)
      setPatients(patientsWithRisk)

      // TODO: refine with patient-specific vitals endpoint - Trends will be handled in PatientProfile
    }catch(err){
      console.error('Failed to load doctor data', err)
      setError(
        'Unable to load escalated alerts. Make sure you are logged in as a doctor using the control in the top right.'
      )
    }finally{ setLoading(false) }
  }

  useEffect(() => {
    loadDoctorData()

    // listen for patient updates triggered by nurse edits
    const handler = async () => {
      try{
        const patientsRes = await api.fetchPatients()
        setPatients(patientsRes) // Re-fetch all patients, will re-calc risk
      }catch(e){ console.error('Failed to refresh patients', e) }
    }
    window.addEventListener('patients:updated', handler)
    return () => window.removeEventListener('patients:updated', handler)
  }, [api]) // Add api to dependency array

  const handleAlertAction = async (alertId, action) => {
    try {
      if (action === 'review') {
        await api.reviewAlert(alertId);
      } else if (action === 'close') {
        await api.closeAlert(alertId);
      }
      loadDoctorData(); // Reload data to show updated alert status
    } catch (err) {
      console.error(`Failed to ${action} alert`, err);
      setError(`Failed to ${action} alert.`);
    }
  };


  return (
    <Layout role="Doctor">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-white p-4 rounded shadow dark:bg-gray-800 dark:text-gray-200">
          <h2 className="text-lg font-semibold mb-2">Escalated Alerts</h2>
          <p className="text-sm text-gray-600 mb-3 dark:text-gray-400">
            Doctors see only escalated critical alerts. Use this view to prioritise the sickest patients first.
          </p>
          {loading && <p className="text-sm text-gray-500">Loading...</p>}
          {error && !loading && (
            <p className="text-sm text-red-600 mb-2">{error}</p>
          )}
          {!loading && !error && <AlertList alerts={alerts} onReview={(id) => handleAlertAction(id, 'review')} onClose={(id) => handleAlertAction(id, 'close')} />}
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
        </div>
      </div>
    </Layout>
  )
}
