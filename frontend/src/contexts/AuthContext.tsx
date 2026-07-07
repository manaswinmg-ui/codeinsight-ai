import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  full_name?: string | null;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (
    username: string,
    email: string,
    password: string,
    fullName?: string
  ) => Promise<void>;
  logout: () => void;
  /** Returns a valid access token (refreshing if needed), or null if no session */
  getAccessToken: () => Promise<string | null>;
}

export const AuthContext = createContext<AuthContextType | null>(null);

const TOKEN_STORAGE_KEY = 'codeinsight_tokens';

function getStoredTokens(): AuthTokens | null {
  try {
    const raw = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as AuthTokens;
  } catch {
    return null;
  }
}

function storeTokens(tokens: AuthTokens): void {
  localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(tokens));
}

function clearTokens(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

async function apiFetch<T>(url: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /** Try to restore session on mount */
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const tokens = getStoredTokens();
      if (!tokens) {
        setIsLoading(false);
        return;
      }
      try {
        const me = await apiFetch<AuthUser>('/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${tokens.access_token}` },
        });
        if (!cancelled) setUser(me);
      } catch {
        // Access token expired — try refreshing
        try {
          const refreshResult = await apiFetch<{
            access_token: string;
            token_type: string;
          }>('/api/v1/auth/refresh', {
            method: 'POST',
            body: JSON.stringify({ refresh_token: tokens.refresh_token }),
          });
          storeTokens({
            access_token: refreshResult.access_token,
            refresh_token: tokens.refresh_token,
          });
          const me = await apiFetch<AuthUser>('/api/v1/auth/me', {
            headers: {
              Authorization: `Bearer ${refreshResult.access_token}`,
            },
          });
          if (!cancelled) setUser(me);
        } catch {
          clearTokens();
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const result = await apiFetch<{
      access_token: string;
      refresh_token: string;
      token_type: string;
      user: AuthUser;
    }>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    storeTokens({
      access_token: result.access_token,
      refresh_token: result.refresh_token,
    });
    setUser(result.user);
  }, []);

  const register = useCallback(
    async (
      username: string,
      email: string,
      password: string,
      fullName?: string
    ) => {
      const result = await apiFetch<{
        access_token: string;
        refresh_token: string;
        token_type: string;
        user: AuthUser;
      }>('/api/v1/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          username,
          email,
          password,
          full_name: fullName || null,
        }),
      });
      storeTokens({
        access_token: result.access_token,
        refresh_token: result.refresh_token,
      });
      setUser(result.user);
    },
    []
  );

  const logout = useCallback(() => {
    const tokens = getStoredTokens();
    if (tokens) {
      // Best-effort server-side logout (fire-and-forget)
      fetch('/api/v1/auth/logout', {
        method: 'POST',
        headers: { Authorization: `Bearer ${tokens.access_token}` },
      }).catch(() => {});
    }
    clearTokens();
    setUser(null);
  }, []);

  const getAccessToken = useCallback(async (): Promise<string | null> => {
    const tokens = getStoredTokens();
    if (!tokens) return null;

    // Attempt to use current access token — if it fails, try refresh
    try {
      await apiFetch('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${tokens.access_token}` },
      });
      return tokens.access_token;
    } catch {
      try {
        const refreshResult = await apiFetch<{
          access_token: string;
          token_type: string;
        }>('/api/v1/auth/refresh', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: tokens.refresh_token }),
        });
        storeTokens({
          access_token: refreshResult.access_token,
          refresh_token: tokens.refresh_token,
        });
        return refreshResult.access_token;
      } catch {
        clearTokens();
        setUser(null);
        return null;
      }
    }
  }, []);

  const value = useMemo<AuthContextType>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading,
      login,
      register,
      logout,
      getAccessToken,
    }),
    [user, isLoading, login, register, logout, getAccessToken]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
