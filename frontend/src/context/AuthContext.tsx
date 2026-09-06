import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';
import { LoginCredentials, ProfileUpdateData, RegisterData, User } from '../types/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  theme: 'dark' | 'light';
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  updateProfile: (data: ProfileUpdateData) => Promise<User>;
  toggleTheme: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('unifound_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('unifound_token');
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    const savedTheme = localStorage.getItem('unifound_theme');
    return (savedTheme as 'dark' | 'light') || 'dark';
  });

  // Apply theme to document element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('unifound_theme', theme);
  }, [theme]);

  // Load and verify initial user state
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('unifound_token');
      if (storedToken) {
        try {
          const freshUser = await authApi.getMe();
          setUser(freshUser);
          localStorage.setItem('unifound_user', JSON.stringify(freshUser));
        } catch (err) {
          console.warn('Session expired or invalid, logging out', err);
          logout();
        }
      }
      setLoading(false);
    };

    initAuth();

    const handleUnauthorized = () => {
      logout();
    };
    window.addEventListener('unifound:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('unifound:unauthorized', handleUnauthorized);
  }, []);

  const login = async (credentials: LoginCredentials) => {
    const data = await authApi.login(credentials);
    setUser(data.user);
    setToken(data.access_token);
    localStorage.setItem('unifound_token', data.access_token);
    localStorage.setItem('unifound_user', JSON.stringify(data.user));
  };

  const register = async (data: RegisterData) => {
    await authApi.register(data);
    // After registration, auto-login
    await login({ email: data.email, password: data.password });
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('unifound_token');
    localStorage.removeItem('unifound_user');
  };

  const updateProfile = async (data: ProfileUpdateData): Promise<User> => {
    const updated = await authApi.updateProfile(data);
    setUser(updated);
    localStorage.setItem('unifound_user', JSON.stringify(updated));
    return updated;
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: !!user && !!token,
        isAdmin: user?.role === 'ADMIN',
        theme,
        login,
        register,
        logout,
        updateProfile,
        toggleTheme,
      }}
    >
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
