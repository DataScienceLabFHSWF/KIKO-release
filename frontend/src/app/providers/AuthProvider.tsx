// frontend/src/app/providers/AuthProvider.tsx
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { apiRequest } from "../../api/client";
import {
  clearStoredToken,
  getStoredToken,
  storeToken,
} from "../../features/auth/AuthStorage";
import type {
  UserLoginRequest,
  UserLoginResponse,
  UserProfileResponse,
} from "@/api/types/auth";

type AuthContextValue = {
  user: UserProfileResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: UserLoginRequest) => Promise<void>;
  logout: () => void;
  restoreSession: () => Promise<void>;
  updateSessionUser: (profile: UserProfileResponse) => void;
  replaceAccessToken: (token: string) => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const restoreSession = useCallback(async () => {
    const token = getStoredToken();

    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const profile =
        await apiRequest<UserProfileResponse>("/profile/user_info");
      setUser(profile);
    } catch {
      clearStoredToken();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateSessionUser = useCallback((profile: UserProfileResponse) => {
    setUser(profile);
  }, []);

  const login = useCallback(async (payload: UserLoginRequest) => {
    setIsLoading(true);

    try {
      const tokenResponse = await apiRequest<UserLoginResponse>(
        "/authentication/authenticate",
        {
          method: "POST",
          auth: false,
          body: JSON.stringify(payload),
        },
      );

      storeToken(tokenResponse.access_token);

      const profile =
        await apiRequest<UserProfileResponse>("/profile/user_info");

      setUser(profile);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    clearStoredToken();
    setUser(null);
    window.location.replace("/login");
  }, []);

  const replaceAccessToken = useCallback(async (token: string) => {
    storeToken(token);

    const profile = await apiRequest<UserProfileResponse>("/profile/user_info");

    setUser(profile);
  }, []);

  useEffect(() => {
    void restoreSession();
  }, [restoreSession]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      logout,
      restoreSession,
      updateSessionUser,
      replaceAccessToken,
    }),
    [
      user,
      isLoading,
      login,
      logout,
      restoreSession,
      updateSessionUser,
      replaceAccessToken,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}
