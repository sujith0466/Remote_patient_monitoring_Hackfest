import  { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'

export default function AlertList({ alerts = [], showEscalate = false, onEscalate, onReview, onClose }){
  const { user } = useAuth();
  const [escalatedIds, setEscalatedIds] = useState(() => alerts.filter(a => a.escalated).map(a => a.id));

  useEffect(() => {
    setEscalatedIds(alerts.filter(a => a.escalated).map(a => a.id));
  }, [alerts]);

  if(!alerts.length) return <p className="text-sm text-gray-500">No alerts</p>
  return (
    <ul className="space-y-3">
      {alerts.map((a) => {
        const isCritical = a.alertLevel === 'critical' || a.severity === 'critical';
        const isWarning = a.alertLevel === 'warning' || a.severity === 'warning';
        const isEscalated = escalatedIds.includes(a.id) || a.escalated;
        const isReviewed = a.reviewed;
        const isClosed = a.closed;

        return (
          <li key={a.id} className="border p-3 rounded flex flex-col sm:flex-row justify-between items-start sm:items-center">
            <div className="mb-2 sm:mb-0">
              <div className="flex items-center space-x-2">
                <div className="text-sm font-semibold">{a.title || a.message}</div>
                {isCritical && <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">Critical</span>}
                {isWarning && <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded">Warning</span>}
                {isEscalated && <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">Escalated</span>}
                {isReviewed && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Reviewed</span>}
                {isClosed && <span className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">Closed</span>}
              </div>
              <div className="text-xs text-gray-600">
                {a.time || new Date(a.created_at).toLocaleString()} — Patient: {a.patientId || a.patient_id}
              </div>
              <div className="text-sm mt-1">{a.details || a.message}</div>
            </div>
            <div className="flex space-x-2 mt-2 sm:mt-0">
              {!isClosed && user && (user.role === 'doctor' || user.role === 'nurse') && (
                <>
                  {!isReviewed && (
                    <button
                      onClick={() => onReview && onReview(a.id)}
                      className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm"
                    >
                      Review
                    </button>
                  )}
                  {isReviewed && (user.role === 'doctor' || user.role === 'nurse') && (
                    <button
                      onClick={() => onClose && onClose(a.id)}
                      className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm"
                    >
                      Close
                    </button>
                  )}
                </>
              )}
              {!isEscalated && showEscalate && isCritical && user && user.role === 'nurse' && (
                <button
                  onClick={() => {
                    setEscalatedIds((s) => [...s, a.id]);
                    onEscalate && onEscalate(a.id);
                  }}
                  className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded text-sm"
                >
                  Escalate
                </button>
              )}
            </div>
          </li>
        );
      })}
    </ul>
  );
}
