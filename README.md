# Hunar RecruitOS

Hunar RecruitOS is a focused recruiting workspace for the Hunar.ai take-home assignment. A recruiter can define a role, discover candidates, shortlist the strongest matches, launch a Hunar Voice workflow, and review structured hiring signals without leaving one product.

**Live demo:** https://hunar-recruitos-vardan.vardanredmi.chatgpt.site

The deployed frontend is deliberately resilient: **Demo mode** exercises the complete reviewer journey without calling real people. A server-only health endpoint verifies the supplied Hunar credential and active candidate-screening agent at runtime; demo candidates, calls, transcripts, and results remain visibly labelled.

## Core journey

```mermaid
flowchart LR
  A[Role brief] --> B[Candidate discovery]
  B --> C[Transparent shortlist]
  C --> D[Hunar Voice campaign]
  D --> E[Signed result callback]
  E --> F[Structured human review]
```

## Assignment coverage

- **AI Hiring Assistant:** role setup, structured screening questions, campaigns, status tracking, conversation results, and recruiter override.
- **People Search & Reachout:** one real Apollo adapter plus a contract-compatible demo adapter, editable filters, match reasons, and shortlisting.
- **Attendance Without Smartphones:** an interactive blueprint covering shared terminals, IVR fallback, site verification, offline sync, fraud controls, reconciliation, privacy, and rollout.

## Technology

- Next.js-compatible React frontend written in TypeScript, styled with Tailwind CSS
- Python FastAPI backend
- SQLAlchemy data model; SQLite for zero-friction demo development and PostgreSQL through `DATABASE_URL`
- `httpx` provider adapters for Hunar Voice and Apollo
- Signed webhook verification using Hunar's documented HMAC-SHA256 scheme
- Deployed server-only Hunar agent verification at `/api/hunar/status`; credentials never reach browser code
- Focused pytest coverage around signatures and demo-provider safety

## Repository map

```text
app/                 Recruiter-facing Next.js application
backend/app/         FastAPI API, data model, and provider adapters
backend/tests/       Focused backend tests
docs/                API contracts, architecture, attendance design, and demo script
.env.example         Safe configuration template—placeholders only
docker-compose.yml   Local API and PostgreSQL setup
```

The frontend remains at the repository root because the bundled Sites deployment runtime expects the Next.js application there; the Python service is isolated in `backend/`.

## Local setup

### Frontend

```bash
corepack enable
pnpm install
pnpm run dev
```

Open `http://localhost:3000`.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for the generated API reference.

### Docker

```bash
docker compose up --build
```

## Configuration

Copy `.env.example` to `.env` and set only the credentials needed for live testing.

| Variable | Purpose |
| --- | --- |
| `DEMO_MODE` | Keeps all people and voice workflows simulated when `true` |
| `DATABASE_URL` | SQLite locally or PostgreSQL in deployment |
| `FRONTEND_URL` | Exact permitted browser origin |
| `PUBLIC_API_URL` | Public HTTPS backend URL used in Hunar callback configuration |
| `HUNAR_API_KEY` | Server-only Hunar credential and webhook-signing secret |
| `HUNAR_AGENT_ID` | Active Hunar agent used for authorized live calls |
| `APOLLO_API_KEY` | Server-only Apollo credential |

Never prefix these server-only variables with `NEXT_PUBLIC_`.

## Live vs. demo mode

Demo mode is the default and supports the full submission walkthrough. It never initiates telephony or represents simulated records as live.

Live mode requires:

1. `DEMO_MODE=false`
2. Hunar and Apollo credentials configured only on the backend
3. An active `HUNAR_AGENT_ID`
4. A public HTTPS callback URL
5. An explicitly authorized test number and `authorized_live_call=true`

Apollo People API Search does not return email addresses or phone numbers. Those require Apollo enrichment endpoints and credits, so the search adapter does not fabricate contact data.

## Security decisions

- Secrets are server-side environment values and excluded from Git.
- Hunar callbacks are verified against the raw request body using `X-Hunar-Timestamp` and `X-Hunar-Signature` with a five-minute replay window.
- Callback fingerprints make processing idempotent.
- Raw provider results are retained separately from normalized fields.
- Provider-generated results, application recommendations, and recruiter decisions remain separately attributed.
- Live calls are locked unless explicitly authorized.
- Logs should contain IDs and event types, not phone numbers, transcripts, or credentials.

## Verification

```bash
# frontend
pnpm run build
pnpm run lint

# backend
cd backend
pytest
python -m compileall app
```

## Documentation

- [Architecture](docs/architecture.md)
- [Verified API contracts](docs/api-contracts.md)
- [Attendance proposal](docs/attendance-proposal.md)
- [Three-to-five-minute demo](docs/demo-script.md)
- [QA report](docs/qa-report.md)
- [Submission email draft](docs/submission-email.md)

## Known limitations

- Authentication and multi-tenancy are intentionally out of scope for this three-day assignment.
- The public frontend uses demo state so it stays reviewable after trial keys expire.
- Hunar's documented call detail payload exposes structured `result` data and recording metadata, but its external documentation does not currently document a transcript field. The application therefore never claims a demo transcript came from a live response.
- Apollo enrichment is not performed by default; a candidate needs an authorized phone number before live reachout.

## Production next steps

Add recruiter authentication, encrypt sensitive candidate fields, move webhook processing to a durable queue, add Apollo enrichment with consent controls, configure retention policies for recordings/transcripts, and complete a privacy and bias review before real hiring use.
