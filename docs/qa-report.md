# QA report

QA pass completed on 14 August 2026 against the assignment checklist. This report separates verified behavior from work that requires live credentials or public access.

## Automated checks passed

- Production frontend build
- Frontend lint and accessibility rules
- Server-render smoke tests
- No starter/loading placeholder metadata in production HTML
- No Hunar or Apollo secret patterns in source or generated frontend files
- Python source compilation
- Eight backend tests covering demo-provider labelling, Hunar HMAC verification, timestamp replay rejection, modified-body rejection, retry-safe webhook idempotency, E.164 validation, and the complete HTTP demo workflow
- API integration coverage for health, role validation, repeated people search, duplicate prevention, shortlist updates, missing-candidate rejection, demo campaign creation, call polling, recruiter review, unsigned-webhook rejection, and canonical webhook retries
- API health and database initialization from an empty SQLite database

## Security checks passed

- `.env` is ignored; `.env.example` contains placeholders only.
- Git history does not contain the supplied Hunar live-key prefix.
- Provider credentials are referenced only in Python server configuration.
- Hunar requests are issued only by the backend adapter.
- Webhooks verify the raw request body before JSON parsing and reject timestamps outside the five-minute replay window.
- Idempotency uses canonical event JSON, so a retry with a fresh timestamp/signature cannot double-process an identical event.
- Live campaigns pre-validate every selected candidate before any outbound request, preventing malformed or missing numbers from creating a partial campaign.

## User-flow checks passed

- Role title, location, and job description show readable inline validation for empty/short values and enforce maximum lengths.
- Talent search has a disabled/loading button and prevents double submission during the simulated request.
- Shortlist singular/plural copy is correct and the avatar stack reflects the actual selected people.
- Opening a talent result now preserves that exact candidate through candidate review and page refresh; review content no longer falls back to Ananya for every result.
- Every demo person, call, and transcript is explicitly labelled.
- Missing contact data is safe: demo candidates never expose or call a fake real number, and live mode requires an authorized E.164 number.
- Voice simulation displays the documented sequence `NOT_STARTED → INITIATED → RINGING → IN_PROGRESS → COMPLETED`.
- Campaign timers are cleared on unmount.
- Shortlist and campaign state survive refresh through device-local demo persistence.
- Hash routes restore Overview, Roles, Talent Search, Campaigns, Candidate Review, and Attendance Blueprint directly; browser back/forward updates the visible screen.
- Candidate A and B retain separate call records keyed by `candidate_id`, `request_id`, and unique `provider_call_id`; out-of-order webhook updates query by provider call ID.
- Backend search pagination accepts `page` and `per_page` and forwards both to Apollo.
- Duplicate candidates are prevented by provider/external-ID and role/candidate uniqueness constraints.
- The API polling fallback (`GET /api/calls/{id}`) refreshes and persists status/results when callbacks are delayed.
- The built production bundle was exercised at 375 px, 768 px, and 1440 px widths. Mobile navigation opens/closes correctly and no tested page produced horizontal overflow.
- Campaign launch cancellation, launch, completion, refresh persistence, attendance tabs, and browser back/forward routing passed in the interactive browser run.
- The final rebuilt bundle produced no browser console warnings or errors.

## Deliberately not applicable

- **Agent-management UI:** intentionally out of scope. RecruitOS selects a preconfigured active Hunar agent using `HUNAR_AGENT_ID`; it does not expose partial agent updates, persona editing, retry configuration, or guardrail editing. This avoids sending invalid partial Hunar objects.
- **Large-list virtualization:** the submission limits each people-search page to at most 100 results and the demo renders four. Server-side pagination exists; virtualization is unnecessary at this scope.
- **Transcript from live Hunar response:** Hunar's current external call schema does not document a transcript field. Live mode does not invent one.

## Requires final live authorization

- A call to an explicitly authorized real phone number
- Real lifecycle/webhook observation using the short-lived Hunar key
- Apollo search using a credential with People API Search access
- Public/incognito access test (the current deployment is owner-only)
- Production backend environment values and a public HTTPS webhook URL
- A complete Chrome plus one independent-browser matrix (the interactive pass used Chromium-based browser surfaces, not a full engine matrix)
- Lighthouse/PageSpeed against the final public URL

These items must not be marked complete until actually run. No real person has been called during QA.

## Remaining product limitations

- The public frontend is a resilient reviewer demo and does not currently fetch the separately deployable FastAPI backend. The repository contains the real backend and provider adapters, but a final production backend deployment is required for live API operation.
- Authentication and organization permissions are outside the three-day scope and must be added before handling real candidate data.
- Demo persistence uses browser storage only. Live workflow state is stored in the backend database.
