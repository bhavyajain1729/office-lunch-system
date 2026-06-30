import { createContext, useContext, useEffect, useState, useRef, useCallback } from "react";
import { loginAdmin, loginEmployee, logout as logoutApi, validateSession, getCurrentUser } from "../api/endpoints";

const AuthContext = createContext(null);

/**
 * Enhanced AuthContext with:
 * - JWT token management
 * - Session tracking
 * - Automatic logout on tab close
 * - Session validation
 * - Role-based access control
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });
  
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem("session_id") || null;
  });
  
  const [loading, setLoading] = useState(false);
  const [isSessionValid, setIsSessionValid] = useState(!!user);
  
  const sessionCheckIntervalRef = useRef(null);
  const beforeUnloadRef = useRef(false);

  /**
   * Save tokens and session to localStorage securely
   */
  const saveTokens = useCallback((tokens, sessionIdValue) => {
    localStorage.setItem("access_token", tokens.access);
    localStorage.setItem("refresh_token", tokens.refresh);
    localStorage.setItem("session_id", sessionIdValue);
    setSessionId(sessionIdValue);
  }, []);

  /**
   * Save user profile to localStorage
   */
  const saveUser = useCallback((userData) => {
    localStorage.setItem("user", JSON.stringify(userData));
    setUser(userData);
  }, []);

  /**
   * Clear all auth data
   */
  const clearAuthData = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("session_id");
    localStorage.removeItem("user");
    setUser(null);
    setSessionId(null);
    setIsSessionValid(false);
  }, []);

  /**
   * Logout function with session cleanup
   */
  const doLogout = useCallback(async (reason = "User logout") => {
    const refresh = localStorage.getItem("refresh_token");
    const sessionIdValue = localStorage.getItem("session_id");
    
    try {
      if (refresh) {
        await logoutApi(refresh, sessionIdValue);
      }
    } catch (e) {
      console.error("Logout API error (clearing local state anyway):", e);
    }
    
    clearAuthData();
  }, [clearAuthData]);

  /**
   * Validate session with backend
   * Called periodically to ensure session is still active
   */
  const validateCurrentSession = useCallback(async () => {
    const sessionIdValue = localStorage.getItem("session_id");
    const token = localStorage.getItem("access_token");
    
    if (!sessionIdValue || !token) {
      setIsSessionValid(false);
      return false;
    }
    
    try {
      const response = await validateSession(sessionIdValue);
      setIsSessionValid(true);
      return true;
    } catch (error) {
      console.warn("Session validation failed:", error.message);
      setIsSessionValid(false);
      await doLogout("Session invalid");
      return false;
    }
  }, [doLogout]);

  /**
   * Employee login
   */
  async function loginAsEmployee(email, password) {
    setLoading(true);
    try {
      const response = await loginEmployee({ email, password });
      const data = response.data;
      
      saveTokens(data, data.session_id);
      saveUser(data.user);
      setIsSessionValid(true);
      
      return data.user;
    } finally {
      setLoading(false);
    }
  }

  /**
   * Admin login
   */
  async function loginAsAdmin(email, password) {
    setLoading(true);
    try {
      const response = await loginAdmin({ email, password });
      const data = response.data;
      
      saveTokens(data, data.session_id);
      saveUser(data.user);
      setIsSessionValid(true);
      
      return data.user;
    } finally {
      setLoading(false);
    }
  }

  /**
   * Handle tab/window close - automatic logout
   */
  useEffect(() => {
    const handleBeforeUnload = async (e) => {
      // Prevent multiple calls
      if (beforeUnloadRef.current) return;
      beforeUnloadRef.current = true;
      
      const sessionIdValue = localStorage.getItem("session_id");
      const refresh = localStorage.getItem("refresh_token");
      
      if (sessionIdValue && refresh) {
        try {
          // Send logout request with sendBeacon for reliability
          const logoutData = JSON.stringify({
            refresh: refresh,
            session_id: sessionIdValue
          });
          
          navigator.sendBeacon(
            `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/auth/logout/`,
            logoutData
          );
        } catch (e) {
          // Errors are ok here, user is leaving anyway
        }
      }
      
      clearAuthData();
    };

    if (user) {
      window.addEventListener("beforeunload", handleBeforeUnload);
      
      return () => {
        window.removeEventListener("beforeunload", handleBeforeUnload);
      };
    }
  }, [user, clearAuthData]);

  /**
   * Periodic session validation
   * Checks every 5 minutes if session is still active
   */
  useEffect(() => {
    if (!user) return;
    
    // Clear existing interval
    if (sessionCheckIntervalRef.current) {
      clearInterval(sessionCheckIntervalRef.current);
    }
    
    // Validate session immediately
    validateCurrentSession();
    
    // Then validate periodically (every 5 minutes)
    sessionCheckIntervalRef.current = setInterval(() => {
      validateCurrentSession();
    }, 5 * 60 * 1000);
    
    return () => {
      if (sessionCheckIntervalRef.current) {
        clearInterval(sessionCheckIntervalRef.current);
      }
    };
  }, [user, validateCurrentSession]);

  /**
   * Handle visibility change - logout if user switches tabs for too long
   * Optional: You can implement more aggressive cleanup here
   */
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Tab hidden - could start a timer for extended inactivity
      } else {
        // Tab visible again - validate session
        if (user) {
          validateCurrentSession();
        }
      }
    };
    
    if (user) {
      document.addEventListener("visibilitychange", handleVisibilityChange);
      return () => {
        document.removeEventListener("visibilitychange", handleVisibilityChange);
      };
    }
  }, [user, validateCurrentSession]);

  const value = {
    user,
    sessionId,
    loading,
    isAuthenticated: !!user && isSessionValid,
    isSessionValid,
    isAdmin: user?.role === "ADMIN",
    isEmployee: user?.role === "EMPLOYEE",
    loginAsEmployee,
    loginAsAdmin,
    logout: doLogout,
    validateSession: validateCurrentSession,
    clearAuth: clearAuthData,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
