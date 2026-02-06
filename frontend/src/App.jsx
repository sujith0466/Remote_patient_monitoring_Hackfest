import { Routes, Route, Navigate, useNavigate, useLocation } from "react-router-dom";
import { useEffect } from "react";
import NurseDashboard from "./pages/NurseDashboard";
import DoctorDashboard from "./pages/DoctorDashboard";
import NotFound from "./pages/NotFound";
import Header from "./components/Header";
import SelectRole from "./pages/SelectRole";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import PatientProfile from "./pages/PatientProfile";
import { useAuth } from "./context/AuthContext";
import { getDashboardPath } from "./utils/navigation";

export default function App() {
  const { isAuthenticated, user, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // This useEffect is the single source of truth for post-login navigation.
  // It runs when auth state changes and redirects to the correct dashboard.
  useEffect(() => {
    // Only redirect if authenticated and we are not on a protected path already
    if (isAuthenticated && user?.role) {
      const dashboardPath = getDashboardPath(user.role);
      // Avoid redirect loops if already on the correct path
      if (location.pathname !== dashboardPath && location.pathname === '/login') {
        navigate(dashboardPath, { replace: true });
      }
    }
  }, [isAuthenticated, user, navigate, location.pathname]);


  if (loading) {
    return null; // AuthContext renders its own loading state
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <Header />
      <main className="p-4">
        <Routes>
          {/* Root path now simply redirects to login, auth logic is handled by effects */}
          <Route path="/" element={<Navigate to="/login" replace />} />

          <Route path="/login" element={<Login />} />
          <Route path="/select-role" element={<SelectRole />} />

          <Route path="/doctor" element={
            <ProtectedRoute role="doctor">
              <DoctorDashboard />
            </ProtectedRoute>
          } />

          <Route path="/nurse" element={
            <ProtectedRoute role="nurse">
              <NurseDashboard />
            </ProtectedRoute>
          } />

          <Route path="/patients/:patientId" element={
            <ProtectedRoute role={["nurse", "doctor"]}>
              <PatientProfile />
            </ProtectedRoute>
          } />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </div>
  );
}
