import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getDashboardPath } from "../utils/navigation"; // Centralized navigation logic

export default function ProtectedRoute({ role, children }) {
  const { isAuthenticated, user, loading } = useAuth();

  // If still loading auth state, render nothing or a loading spinner
  if (loading) {
    return null; // Or a loading component
  }

  // If not authenticated, redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // If authenticated but role doesn't match, redirect to their own valid dashboard
  const userRole = user?.role;
  const requiredRoles = Array.isArray(role) ? role : [role];

  if (!requiredRoles.includes(userRole)) {
    const userDashboardPath = getDashboardPath(userRole);
    return <Navigate to={userDashboardPath} replace />;
  }

  // If authenticated and role matches, render children
  return children;
}
