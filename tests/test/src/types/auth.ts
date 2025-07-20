export interface User {
  user_id: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  middle_name?: string;
  username: string;
  organization: boolean;
  session_token: string;
  session_expires: Date;
  created_at: Date;
  updated_at: Date;
  memory_context?: string;
  service_keys?: Record<string, any>;
  credits: number;
  want_notifications?: boolean;
}

export interface AuthResponse {
  success: boolean;
  error?: string;
  user?: Omit<User, 'password'>;
  session_token?: string;
}

export interface SignupData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  middle_name?: string;
  want_notifications: boolean;
}

export interface LoginData {
  email: string;
  password: string;
}
