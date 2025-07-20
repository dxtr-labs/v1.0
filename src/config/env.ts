const getDevelopmentFallback = (name: string): string => {
  switch (name) {
    case 'NEXT_PUBLIC_SUPABASE_URL':
      return 'https://development.supabase.co';
    case 'NEXT_PUBLIC_SUPABASE_ANON_KEY':
      return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRldmVsb3BtZW50IiwiaWF0IjoxNTE2MjM5MDIyfQ.5D_7IZ_D';
    default:
      return 'development-placeholder';
  }
};

const requireEnvVar = (name: string): string => {
  const value = process.env[name];
  if (!value && process.env.NODE_ENV === 'production') {
    throw new Error(`Missing environment variable: ${name}`);
  }
  return value || getDevelopmentFallback(name);
};

export const env = {
  NEXT_PUBLIC_SUPABASE_URL: requireEnvVar('NEXT_PUBLIC_SUPABASE_URL'),
  NEXT_PUBLIC_SUPABASE_ANON_KEY: requireEnvVar('NEXT_PUBLIC_SUPABASE_ANON_KEY'),
} as const;
