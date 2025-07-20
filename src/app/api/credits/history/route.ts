import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // Mock data for now - you can replace this with actual database calls
    const mockCredits = 1250;
    const mockTransactions = [
      {
        type: 'Refill',
        amount: 500,
        description: 'Credit purchase',
        timestamp: new Date().toISOString()
      },
      {
        type: 'Usage',
        amount: -25,
        description: 'API call - GPT-4 request',
        timestamp: new Date(Date.now() - 3600000).toISOString()
      },
      {
        type: 'Usage',
        amount: -15,
        description: 'Agent execution - Email Assistant',
        timestamp: new Date(Date.now() - 7200000).toISOString()
      },
      {
        type: 'Refill',
        amount: 1000,
        description: 'Initial credit package',
        timestamp: new Date(Date.now() - 86400000).toISOString()
      },
      {
        type: 'Usage',
        amount: -50,
        description: 'Automation workflow execution',
        timestamp: new Date(Date.now() - 172800000).toISOString()
      }
    ];

    return NextResponse.json({
      credits: mockCredits,
      transactions: mockTransactions
    });
  } catch (error) {
    console.error('Credits history error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch credits history' },
      { status: 500 }
    );
  }
}
