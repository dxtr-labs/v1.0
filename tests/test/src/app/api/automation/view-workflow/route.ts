import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ error: 'This route is deprecated' }, { status: 404 });
}
