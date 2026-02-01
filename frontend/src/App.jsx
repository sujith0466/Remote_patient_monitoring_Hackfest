import { Routes, Route, Navigate } from "react-router-dom";
import NurseDashboard from "./pages/NurseDashboard";
import DoctorDashboard from "./pages/DoctorDashboard";
import NotFound from "./pages/NotFound";
import Header from "./components/Header";
import SelectRole from "./pages/SelectRole";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  const rawRole = localStorage.getItem("carewatch_role");
  const role = rawRole ? rawRole.toLowerCase().trim() : null;

  const isValidRole = role === "doctor" || role === "nurse";

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main className="p-4">
        <Routes>
          <Route
            path="/"
            element={
              isValidRole
                ? <Navigate to={`/${role}`} replace />
                : <Navigate to="/select-role" replace />
            }
          />

          <Route path="/select-role" element={<SelectRole />} />

          <Route
            path="/doctor"
            element={
              <ProtectedRoute role="doctor">
                <DoctorDashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/nurse"
            element={
              <ProtectedRoute role="nurse">
                <NurseDashboard />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </div>
  );
}
