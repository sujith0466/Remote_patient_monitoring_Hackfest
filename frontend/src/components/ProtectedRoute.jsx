import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ role, children }) {
  const storedRole = localStorage.getItem("carewatch_role");

  // No role selected → go to role selection
  if (!storedRole) {
    return <Navigate to="/select-role" replace />;
  }

  // Wrong role trying to access page
  if (storedRole !== role) {
    return <Navigate to={`/${storedRole}`} replace />;
  }

  // ✅ Authorized → render page
  return children;
}
