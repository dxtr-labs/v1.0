export interface Credential {
  id: string;
  name: string;
  service: string;
  status: 'connected' | 'disconnected' | 'error';
  fields: { [key: string]: string };
  lastUsed?: string;
}

export interface ServiceConfig {
  name: string;
  category: string;
  icon: React.ReactNode;
  description: string;
  fields: {
    name: string;
    label: string;
    type: 'text' | 'password' | 'url' | 'email';
    placeholder: string;
    required: boolean;
  }[];
  color: string;
  authType: 'oauth' | 'api_key' | 'manual';
  provider?: string;
  service?: string;
}

export interface CredentialsResponse {
  credentials: Credential[];
}

export interface CredentialResponse {
  success: boolean;
  credential: Credential;
}

export interface ErrorResponse {
  error: string;
}

export interface TestConnectionResponse {
  success: boolean;
}

export interface EnvironmentResponse {
  environment: { [key: string]: string };
}
