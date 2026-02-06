import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';
import VitalsChart from '../components/VitalsChart';
import ParameterCharts from '../components/ParameterCharts';
import AlertList from '../components/AlertList';
import PatientVitalsList from '../components/PatientVitalsList'; // Reusing for displaying current vitals
import { jwtDecode } from 'jwt-decode';

// Skeleton component for placeholders
const Skeleton = ({ width, height, className = '' }) => (
  <div className={`bg-gray-200 animate-pulse rounded ${className} dark:bg-gray-700`} style={{ width, height }}></div>
);


export default function PatientProfile() {
  const { patientId } = useParams();
  const navigate = useNavigate();
  const { api, user, isAuthenticated } = useAuth();
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [noteContent, setNoteContent] = useState('');

  const loadPatientData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const patientData = await api.getPatient(patientId);
      const riskData = await api.getPatientRiskScore(patientId);
      const hrTrends = await api.getPatientVitalTrends(patientId, 'heart_rate', 24, 60);
      const tempTrends = await api.getPatientVitalTrends(patientId, 'temperature', 24, 60);
      const spo2Trends = await api.getPatientVitalTrends(patientId, 'spo2', 24, 60);

      setPatient({
        ...patientData,
        riskScore: riskData.risk_score,
        trends: {
          heart_rate: hrTrends.trends,
          temperature: tempTrends.trends,
          spo2: spo2Trends.trends,
        },
      });
    } catch (err) {
      console.error('Failed to load patient data', err);
      setError('Unable to load patient data. Please check the backend and your network connection.');
    } finally {
      setLoading(false);
    }
  }, [api, patientId]);

  useEffect(() => {
    if (isAuthenticated) {
      loadPatientData();
    } else {
      navigate('/login');
    }
  }, [isAuthenticated, navigate, loadPatientData]);

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!noteContent.trim()) return;

    try {
      await api.addPatientNote(patientId, noteContent);
      setNoteContent('');
      loadPatientData(); // Reload data to show new note
    } catch (err) {
      console.error('Failed to add note', err);
      setError('Failed to add note.');
    }
  };

  const handleDeleteNote = async (noteId) => {
    try {
      await api.deletePatientNote(patientId, noteId);
      loadPatientData(); // Reload data to show note removed
    } catch (err) {
      console.error('Failed to delete note', err);
      setError('Failed to delete note.');
    }
  };

  const handleAlertAction = async (alertId, action) => {
    try {
      let res;
      if (action === 'review') {
        res = await api.reviewAlert(alertId);
      } else if (action === 'close') {
        res = await api.closeAlert(alertId);
      }
      loadPatientData(); // Reload data to show updated alert status
    } catch (err) {
      console.error(`Failed to ${action} alert`, err);
      setError(`Failed to ${action} alert.`);
    }
  };


  if (loading) {
    return (
      <Layout role={user?.role}>
        <div className="bg-white p-6 rounded-lg shadow-md mb-6 dark:bg-gray-800">
          <Skeleton width="60%" height="2rem" className="mb-4" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Skeleton width="80%" height="1.25rem" className="mb-2" />
              <Skeleton width="70%" height="1.25rem" className="mb-2" />
              <Skeleton width="85%" height="1.25rem" className="mb-2" />
            </div>
            <div>
              <Skeleton width="90%" height="1.25rem" className="mb-2" />
              <Skeleton width="50%" height="1.25rem" className="mb-2" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-md dark:bg-gray-800">
              <Skeleton width="70%" height="1.5rem" className="mb-4" />
              <Skeleton width="100%" height="200px" className="mb-4" />
              <Skeleton width="100%" height="80px" />
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md dark:bg-gray-800">
              <Skeleton width="60%" height="1.5rem" className="mb-4" />
              <Skeleton width="100%" height="100px" />
            </div>
          </div>
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-md dark:bg-gray-800">
              <Skeleton width="50%" height="1.5rem" className="mb-4" />
              <Skeleton width="100%" height="120px" className="mb-4" />
              <Skeleton width="100%" height="40px" className="mb-4" />
              <Skeleton width="100%" height="120px" />
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout role={user?.role}>
        <p className="text-red-600">{error}</p>
      </Layout>
    );
  }

  if (!patient) {
    return (
      <Layout role={user?.role}>
        <p>Patient not found.</p>
      </Layout>
    );
  }

  // Prepare data for VitalsChart and ParameterCharts
  const vitalsChartData = {
    timestamps: patient.trends.heart_rate.map(t => new Date(t.timestamp).toLocaleTimeString()),
    heartRate: patient.trends.heart_rate.map(t => t.value),
    temperature: patient.trends.temperature.map(t => t.value),
    spo2: patient.trends.spo2.map(t => t.value),
  };

  return (
    <Layout role={user?.role}>
      <div className="bg-white p-6 rounded-lg shadow-md mb-6 dark:bg-gray-800 dark:text-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 mb-2 dark:text-white">{patient.name}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-700 dark:text-gray-300">
          <div>
            <p><strong>Age:</strong> {patient.age} years</p>
            <p><strong>Sex:</strong> {patient.sex}</p>
            <p><strong>Room:</strong> {patient.room}</p>
            <p><strong>Weight:</strong> {patient.weight_kg} kg</p>
          </div>
          <div>
            <p><strong>Notes:</strong> {patient.notes || 'N/A'}</p>
            <p><strong>Risk Score:</strong> <span className="font-semibold text-lg">{patient.riskScore}</span></p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Vitals and Trends */}
          <div className="bg-white p-6 rounded-lg shadow-md dark:bg-gray-800 dark:text-gray-200">
            <h3 className="text-xl font-semibold text-gray-800 mb-4 dark:text-white">Recent Vitals & Trends</h3>
            <div className="mb-4">
              <VitalsChart data={vitalsChartData} />
              <ParameterCharts data={vitalsChartData} />
            </div>
            {patient.vitals && patient.vitals.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-gray-700 mb-2 dark:text-gray-300">Latest Readings:</h4>
                <ul className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {patient.vitals.slice(0,3).map((vital, index) => (
                    <li key={index} className="text-sm">
                      HR: {vital.heart_rate} bpm, Temp: {vital.temperature}°C, SpO₂: {vital.spo2}%
                      <span className="ml-2 text-gray-500 dark:text-gray-400">({new Date(vital.timestamp).toLocaleTimeString()})</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Alerts */}
          <div className="bg-white p-6 rounded-lg shadow-md dark:bg-gray-800 dark:text-gray-200">
            <h3 className="text-xl font-semibold text-gray-800 mb-4 dark:text-white">Active Alerts</h3>
            {patient.alerts && patient.alerts.length > 0 ? (
              <AlertList alerts={patient.alerts} showEscalate={false} onReview={(id) => handleAlertAction(id, 'review')} onClose={(id) => handleAlertAction(id, 'close')} />
            ) : (
              <p className="text-gray-600 dark:text-gray-400">No active alerts for this patient.</p>
            )}
          </div>
        </div>

        {/* Notes Section */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-md dark:bg-gray-800 dark:text-gray-200">
            <h3 className="text-xl font-semibold text-gray-800 mb-4 dark:text-white">Notes</h3>
            <form onSubmit={handleAddNote} className="mb-4">
              <textarea
                className="w-full p-2 border rounded-md focus:ring focus:ring-blue-200 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-200"
                rows="4"
                placeholder="Add a new note..."
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
              ></textarea>
              <button
                type="submit"
                className="mt-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
              >
                Add Note
              </button>
            </form>
            {patient.notes && patient.notes.length > 0 ? (
              <ul className="space-y-3">
                {patient.notes.map((note) => (
                  <li key={note.id} className="border p-3 rounded-md bg-gray-50 dark:bg-gray-700 dark:border-gray-600">
                    <div className="flex justify-between items-center text-sm mb-1">
                      <span className="font-semibold">{note.user_name}</span>
                      <span className="text-gray-500 dark:text-gray-400">{new Date(note.timestamp).toLocaleString()}</span>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300">{note.content}</p>
                    {user?.id === note.user_id && (
                        <button
                          onClick={() => handleDeleteNote(note.id)}
                          className="mt-2 text-red-500 hover:text-red-700 text-sm"
                        >
                          Delete
                        </button>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-600 dark:text-gray-400">No notes for this patient yet.</p>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}