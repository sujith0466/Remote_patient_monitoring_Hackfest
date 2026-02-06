import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext"; // Import useAuth
import toast from 'react-hot-toast'; // Import toast


export default function DevAuth() {
  const navigate = useNavigate();
  const { isAuthenticated, user, accessToken, legacyApiToken, login, logout, saveTokens, api } = useAuth();

  const [userId, setUserId] = useState("");
  const [tokenInput, setTokenInput] = useState(legacyApiToken || ""); // For manual token input
  const [loading, setLoading] = useState(false);

  const currentToken = accessToken || legacyApiToken;
  const isLoggedIn = isAuthenticated || !!legacyApiToken; // Consider legacy token as logged in for DevAuth display

  // If already authenticated via JWT, DevAuth shouldn't interfere, but can display user info
  useEffect(() => {
    if (isAuthenticated && user) {
      navigate(`/${user.role}`);
    } else if (legacyApiToken) {
      // If we only have a legacy token, try to fetch user info to get role for navigation
      const fetchLegacyUser = async () => {
        try {
          const fetchedUser = await api.fetchMe(); // Use api instance with legacy token
          if (fetchedUser && fetchedUser.role) {
            navigate(`/${fetchedUser.role}`);
          } else {
            logout(); // Clear token if user fetch fails
          }
        } catch (error) {
          console.error("Failed to fetch legacy user with token:", error);
          toast.error("Failed to fetch user with legacy token. Logging out.");
          logout();
        }
      };
      fetchLegacyUser();
    }
  }, [isAuthenticated, user, legacyApiToken, navigate, logout, api]);


  // -----------------------------
  // Dev login by user ID (legacy API token)
  // -----------------------------
  const handleLegacyLogin = useCallback(async (id) => {
    const targetUserId = id || userId;
    if (!targetUserId) return;

    setLoading(true);
    try {
      const data = await api.legacyLogin(Number(targetUserId));
      saveTokens(null, null, data.api_token); // Save only legacy API token
      const fetchedUser = await api.fetchMe(); // Fetch user details with the new API token
      if (fetchedUser && fetchedUser.role) {
        toast.success(`Logged in as ${fetchedUser.name} (${fetchedUser.role}) via legacy token.`);
        navigate(`/${fetchedUser.role}`);
      } else {
        toast.error("Failed to retrieve user info after legacy login. Logging out.");
        logout();
      }
    } catch (error) {
      toast.error(`Legacy Login failed: ${error.message}`);
      logout();
    } finally {
      setLoading(false);
    }
  }, [userId, saveTokens, navigate, logout, api]);

  // -----------------------------
  // Manual token apply (dev)
  // -----------------------------
  const applyToken = useCallback(() => {
    if (!tokenInput) return logout();
    // Assuming the manually entered token is a legacy API token for DevAuth context
    saveTokens(null, null, tokenInput);
    // After setting, try to fetch user to validate and navigate
    const fetchUserWithManualToken = async () => {
      try {
        const fetchedUser = await api.fetchMe();
        if (fetchedUser && fetchedUser.role) {
          toast.success(`Applied legacy token for ${fetchedUser.name} (${fetchedUser.role}).`);
          navigate(`/${fetchedUser.role}`);
        } else {
          toast.error("Failed to fetch user with manual token. Logging out.");
          logout();
        }
      } catch (error) {
        console.error("Failed to fetch user with manual token:", error);
        toast.error("Failed to apply manual token. Logging out.");
        logout();
      }
    };
    fetchUserWithManualToken();
  }, [tokenInput, saveTokens, logout, navigate, api]);

  // -----------------------------
  // UI
  // -----------------------------
  return (
    <div className="flex items-center space-x-3 text-sm">
      {loading && (
        <span className="text-gray-400">Loading…</span>
      )}

      {!isLoggedIn && (
        <>
          <div className="flex items-center space-x-2">
            <button
              type="button"
              className="bg-green-600 text-white px-3 py-1 rounded"
              onClick={() => handleLegacyLogin("1")} // Nurse seeded with ID 1
              disabled={loading}
            >
              Nurse demo
            </button>
            <button
              type="button"
              className="bg-blue-600 text-white px-3 py-1 rounded"
              onClick={() => handleLegacyLogin("2")} // Doctor seeded with ID 2
              disabled={loading}
            >
              Doctor demo
            </button>
          </div>

          <input
            className="border rounded px-2 py-1"
            placeholder="User ID"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
          />
          <button
            onClick={() => handleLegacyLogin()}
            disabled={loading}
            className="bg-blue-600 text-white px-3 py-1 rounded"
          >
            Login (Legacy ID)
          </button>

          <input
            className="border rounded px-2 py-1"
            placeholder="Paste API token"
            value={tokenInput}
            onChange={(e) => setTokenInput(e.target.value)}
          />
          <button
            onClick={applyToken}
            className="bg-gray-200 px-2 py-1 rounded"
          >
            Set (Legacy API Token)
          </button>
        </>
      )}

      {isLoggedIn && user && ( // Display user info from AuthContext if authenticated via JWT or legacy token
        <>
          <span className="text-green-600 font-medium">
            {user.name} ({user.role})
          </span>
          <button
            onClick={logout}
            className="bg-red-500 text-white px-2 py-1 rounded"
          >
            Logout
          </button>
        </>
      )}
      {isLoggedIn && !user && legacyApiToken && ( // Fallback display for legacy token if JWT user not fully loaded
        <span className="text-orange-600 font-medium">Legacy Token Active</span>
      )}
    </div>
  );
}
