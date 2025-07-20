import { 
  Credential, 
  CredentialsResponse, 
  CredentialResponse, 
  ErrorResponse, 
  TestConnectionResponse, 
  EnvironmentResponse 
} from '../types/credentials';

export class CredentialsService {
  private static instance: CredentialsService;
  private cache: Map<string, Credential[]> = new Map();

  static getInstance(): CredentialsService {
    if (!CredentialsService.instance) {
      CredentialsService.instance = new CredentialsService();
    }
    return CredentialsService.instance;
  }

  async getCredentials(): Promise<Credential[]> {
    try {
      const cacheKey = 'user_credentials';
      
      // Check cache first
      if (this.cache.has(cacheKey)) {
        return this.cache.get(cacheKey)!;
      }

      const response = await fetch('/api/credentials', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication required');
        }
        throw new Error(`Failed to fetch credentials: ${response.statusText}`);
      }

      const data = await response.json() as CredentialsResponse;
      this.cache.set(cacheKey, data.credentials);
      return data.credentials;
    } catch (error) {
      console.error('Error fetching credentials:', error);
      throw error;
    }
  }

  async createCredential(credential: Omit<Credential, 'id' | 'status' | 'lastUsed'>): Promise<Credential> {
    try {
      const response = await fetch('/api/credentials', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credential),
      });

      if (!response.ok) {
        const errorData = await response.json() as ErrorResponse;
        throw new Error(errorData.error || 'Failed to create credential');
      }

      const data = await response.json() as CredentialResponse;
      
      // Invalidate cache
      this.cache.delete('user_credentials');
      
      return data.credential;
    } catch (error) {
      console.error('Error creating credential:', error);
      throw error;
    }
  }

  async updateCredential(id: string, credential: Omit<Credential, 'id' | 'status' | 'lastUsed'>): Promise<Credential> {
    try {
      const response = await fetch('/api/credentials', {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id, ...credential }),
      });

      if (!response.ok) {
        const errorData = await response.json() as ErrorResponse;
        throw new Error(errorData.error || 'Failed to update credential');
      }

      const data = await response.json() as CredentialResponse;
      
      // Invalidate cache
      this.cache.delete('user_credentials');
      
      return data.credential;
    } catch (error) {
      console.error('Error updating credential:', error);
      throw error;
    }
  }

  async deleteCredential(id: string): Promise<void> {
    try {
      const response = await fetch(`/api/credentials?id=${id}`, {
        method: 'DELETE',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json() as ErrorResponse;
        throw new Error(errorData.error || 'Failed to delete credential');
      }

      // Invalidate cache
      this.cache.delete('user_credentials');
    } catch (error) {
      console.error('Error deleting credential:', error);
      throw error;
    }
  }

  async testConnection(service: string, fields: { [key: string]: string }): Promise<boolean> {
    try {
      const response = await fetch('/api/credentials/test', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ service, fields }),
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json() as TestConnectionResponse;
      return data.success;
    } catch (error) {
      console.error('Error testing connection:', error);
      return false;
    }
  }

  // Environment variable integration for production
  async getEnvironmentCredentials(): Promise<{ [key: string]: string }> {
    try {
      const response = await fetch('/api/credentials/environment', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        return {};
      }

      const data = await response.json() as EnvironmentResponse;
      return data.environment;
    } catch (error) {
      console.error('Error fetching environment credentials:', error);
      return {};
    }
  }

  clearCache(): void {
    this.cache.clear();
  }
}
