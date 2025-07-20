import { handleAuth } from '@/app/actions/auth';
import { type NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const result = await handleAuth(formData);
    
    return Response.json(result);
  } catch (error) {
    console.error('API error:', error);
    return Response.json({
      success: false,
      error: 'An error occurred during authentication'
    });
  }
}
