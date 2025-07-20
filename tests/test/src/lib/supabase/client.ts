"use client";

import { createBrowserClient } from '@supabase/ssr';
import { env } from '@/config/env';

const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const createClient = () => {
  if (!isValidUrl(env.NEXT_PUBLIC_SUPABASE_URL)) {
    throw new Error('Invalid Supabase URL. Please check your environment variables.');
  }

  return createBrowserClient(
    env.NEXT_PUBLIC_SUPABASE_URL,
    env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  );
};
