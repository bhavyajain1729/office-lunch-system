import { createContext, useContext, useEffect, useState } from "react";
import { loginAdmin, loginEmployee, logout as logoutApi } from "../api/endpoints";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      localStorage.setItem("user", JSON.stringify(user));
    } else {
      localStorage.removeItem("user");
    }
  }, [user]);

  async function loginAsEmployee(email, password) {
    setLoading(true);
    try {
      const { data } = await loginEmployee({ email, password });
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      setUser(data.user);
      return data.user;
    } finally {
      setLoading(false);
    }
  }

  async function loginAsAdmin(email, password) {
    setLoading(true);
    try {
      const { data } = await loginAdmin({ email, password });
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      setUser(data.user);
      return data.user;
    } finally {
      setLoading(false);
    }
  }

  async function doLogout() {
    const refresh = localStorage.getItem("refresh_token");
    try {
      if (refresh) await logoutApi(refresh);
    } catch (e) {
      // ignore — clearing local state regardless
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  }

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.role === "ADMIN",
    isEmployee: user?.role === "EMPLOYEE",
    loginAsEmployee,
    loginAsAdmin,
    logout: doLogout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
