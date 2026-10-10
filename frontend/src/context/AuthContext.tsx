import React, { createContext, useContext, useState, useEffect } from "react";
import type { User, UserRole } from "../types";
import { apiClient } from "../api/client";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  unreadCount: number;
  login: (data: any) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  switchDemoUser: (role: UserRole) => Promise<void>;
  refreshUnreadCount: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem("auth_user");
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("auth_token"));
  const [isLoading, setIsLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  const refreshUnreadCount = async () => {
    if (!token) return;
    try {
      const res = await apiClient.getUnreadCount();
      setUnreadCount(res.data.unread_count);
    } catch {
      // Ignore if not logged in
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem("auth_token");
      if (storedToken) {
        try {
          const res = await apiClient.getMe();
          setUser(res.data);
          localStorage.setItem("auth_user", JSON.stringify(res.data));
          const countRes = await apiClient.getUnreadCount();
          setUnreadCount(countRes.data.unread_count);
        } catch {
          localStorage.removeItem("auth_token");
          localStorage.removeItem("auth_user");
          setUser(null);
          setToken(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials: any) => {
    const res = await apiClient.login(credentials);
    const { access_token, user: userData } = res.data;
    localStorage.setItem("auth_token", access_token);
    localStorage.setItem("auth_user", JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    await refreshUnreadCount();
  };

  const register = async (regData: any) => {
    const res = await apiClient.register(regData);
    const { access_token, user: userData } = res.data;
    localStorage.setItem("auth_token", access_token);
    localStorage.setItem("auth_user", JSON.stringify(userData));
    setToken(access_token);
    setUser(userData);
    await refreshUnreadCount();
  };

  const logout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_user");
    setToken(null);
    setUser(null);
    window.location.href = "/login";
  };

  const switchDemoUser = async (role: UserRole) => {
    setIsLoading(true);
    try {
      const res = await apiClient.switchDemo(role);
      const { access_token, user: userData } = res.data;
      localStorage.setItem("auth_token", access_token);
      localStorage.setItem("auth_user", JSON.stringify(userData));
      setToken(access_token);
      setUser(userData);
      
      const countRes = await apiClient.getUnreadCount();
      setUnreadCount(countRes.data.unread_count);

      // Navigate to corresponding dashboard
      if (role === "student") {
        window.location.href = "/student/dashboard";
      } else if (role === "faculty") {
        window.location.href = "/faculty/dashboard";
      } else {
        window.location.href = "/admin/dashboard";
      }
    } catch (e) {
      console.error("Demo user switch error", e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        unreadCount,
        login,
        register,
        logout,
        switchDemoUser,
        refreshUnreadCount,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
