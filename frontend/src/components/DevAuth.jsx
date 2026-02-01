import { useEffect, useState } from "react";
import { setAuthToken, getAuthToken } from "../api";
import { useNavigate } from "react-router-dom";

export default function DevAuth() {
  const navigate = useNavigate();

  const [token, setToken] = useState(getAuthToken() || "");
  const [userId, setUserId] = useState("");
  const [me, setMe] = useState(null);
  const [status, setStatus] = useState("checking"); // checking | logged_out | logged_in
  const [loading, setLoading] = useState(false);

  // -----------------------------
  // Initial auth check
  // -----------------------------
  useEffect(() => {
    const t = getAuthToken();
    if (t) {
      fetchMe(t);
    } else {
      setStatus("logged_out");
    }
  }, []);

  // -----------------------------
  // Fetch logged-in user
  // -----------------------------
  async function fetchMe(t) {
    setStatus("checking");
    try {
      const res = await fetch("/users/me", {
        headers: { Authorization: `Token ${t}` },
      });

      if (!res.ok) throw new Error();

      const user = await res.json();
      setMe(user);

      // Persist role for routing
      localStorage.setItem("carewatch_role", user.role);

      setStatus("logged_in");
      navigate(`/${user.role}`);
    } catch {
      logout();
    }
  }

  // -----------------------------
  // Dev login by user ID
  // -----------------------------
  async function login() {
    if (!userId) return;

    setLoading(true);
    try {
      const res = await fetch("/users/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: Number(userId) }),
      });

      if (!res.ok) {
        alert("Login failed");
        return;
      }

      const data = await res.json();
      setAuthToken(data.api_token);
      setToken(data.api_token);
      fetchMe(data.api_token);
    } catch {
      alert("Login request failed");
    } finally {
      setLoading(false);
    }
  }

  // -----------------------------
  // Manual token apply (dev)
  // -----------------------------
  function applyToken() {
    if (!token) return logout();
    setAuthToken(token);
    fetchMe(token);
  }

  // -----------------------------
  // Logout
  // -----------------------------
  function logout() {
    setAuthToken(null);
    localStorage.removeItem("carewatch_role");
    setToken("");
    setMe(null);
    setStatus("logged_out");
    navigate("/select-role");
  }

  // -----------------------------
  // UI
  // -----------------------------
  return (
    <div className="flex items-center space-x-3 text-sm">
      

      {status === "checking" && (
        <span className="text-gray-400">Checking session…</span>
      )}

      {status === "logged_out" && (
        <>
          <input
            className="border rounded px-2 py-1"
            placeholder="User ID"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
          />
          <button
            onClick={login}
            disabled={loading}
            className="bg-blue-600 text-white px-3 py-1 rounded"
          >
            Login
          </button>

          <input
            className="border rounded px-2 py-1"
            placeholder="Paste token"
            value={token}
            onChange={(e) => setToken(e.target.value)}
          />
          <button
            onClick={applyToken}
            className="bg-gray-200 px-2 py-1 rounded"
          >
            Set
          </button>
        </>
      )}

      {status === "logged_in" && me && (
        <>
          <span className="text-green-600 font-medium">
            {me.name} ({me.role})
          </span>
          <button
            onClick={logout}
            className="bg-red-500 text-white px-2 py-1 rounded"
          >
            Logout
          </button>
        </>
      )}
    </div>
  );
}
