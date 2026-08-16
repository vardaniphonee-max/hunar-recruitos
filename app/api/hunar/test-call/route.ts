import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const E164 = /^\+[1-9]\d{7,14}$/;

function response(body: object, status = 200) {
  return NextResponse.json(body, { status, headers: { "Cache-Control": "no-store" } });
}

function authorized(request: NextRequest) {
  const expected = process.env.HUNAR_TEST_CALL_TOKEN;
  return process.env.HUNAR_TEST_CALL_ENABLED === "true"
    && Boolean(expected && expected.length >= 32)
    && request.headers.get("authorization") === `Bearer ${expected}`;
}

function configuration() {
  return {
    apiKey: process.env.HUNAR_API_KEY,
    agentId: process.env.HUNAR_AGENT_ID,
    baseUrl: (process.env.HUNAR_BASE_URL ?? "https://api.voice.hunar.ai/external/v1").replace(/\/$/, ""),
  };
}

function sanitizedCall(payload: Record<string, unknown>) {
  return {
    id: payload.id,
    requestId: payload.request_id,
    status: payload.status,
    lifecycleStatus: payload.lifecycle_status,
    durationSeconds: payload.duration_seconds,
    result: payload.result,
  };
}

export async function POST(request: NextRequest) {
  if (!authorized(request)) return response({ message: "Test calling is disabled" }, 404);

  const { apiKey, agentId, baseUrl } = configuration();
  if (!apiKey || !agentId) return response({ message: "Hunar is not configured" }, 503);

  let body: { mobileNumber?: string; consented?: boolean };
  try {
    body = await request.json() as { mobileNumber?: string; consented?: boolean };
  } catch {
    return response({ message: "Malformed request" }, 400);
  }
  if (body.consented !== true || !body.mobileNumber || !E164.test(body.mobileNumber)) {
    return response({ message: "Explicit consent and a valid E.164 number are required" }, 422);
  }

  const providerResponse = await fetch(`${baseUrl}/calls/`, {
    method: "POST",
    headers: { "X-API-Key": apiKey, "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      agent_id: agentId,
      callee_name: "Vardan Malik",
      mobile_number: body.mobileNumber,
      request_id: `recruitos-consented-${crypto.randomUUID().slice(0, 8)}`,
      timezone: "Asia/Kolkata",
      retry_config: { max_retry_count: 0, retry_interval_hours: 0 },
      custom_data: {
        company_name: "Hunar RecruitOS Demo",
        job_title: "Customer Success Manager",
        job_role: "Customer Success Manager",
        job_location: "Bengaluru, India",
        location: "Bengaluru, India",
        required_skills: "B2B SaaS, enterprise accounts, retention",
        experience_range: "5-8 years",
        job_summary: "Own enterprise customer onboarding, adoption, retention, and measurable customer outcomes.",
        interview_questions: "1. Describe the largest enterprise portfolio you managed. 2. How do you handle churn risk? 3. What is your notice period?",
      },
    }),
    cache: "no-store",
    signal: AbortSignal.timeout(20_000),
  });
  if (!providerResponse.ok) return response({ message: "Hunar rejected the authorized test call" }, 502);

  return response(sanitizedCall(await providerResponse.json() as Record<string, unknown>), 201);
}

export async function GET(request: NextRequest) {
  if (!authorized(request)) return response({ message: "Test calling is disabled" }, 404);

  const { apiKey, baseUrl } = configuration();
  const callId = request.nextUrl.searchParams.get("call_id");
  if (!apiKey || !callId || !/^[a-zA-Z0-9-]{1,80}$/.test(callId)) {
    return response({ message: "A valid call ID is required" }, 422);
  }
  const providerResponse = await fetch(`${baseUrl}/calls/${encodeURIComponent(callId)}/`, {
    headers: { "X-API-Key": apiKey, Accept: "application/json" },
    cache: "no-store",
    signal: AbortSignal.timeout(15_000),
  });
  if (!providerResponse.ok) return response({ message: "Hunar call status is unavailable" }, 502);
  return response(sanitizedCall(await providerResponse.json() as Record<string, unknown>));
}
