// src/app/api/user/automations/route.ts
// DEPRECATED: This endpoint is deprecated. Use /api/automation/simple or /api/automation/advanced instead.

import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  return NextResponse.json({
    deprecated: true,
    message: 'This API is deprecated. Use /api/automation/simple or /api/automation/advanced instead.',
    migration_notice: 'User automation management has been integrated into the main automation system',
    user_guidance: 'Use the automation UI at /automation/simple or /automation/advanced for creating and managing automations.',
    suggested_endpoints: {
      simple: '/api/automation/simple',
      advanced: '/api/automation/advanced',
      ui: '/automation'
    }
  }, { status: 410 });
}

export async function POST(req: NextRequest) {
  return NextResponse.json({
    deprecated: true,
    message: 'This API is deprecated. Use /api/automation/simple or /api/automation/advanced instead.',
    migration_notice: 'User automation creation has been integrated into the main automation system',
    user_guidance: 'Use the automation UI at /automation/simple or /automation/advanced for creating automations.',
    suggested_endpoints: {
      simple: '/api/automation/simple',
      advanced: '/api/automation/advanced',
      ui: '/automation'
    }
  }, { status: 410 });
}
