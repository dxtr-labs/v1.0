'use client';

import type { AuthResponse } from '@/types/auth';

export async function submitAuth(formData: FormData): Promise<AuthResponse> {
  try {
    const res = await fetch('/api/auth', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    return data as AuthResponse;
  } catch (error) {
    console.error('Auth error:', error);
    return {
      success: false,
      error: 'An error occurred during authentication'
    };
  }
}
