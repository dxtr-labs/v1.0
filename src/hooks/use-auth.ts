"use client";

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';

interface AuthState {
  isLoading: boolean;
  error: string | null;
}

interface AuthResponse {
  success: boolean;
  error?: string;
  data?: any;
}

export const useAuth = () => {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    isLoading: false,
    error: null,
  });

  const handleAuth = useCallback(async (
    endpoint: string,
    data: Record<string, any>
  ): Promise<AuthResponse> => {
    setState({ isLoading: true, error: null });

    try {
      const response = await fetch(`/api/auth/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || `Failed to ${endpoint}`);
      }

      setState({ isLoading: false, error: null });
      return { success: true, data: result };
    } catch (error: any) {
      const errorMessage = error.message || `An error occurred during ${endpoint}`;
      setState({ isLoading: false, error: errorMessage });
      return { success: false, error: errorMessage };
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const result = await handleAuth('login', { email, password });
    if (result.success) {
      router.push('/dashboard');
      router.refresh();
    }
    return result;
  }, [handleAuth, router]);

  const signup = useCallback(async (userData: {
    email: string;
    password: string;
    firstName?: string;
    lastName?: string;
  }) => {
    const result = await handleAuth('signup', userData);
    if (result.success) {
      router.push('/login?message=Account created successfully. Please log in.');
    }
    return result;
  }, [handleAuth, router]);

  const logout = useCallback(async () => {
    const result = await handleAuth('logout', {});
    if (result.success) {
      router.push('/login');
      router.refresh();
    }
    return result;
  }, [handleAuth, router]);

  return {
    ...state,
    login,
    signup,
    logout,
  };
};
