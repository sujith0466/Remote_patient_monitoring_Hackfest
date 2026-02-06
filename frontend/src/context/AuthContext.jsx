import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import { createApi } from '../api/index.js';
import toast from 'react-hot-toast'; // Import toast

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('accessToken'));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken'));
  const [legacyApiToken, setLegacyApiToken] = useState(localStorage.getItem('legacyApiToken'));
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const api = createApi(accessToken, legacyApiToken);

  const clearTokens = useCallback(() => {
    setAccessToken(null);
    setRefreshToken(null);
    setLegacyApiToken(null);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('legacyApiToken');
    setUser(null);
  }, []);

  const saveTokens = useCallback((access, refresh, legacyToken = null) => {
    setAccessToken(access);
    setRefreshToken(refresh);
    setLegacyApiToken(legacyToken);
    
    if (access) {
      localStorage.setItem('accessToken', access);
      const decodedUser = jwtDecode(access);
      // Normalize role on creation
      const normalizedRole = decodedUser?.role?.toLowerCase();
      setUser(decodedUser ? { ...decodedUser, id: decodedUser.sub, role: normalizedRole } : null);
    } else {
      localStorage.removeItem('accessToken');
      setUser(null);
    }

    if (refresh) {
      localStorage.setItem('refreshToken', refresh);
    } else {
      localStorage.removeItem('refreshToken');
    }

    if (legacyToken) {
      localStorage.setItem('legacyApiToken', legacyToken);
    } else {
      localStorage.removeItem('legacyApiToken');
    }

  }, []);

  useEffect(() => {
    if (accessToken) {
      try {
        const decodedUser = jwtDecode(accessToken);
        // Normalize role on rehydration
        const normalizedRole = decodedUser?.role?.toLowerCase();
        setUser({ ...decodedUser, id: decodedUser.sub, role: normalizedRole });
      } catch (error) {
        console.error("Invalid access token:", error);
        clearTokens();
        toast.error("Session expired or invalid. Please log in again.");
      }
    }
    setLoading(false);
  }, [accessToken, clearTokens]);

  const login = useCallback(async (email, password) => {
    setLoading(true);
    try {
      const data = await api.login(email, password);
      saveTokens(data.access_token, data.refresh_token);
      toast.success("Logged in successfully!");
      return { success: true }; // Navigation is handled by App.jsx
    } catch (error) {
      console.error("Login request failed:", error.message);
      toast.error(error.message || 'Login failed');
      clearTokens();
      return { success: false, error: error.message || 'Login failed' };
    } finally {
      setLoading(false);
    }
  }, [api, saveTokens, clearTokens]); // Removed navigate from dependencies

  const logout = useCallback(() => {
    clearTokens();
    toast('You have been logged out.', { icon: '👋' });
    navigate('/login');
  }, [clearTokens, navigate]);

  const handleRefresh = useCallback(async () => {
    try {
      const data = await api.refreshToken(refreshToken);
      saveTokens(data.access_token, refreshToken);
      toast.success("Session refreshed!");
    } catch (error) {
      console.error("Failed to refresh token:", error);
      toast.error("Failed to refresh session. Please log in again.");
      logout();
    }
  }, [api, refreshToken, saveTokens, logout]);

  useEffect(() => {
    let interval;
    if (accessToken && refreshToken) {
      const decodedAccess = jwtDecode(accessToken);
      const expiresIn = decodedAccess.exp * 1000 - Date.now();

      const refreshThreshold = 5 * 60 * 1000;
      if (expiresIn < refreshThreshold && expiresIn > 0) {
        handleRefresh();
      }

      interval = setInterval(() => {
        const currentExpiresIn = jwtDecode(accessToken).exp * 1000 - Date.now();
        if (currentExpiresIn < refreshThreshold && currentExpiresIn > 0) {
          handleRefresh();
        } else if (currentExpiresIn <= 0) {
          toast.error("Session expired. Please log in again.");
          logout();
        }
      }, 30 * 1000);
    }
    return () => clearInterval(interval);
  }, [accessToken, refreshToken, logout, handleRefresh]);

  const authContextValue = {
    user,
    isAuthenticated: !!user,
    accessToken,
    refreshToken,
    legacyApiToken,
    loading,
    login,
    logout,
    saveTokens,
    clearTokens,
    api,
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <span className="text-xl text-gray-600">Loading authentication...</span>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={authContextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};


