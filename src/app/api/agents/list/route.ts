// app/api/agents/list/route.ts

import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  try {
    // Pull token from headers or cookies
    const token = req.cookies.get("session_token")?.value;

    if (!token) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Call FastAPI backend
    const fastapiRes = await fetch(`${process.env.FASTAPI_URL}/agents/list`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    });

    const data = await fastapiRes.json();
    return NextResponse.json(data);
  } catch (err) {
    console.error("Error fetching agents:", err);
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}
