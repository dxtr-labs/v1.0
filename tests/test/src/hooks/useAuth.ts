import { useState } from 'react';
import { useRouter } from 'next/navigation';

export interface User {
  id: number;
  email: string;
  name: string;
  username: string;
  credits: number;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  user?: User;
  userId?: number;
  email?: string;
  name?: string;
  error?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface SignupData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  isOrganization?: boolean;
}

export const useAuth = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const login = (data: LoginData): Promise<AuthResponse> => {
    setIsLoading(true);
    setError(null);
    
    return fetch('/api/auth/login', {
      method: 'POST',
      credentials: 'include', // 👈 sends the HttpOnly cookie
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    .then(response => response.json().then(result => ({ response, result: result as AuthResponse })))
    .then(({ response, result }) => {
      if (!response.ok) {
        throw new Error(result.error || 'Login failed');
      }

      if (result.success) {
        // No need to store user data in localStorage - cookies will handle auth
        // Use window.location instead of router.push to avoid promise issues
        if (typeof window !== 'undefined') {
          window.location.href = '/dashboard';
        }
      }

      return result;
    })
    .catch(err => {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
        error: errorMessage
      } as AuthResponse;
    })
    .finally(() => {
      setIsLoading(false);
    });
  };

  const signup = (data: SignupData): Promise<AuthResponse> => {
    setIsLoading(true);
    setError(null);
    
    return fetch('/api/auth/signup', {
      method: 'POST',
      credentials: 'include', // 👈 sends the HttpOnly cookie
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    .then(response => response.json().then(result => ({ response, result: result as AuthResponse })))
    .then(({ response, result }) => {
      if (!response.ok) {
        throw new Error(result.error || 'Signup failed');
      }

      if (result.success) {
        // No need to store user data in localStorage - cookies will handle auth
        // Use window.location instead of router.push to avoid promise issues
        if (typeof window !== 'undefined') {
          window.location.href = '/dashboard';
        }
      }

      return result;
    })
    .catch(err => {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
        error: errorMessage
      } as AuthResponse;
    })
    .finally(() => {
      setIsLoading(false);
    });
  };

  const logout = () => {
    setIsLoading(true);
    
    // Call logout API to clear session cookies
    fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include', // 👈 sends the HttpOnly cookie
    })
    .then(() => {
      // Redirect to login using window.location for consistency
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    })
    .catch(err => {
      console.error('Logout error:', err);
      // Still redirect on error
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    })
    .finally(() => {
      setIsLoading(false);
    });
  };

  const getCurrentUser = (): Promise<User | null> => {
    return fetch('/api/auth/me', {
      credentials: 'include', // 👈 sends the HttpOnly cookie
    })
    .then(response => {
      if (!response.ok) {
        return null;
      }
      return response.json();
    })
    .then((data: any) => {
      return data?.user || null;
    })
    .catch(() => {
      return null;
    });
  };

  return {
    login,
    signup,
    logout,
    getCurrentUser,
    isLoading,
    error,
    clearError: () => setError(null)
  };
};
