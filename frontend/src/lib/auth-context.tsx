/**
 * Authentication Context
 * Wraps the entire application and provides:
 *  - user       : the currently logged-in user (or null)
 *  - token      : the JWT stored in localStorage
 *  - login(idToken) : exchanges a Google ID token for our JWT, saves to state + localStorage
 *  - logout()   : clears state and localStorage
 *  - isLoading  : true while checking for an existing session on first load
 */

"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import api from "@/lib/api";
import { User, AuthContextType } from "@/types";

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // On mount: restore session from localStorage
  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedUser = localStorage.getItem("user");
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false);
  }, []);

  /**
   * login(idToken)
   * Called after the user completes Google Sign-In in the browser.
   * Sends the Google ID token to our Flask backend for verification,
   * then stores the returned JWT and user profile.
   */
  const login = useCallback(async (idToken: string) => {
    const res = await api.post("/api/auth/google", { id_token: idToken });
    const { token: jwt, user: userData } = res.data;

    localStorage.setItem("token", jwt);
    localStorage.setItem("user", JSON.stringify(userData));
    setToken(jwt);
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
