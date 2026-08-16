import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const apiKey = process.env.HUNAR_API_KEY;
  const agentId = process.env.HUNAR_AGENT_ID;
  const baseUrl = (process.env.HUNAR_BASE_URL ?? "https://api.voice.hunar.ai/external/v1").replace(/\/$/, "");

  if (!apiKey || !agentId) {
    return NextResponse.json(
      { connected: false, message: "Hunar credentials are not configured" },
      { status: 503, headers: { "Cache-Control": "no-store" } },
    );
  }

  try {
    const response = await fetch(`${baseUrl}/agents/${agentId}/`, {
      headers: { "X-API-Key": apiKey, Accept: "application/json" },
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        { connected: false, message: "Hunar rejected the configured agent" },
        { status: 502, headers: { "Cache-Control": "no-store" } },
      );
    }

    const agent = await response.json() as { id?: string; name?: string; status?: string; agent_code?: string };
    return NextResponse.json(
      {
        connected: true,
        agent: {
          id: agent.id,
          name: agent.name,
          status: agent.status,
          code: agent.agent_code,
        },
        verifiedAt: new Date().toISOString(),
      },
      { headers: { "Cache-Control": "no-store" } },
    );
  } catch {
    return NextResponse.json(
      { connected: false, message: "Hunar is temporarily unreachable" },
      { status: 502, headers: { "Cache-Control": "no-store" } },
    );
  }
}
